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

NOTIFY_DELAY = datetime.timedelta(days=3)
NOTIFY_INTERVAL = datetime.timedelta(days=5)


def mail_uk_notification(user, domain):
    context = {
        "name": user.first_name,
        "domain": domain,
        "subject": "Your .uk domain transfer"
    }
    html_content = render_to_string("domains_email/uk_transfer_notification.html", context)
    txt_content = render_to_string("domains_email/uk_transfer_notification.txt", context)

    email = EmailMultiAlternatives(
        subject='Your .uk domain transfer',
        body=txt_content,
        to=[user.email],
        bcc=['email-log@as207960.net'],
        reply_to=['Glauca Support <hello@glauca.digital>']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


class Command(BaseCommand):
    help = 'Reminds users to push domains if required by the registry'

    def handle(self, *args, **options):
        now = timezone.now()
        orders = models.DomainTransferOrder.objects.filter(state=models.DomainTransferOrder.STATE_PENDING_APPROVAL)

        for order in orders:
            domain_info, sld = zone_info.get_domain_info(order.domain)  # type: (zone_info.DomainInfo, str)

            if not domain_info:
                print(f"Can't notify {order.domain}: unknown zone")
                continue

            user = order.get_user()

            if (order.timestamp - NOTIFY_DELAY) <= now and order.last_transfer_notify <= (now - NOTIFY_INTERVAL):
                if domain_info.registry == domain_info.REGISTRY_NOMINET:
                    print(f"{order.domain} not yet transferred, notifying")
                    mail_uk_notification(user, order.domain)
                    order.last_transfer_notify = now
                    order.save()
