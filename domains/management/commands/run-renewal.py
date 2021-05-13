from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import reverse
from django.conf import settings
from django.utils import timezone
import datetime
import grpc
from domains import models, zone_info, apps, tasks
from domains.views import billing, emails

NOTIFY_INTERVAL = datetime.timedelta(days=15)
RENEW_INTERVAL = datetime.timedelta(days=7)
FAIL_INTERVAL = datetime.timedelta(days=1)


def mail_upcoming(user, domains):
    context = {
        "name": user.first_name,
        "domains": domains,
        "subject": "Upcoming domain renewals"
    }
    html_content = render_to_string("domains_email/renewal_upcoming.html", context)
    txt_content = render_to_string("domains_email/renewal_upcoming.txt", context)

    email = EmailMultiAlternatives(
        subject='Upcoming domain renewals',
        body=txt_content,
        to=[user.email],
        bcc=['email-log@as207960.net'],
        reply_to=['Glauca Support <hello@glauca.digital>']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def mail_deleted(user, domains):
    context = {
        "name": user.first_name,
        "domains": domains,
        "subject": "Domain renewal failed - domains deleted"
    }
    html_content = render_to_string("domains_email/renewal_deleted.html", context)
    txt_content = render_to_string("domains_email/renewal_deleted.txt", context)

    email = EmailMultiAlternatives(
        subject='Domain renewal failed - domains deleted',
        body=txt_content,
        to=[user.email],
        bcc=['email-log@as207960.net'],
        reply_to=['Glauca Support <hello@glauca.digital>']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


class Command(BaseCommand):
    help = 'Automatically renews all eligible domains'

    def handle(self, *args, **options):
        now = timezone.now()
        domains = models.DomainRegistration.objects.filter(deleted=False, former_domain=False)
        deleted_domains = models.DomainRegistration.objects.filter(deleted=True, former_domain=False)

        notifications = {}
        deleted = {}

        def insert_into_dict(d, key, value):
            if key not in d:
                d[key] = [value]
            else:
                d[key].append(value)

        for domain in domains:
            domain_info, sld = zone_info.get_domain_info(domain.domain)

            if not domain_info:
                print(f"Can't renew {domain.domain}: unknown zone")
                continue

            try:
                domain_data = apps.epp_client.get_domain(domain.domain)
            except grpc.RpcError as rpc_error:
                print(f"Can't get data for {domain.domain}: {rpc_error.details()}")
                continue

            user = domain.get_user()

            expiry_date = domain_data.expiry_date.replace(tzinfo=datetime.timezone.utc)
            email_data = {
                "obj": domain,
                "domain": domain_data,
                "expiry_date": expiry_date
            }
            print(f"{domain_data.name} expiring on {expiry_date}")

            if (expiry_date - FAIL_INTERVAL) <= now:
                if (domain.last_billed + RENEW_INTERVAL) > now:
                    continue

            if (expiry_date - RENEW_INTERVAL) <= now:
                renewal_period = domain_info.pricing.periods[0]

                try:
                    renewal_price = domain_info.pricing.renewal(
                        country=None, username=user.username, sld=sld,
                        unit=renewal_period.unit, value=renewal_period.value
                    ).amount
                except grpc.RpcError as rpc_error:
                    print(f"Can't get renewal price for {domain.domain}: {rpc_error.details()}")
                    continue

                if not renewal_price:
                    print(f"No renewal price available for {domain.domain}")
                    continue

                if (expiry_date - FAIL_INTERVAL) <= now:
                    print(f"Deleting {domain.domain} due to billing failure")
                    try:
                        apps.epp_client.delete_domain(domain_data.name)
                    except grpc.RpcError as rpc_error:
                        print(f"Failed to delete {domain.domain}: {rpc_error.details()}")
                        billing.charge_account(
                            user.username, renewal_price, f"{domain.unicode_domain} automatic renewal",
                            f"dm_auto_renew_{domain.id}", can_reject=False
                        )
                        continue
                    domain.former_domain = True
                    domain.save()
                    print(f"Deleted {domain.domain}")
                    insert_into_dict(deleted, user, email_data)
                    renew_order = models.DomainAutomaticRenewOrder.objects.filter(domain_obj=domain).order_by("-timestamp").first()
                    if renew_order:
                        billing.reverse_charge(renew_order.id)

                else:
                    if (domain.last_billed + RENEW_INTERVAL) > now:
                        continue

                    print(f"{domain_data.name} expiring soon, renewing for {renewal_price:.2f} GBP")
                    order = models.DomainAutomaticRenewOrder(
                        domain=domain.domain,
                        domain_obj=domain,
                        period_unit=renewal_period.unit,
                        period_value=renewal_period.value,
                        price=renewal_price,
                        off_session=True,
                    )
                    order.save()
                    tasks.charge_order(
                        order=order,
                        username=user.username,
                        descriptor=f"{domain.unicode_domain} automatic renewal",
                        charge_id=order.id,
                        return_uri=None,
                        success_func=None,
                        notif_queue="domains_auto_renew_billing_notif"
                    )
                    domain.last_billed = now
                    domain.save()
                    if order.state == order.STATE_NEEDS_PAYMENT:
                        emails.mail_auto_renew_redirect.delay(order.id)
                    elif order.state == order.STATE_FAILED:
                        emails.mail_auto_renew_failed.delay(order.id)

            elif (expiry_date - NOTIFY_INTERVAL) <= now:
                if domain.last_renew_notify + NOTIFY_INTERVAL > now:
                    continue

                print(f"{domain_data.name} expiring soon, notifying owner")
                insert_into_dict(notifications, user, email_data)
            else:
                print(f"Not doing anything with {domain_data.name}")

        for user, domains in notifications.items():
            mail_upcoming(user, domains)
            for domain in domains:
                domain["obj"].last_renew_notify = now
                domain["obj"].save()

        for user, domains in deleted.items():
            mail_deleted(user, domains)

        for domain in deleted_domains:
            domain_info, sld = zone_info.get_domain_info(domain.domain)

            if not domain_info:
                print(f"Can't check RGP on {domain.domain}: unknown zone")
                continue

            if domain.deleted_date and domain_info.redemption_period:
                if domain.deleted_date + domain_info.redemption_period <= now:
                    domain.former_domain = True
                    domain.save()
