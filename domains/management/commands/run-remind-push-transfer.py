from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
import datetime
import grpc
from domains import models, zone_info, apps, tasks
from domains.views import billing, emails

NOTIFY_DELAY = datetime.timedelta(days=3)
NOTIFY_INTERVAL = datetime.timedelta(days=5)


class Command(BaseCommand):
    help = 'Reminds users to push domains if required by the registry'

    def handle(self, *args, **options):
        now = timezone.now()
        orders = models.DomainTransferOrder.objects.filter(state=models.DomainTransferOrder.STATE_PENDING_APPROVAL)

        for order in orders:
            domain_info, sld = zone_info.get_domain_info(order.domain, registry_id=order.registry_id)  # type: (zone_info.DomainInfo, str)

            if not domain_info:
                print(f"Can't notify {order.domain}: unknown zone")
                continue

            user = order.get_user()

            if (order.timestamp - NOTIFY_DELAY) <= now and order.last_transfer_notify <= (now - NOTIFY_INTERVAL):
                if domain_info.registry == domain_info.REGISTRY_NOMINET:
                    print(f"{order.domain} not yet transferred, notifying")
                    emails.send_email(user, {
                        "subject": "Your .uk domain transfer",
                        "content": render_to_string("domains_email/uk_transfer_notification.html", {
                            "domain": order.domain,
                        })
                    })
                    order.last_transfer_notify = now
                    order.save()
