from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
import datetime
import grpc
from domains import models, zone_info, apps
from domains.views import billing

NOTIFY_INTERVAL = datetime.timedelta(days=15)
RENEW_INTERVAL = datetime.timedelta(days=5)
FAIL_INTERVAL = datetime.timedelta(days=1)


def mail_success(user, domains):
    context = {
        "name": user.first_name,
        "domains": domains
    }
    html_content = render_to_string("domains_email/renewal_success.html", context)
    txt_content = render_to_string("domains_email/renewal_success.txt", context)

    email = EmailMultiAlternatives(
        subject='Domain renewal successful',
        body=txt_content,
        to=[user.email],
        bcc=['q@as207960.net']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def mail_upcoming(user, domains):
    context = {
        "name": user.first_name,
        "domains": domains
    }
    html_content = render_to_string("domains_email/renewal_upcoming.html", context)
    txt_content = render_to_string("domains_email/renewal_upcoming.txt", context)

    email = EmailMultiAlternatives(
        subject='Upcoming domain renewals',
        body=txt_content,
        to=[user.email],
        bcc=['q@as207960.net']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def mail_failed(user, domains):
    context = {
        "name": user.first_name,
        "domains": domains
    }
    html_content = render_to_string("domains_email/renewal_failed.html", context)
    txt_content = render_to_string("domains_email/renewal_failed.txt", context)

    email = EmailMultiAlternatives(
        subject='Domain renewal failed',
        body=txt_content,
        to=[user.email],
        bcc=['q@as207960.net']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def mail_deleted(user, domains):
    context = {
        "name": user.first_name,
        "domains": domains
    }
    html_content = render_to_string("domains_email/renewal_deleted.html", context)
    txt_content = render_to_string("domains_email/renewal_deleted.txt", context)

    email = EmailMultiAlternatives(
        subject='Domain renewal failed - domains deleted',
        body=txt_content,
        to=[user.email],
        bcc=['q@as207960.net']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


class Command(BaseCommand):
    help = 'Automatically renews all eligible domains'

    def handle(self, *args, **options):
        now = timezone.now()
        domains = models.DomainRegistration.objects.filter(pending=False, deleted=False)

        notifications = {}
        renewed = {}
        failed = {}
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

            if (expiry_date - RENEW_INTERVAL) <= now:
                if (domain.last_billed + RENEW_INTERVAL) > now:
                    continue

                renewal_period = domain_info.pricing.periods[0]

                try:
                    renewal_price = domain_info.pricing.renewal(
                        sld, unit=renewal_period.unit, value=renewal_period.value
                    )
                except grpc.RpcError as rpc_error:
                    print(f"Can't get renewal price for {domain.domain}: {rpc_error.details()}")
                    continue

                if not renewal_price:
                    print(f"No renewal price available for {domain.domain}")
                    continue

                print(f"{domain_data.name} expiring soon, renewing for {renewal_price:.2f} GBP")
                charge_state = billing.charge_account(
                    user.username, renewal_price, f"{domain.domain} automatic renewal", f"dm_auto_renew_{domain.id}"
                )

                if charge_state.success:
                    domain.last_billed = now
                    domain.save()
                    if domain_info.renew_supported:
                        try:
                            apps.epp_client.renew_domain(domain_data.name, renewal_period, domain_data.expiry_date)
                        except grpc.RpcError as rpc_error:
                            print(f"Failed to renew {domain.domain}: {rpc_error.details()}")
                            billing.reverse_charge(f"dm_auto_renew_{domain.id}")
                            continue
                    print(f"{domain_data.name} renewed")
                    insert_into_dict(renewed, user, email_data)
                else:
                    print(f"Failed to charge for {domain_data.name} renewal: {charge_state.error}")
                    if (expiry_date - FAIL_INTERVAL) >= now:
                        print(f"Deleting {domain.domain} due to billing failure")
                        # try:
                        #     apps.epp_client.delete_domain(domain_data.name)
                        # except grpc.RpcError as rpc_error:
                        #     print(f"Failed to delete {domain.domain}: {rpc_error.details()}")
                        #     billing.charge_account(
                        #         user.username, renewal_price, f"{domain.domain} automatic renewal",
                        #         f"dm_auto_renew_{domain.id}", can_reject=False
                        #     )
                        #     continue
                        # domain.delete()
                        print(f"Deleted {domain.domain}")
                        insert_into_dict(deleted, user, email_data)
                    else:
                        insert_into_dict(failed, user, email_data)

            elif (expiry_date - NOTIFY_INTERVAL) <= now:
                if domain.last_renew_notify + NOTIFY_INTERVAL > now:
                    continue

                print(f"{domain_data.name} expiring soon, notifying owner")
                insert_into_dict(notifications, user, email_data)
            else:
                print(f"Not doing anything with {domain_data.name}")

        for user, domains in notifications.items():
            mail_upcoming(user, domains)

        for user, domains in renewed.items():
            mail_success(user, domains)

        for user, domains in failed.items():
            mail_failed(user, domains)

        for user, domains in deleted.items():
            mail_deleted(user, domains)
