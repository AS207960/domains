from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
# from dateutil import relativedelta
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
import datetime
import grpc
import decimal
from domains import models, zone_info, apps
from domains.views import billing

NOTIFY_INTERVAL = datetime.timedelta(days=7)
RENEW_INTERVAL = datetime.timedelta(days=5)
FAIL_INTERVAL = datetime.timedelta(days=1)


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


class Command(BaseCommand):
    help = 'Automatically renews all eligible domains'

    def handle(self, *args, **options):
        now = timezone.now()
        domains = models.DomainRegistration.objects.filter(pending=False, deleted=False)

        notifications = {}

        for domain in domains:
            domain_info = zone_info.get_domain_info(domain.domain)[0]  # type: zone_info.DomainInfo

            if not domain_info:
                print(f"Can't renew {domain.domain}: unknown zone")
                continue

            try:
                domain_data = apps.epp_client.get_domain(domain.domain)
            except grpc.RpcError as rpc_error:
                print(f"Can't get data for {domain.domain}: {rpc_error.details()}")
                continue

            user = domain.get_user()

            if (domain_data.expiry_date - RENEW_INTERVAL) >= now:
                renewal_period = domain_info.pricing.periods[0]

                try:
                    renewal_price = domain_info.pricing.renewal(unit=renewal_period.unit, value=renewal_period.value)
                except grpc.RpcError as rpc_error:
                    print(f"Can't get renewal price for {domain.domain}: {rpc_error.details()}")
                    continue

                if not renewal_price:
                    print(f"No renewal price available for {domain.domain}")
                    continue

                print(f"{domain_data.name} expiring soon, renewing for {renewal_price}")
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
                else:
                    print(f"Failed to charge for {domain_data.name} renewal: {charge_state.error}")
                    if (domain_data.expiry_date - FAIL_INTERVAL) >= now:
                        print(f"Deleting {domain.domain} due to billing failure")
                        try:
                            apps.epp_client.delete_domain(domain_data.name)
                        except grpc.RpcError as rpc_error:
                            print(f"Failed to delete {domain.domain}: {rpc_error.details()}")
                            billing.charge_account(
                                user.username, renewal_price, f"{domain.domain} automatic renewal",
                                f"dm_auto_renew_{domain.id}", can_reject=False
                            )
                            continue
                        print(f"Deleted {domain.domain}")

            elif (domain_data.expiry_date - NOTIFY_INTERVAL) >= now:
                if domain.last_renew_notify + NOTIFY_INTERVAL > now:
                    continue

                print(f"{domain_data.name} expiring soon, notifying owner")
                if user not in notifications:
                    notifications[user] = [{
                        "obj": domain,
                        "domain": domain_data
                    }]
                else:
                    notifications[user].append({
                        "obj": domain,
                        "domain": domain_data
                    })
