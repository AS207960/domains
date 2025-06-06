from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
import datetime
import grpc
from domains import models, zone_info, apps, tasks, utils
from domains.views import billing, emails

FAIL_INTERVAL = datetime.timedelta(days=3)


class Command(BaseCommand):
    help = 'Automatically renews all eligible domains'

    def handle(self, *args, **options):
        now = timezone.now()
        domains = models.DomainRegistration.objects.filter(deleted=False, former_domain=False)
        deleted_domains = models.DomainRegistration.objects.filter(deleted=True, former_domain=False)

        notifications = {}
        deleted = {}
        expired = {}

        def insert_into_dict(d, key, value):
            if key not in d:
                d[key] = [value]
            else:
                d[key].append(value)

        for domain in domains:
            domain_info, sld = zone_info.get_domain_info(domain.domain, registry_id=domain.registry_id) # type: zone_info.DomainInfo, str

            if not domain_info:
                print(f"Can't renew {domain.domain}: unknown zone", flush=True)
                continue

            try:
                domain_available, _, _ = apps.epp_client.check_domain(
                    domain.domain, registry_id=domain.registry_id
                )
            except grpc.RpcError as rpc_error:
                print(f"Can't get data for {domain.domain}: {rpc_error.details()}", flush=True)
                continue

            if domain_available:
                print(f"{domain.domain} is available for registration, marking as deleted", flush=True)
                domain.former_domain = True
                domain.save()
                continue

            if domain.not_required:
                print(f"{domain.domain} is not required, skipping", flush=True)
                continue

            try:
                domain_data = apps.epp_client.get_domain(
                    domain.domain, registry_id=domain.registry_id
                )
            except grpc.RpcError as rpc_error:
                print(f"Can't get data for {domain.domain}: {rpc_error.details()}", flush=True)
                continue

            if apps.epp_api.domain_common_pb2.PendingDelete in domain_data.statuses or \
               apps.epp_api.rgp_pb2.RedemptionPeriod in domain_data.rgp_state or \
               apps.epp_api.rgp_pb2.PendingDelete in domain_data.rgp_state:
                print(f"{domain_data.name} is already pending delete, not touching", flush=True)
                continue

            if not (domain_data.expiry_date or domain_data.paid_until_date):
                print(f"{domain_data.name} has no expiry date, not touching", flush=True)
                continue

            user = domain.get_user()

            expiry_date, _ = utils.domain_paid_until_date(domain, domain_data, domain_info)

            email_data = {
                "obj": domain,
                "domain": domain_data,
                "expiry_date": expiry_date
            }
            print(f"{domain_data.name} expiring on {expiry_date}", flush=True)

            if (expiry_date - utils.RENEW_INTERVAL) <= now:
                print(f"{domain_data.name} expiring soon, renewing", flush=True)

                last_renew_order = models.DomainAutomaticRenewOrder.objects.filter(domain_obj=domain) \
                    .order_by("-timestamp").first()  # type: models.DomainAutomaticRenewOrder
                if last_renew_order and last_renew_order.state == last_renew_order.STATE_COMPLETED and \
                        last_renew_order.timestamp + utils.NOTIFY_INTERVAL >= now:
                    print(f"{domain_data.name} expiring soon, renewal already succeeded", flush=True)
                    continue
                last_renew_order = models.DomainRenewOrder.objects.filter(domain_obj=domain) \
                    .order_by("-timestamp").first()  # type: models.DomainRenewOrder
                if last_renew_order and last_renew_order.state == last_renew_order.STATE_COMPLETED and \
                        last_renew_order.timestamp + utils.NOTIFY_INTERVAL >= now:
                    print(f"{domain_data.name} expiring soon, renewal already succeeded", flush=True)
                    continue
                last_restore_order = models.DomainRestoreOrder.objects.filter(domain_obj=domain, should_renew=True) \
                    .order_by("-timestamp").first()  # type: models.DomainRestoreOrder
                if last_restore_order and last_restore_order.state == last_restore_order.STATE_COMPLETED and \
                        last_restore_order.timestamp + utils.NOTIFY_INTERVAL >= now:
                    print(f"{domain_data.name} expiring soon, renewal (by restore) already succeeded", flush=True)
                    continue

                renewal_period = domain_info.pricing.periods[0]

                try:
                    renewal_price = domain_info.pricing.renewal(
                        country=None, username=user.username, sld=sld,
                        unit=renewal_period.unit, value=renewal_period.value
                    ).amount
                except grpc.RpcError as rpc_error:
                    print(f"Can't get renewal price for {domain.domain}: {rpc_error.details()}", flush=True)
                    continue

                if not renewal_price:
                    print(f"No renewal price available for {domain.domain}", flush=True)
                    continue

                if (expiry_date - FAIL_INTERVAL) <= now:
                    if domain_info.renews_if_not_deleted:
                        print(f"Deleting {domain.domain} due to billing failure", flush=True)
                        if last_renew_order and last_renew_order.timestamp + utils.NOTIFY_INTERVAL >= now:
                            print(f"Reversing charge just to be sure", flush=True)
                            billing.reverse_charge(last_renew_order.id)

                        try:
                            if domain_info.keysys_de:
                                apps.epp_client.delete_domain(
                                    domain.domain, keysys_target="TRANSIT",
                                    registry_id=domain.registry_id
                                )
                            else:
                                apps.epp_client.delete_domain(
                                    domain_data.name,
                                    registry_id=domain.registry_id
                                )
                        except grpc.RpcError as rpc_error:
                            print(f"Failed to delete {domain.domain}: {rpc_error.details()}", flush=True)
                            billing.charge_account(
                                user.username, renewal_price, f"{domain.unicode_domain} automatic renewal",
                                f"dm_auto_renew_{domain.id}", can_reject=False
                            )
                            continue

                        if not domain_info.restore_supported:
                            domain.former_domain = True
                        else:
                            domain.deleted = True
                            domain.deleted_date = now
                        domain.save()
                        print(f"Deleted {domain.domain}", flush=True)
                        insert_into_dict(deleted, user, email_data)
                    else:
                        print(f"{domain.domain} expired, sending reminder", flush=True)
                        insert_into_dict(expired, user, email_data)

                else:
                    if (domain.last_billed + utils.RENEW_INTERVAL) >= now:
                        print(f"{domain_data.name} expiring soon, renewal already charged", flush=True)
                        continue

                    print(f"{domain_data.name} expiring soon, renewing for {renewal_price:.2f} GBP", flush=True)
                    order = models.DomainAutomaticRenewOrder(
                        domain=domain.domain,
                        domain_obj=domain,
                        period_unit=renewal_period.unit,
                        period_value=renewal_period.value,
                        price=renewal_price,
                        off_session=True,
                        user=user,
                    )
                    order.save()
                    tasks.charge_order(
                        order=order,
                        username=user.username,
                        descriptor=f"{domain.unicode_domain} automatic renewal",
                        charge_id=order.id,
                        return_uri=None,
                        success_func=tasks.process_domain_auto_renew_paid,
                        notif_queue="domains_auto_renew_billing_notif"
                    )
                    domain.last_billed = now
                    domain.save()
                    if order.state == order.STATE_NEEDS_PAYMENT and order.redirect_uri:
                        emails.mail_auto_renew_redirect.delay(order.id)
                    elif order.state == order.STATE_FAILED:
                        emails.mail_auto_renew_failed.delay(order.id)

            elif (expiry_date - utils.NOTIFY_INTERVAL) <= now:
                if domain.last_renew_notify + utils.NOTIFY_INTERVAL > now:
                    print(f"{domain_data.name} expiring soon, already notified", flush=True)
                    continue

                print(f"{domain_data.name} expiring soon, notifying owner", flush=True)
                insert_into_dict(notifications, user, email_data)
            else:
                print(f"Not doing anything with {domain_data.name}", flush=True)

        for user, domains in notifications.items():
            emails.send_email(user, {
                "subject": "Upcoming domain renewals",
                "content": render_to_string("domains_email/renewal_upcoming.html", {
                    "domains": domains,
                })
            })

            for domain in domains:
                domain["obj"].last_renew_notify = now
                domain["obj"].save()

        for user, domains in deleted.items():
            emails.send_email(user, {
                "subject": "Domain renewal failed - domains deleted",
                "content": render_to_string("domains_email/renewal_deleted.html", {
                    "domains": domains,
                })
            })

        for user, domains in expired.items():
            emails.send_email(user, {
                "subject": "Your domain has expired",
                "content": render_to_string("domains_email/renewal_expired.html", {
                    "domains": domains,
                })
            })

        for domain in deleted_domains:
            domain_info, sld = zone_info.get_domain_info(domain.domain, registry_id=domain.registry_id)

            if not domain_info:
                print(f"Can't check RGP on {domain.domain}: unknown zone", flush=True)
                continue

            if domain.deleted_date and domain_info.redemption_period:
                if domain.deleted_date + domain_info.redemption_period <= now:
                    domain.former_domain = True
                    domain.save()
