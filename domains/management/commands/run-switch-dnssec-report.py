from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import requests
import csv
import datetime
import dataclasses
import domains.models


class Command(BaseCommand):
    help = 'Processes the daily DNSSEC reports from SWITCH, and emails registrants'

    def handle(self, *args, **options):
        report_url = (f"https://registrar.nic.ch/dnlist/{settings.SWITCH_REGISTRAR_ID}/"
                      f"resilience_error_report_{settings.SWITCH_REGISTRAR_ID}.csv")
        r = requests.get(report_url, auth=(settings.SWITCH_REGISTRAR_ID, settings.SWITCH_REGISTRAR_PASSWORD))
        r.raise_for_status()

        lines = csv.DictReader(r.text.splitlines()[1:])
        for line in lines:
            domain = line["Domain name"]

            domain_obj = domains.models.DomainRegistration.objects.filter(domain=domain).first()
            if not domain_obj:
                continue

            domain_report_url = line["Report URL"]
            error_date = datetime.date.fromisoformat(line["Error date"])

            user = domain_obj.get_user()
            context = {
                "name": user.first_name,
                "domain": domain_obj,
                "error_date": error_date,
                "report_url": domain_report_url,
                "subject": "DNSSEC error report"
            }
            html_content = render_to_string("domains_email/switch_dnssec_report.html", context)
            txt_content = render_to_string("domains_email/switch_dnssec_report.txt", context)

            email = EmailMultiAlternatives(
                subject='DNSSEC error report',
                body=txt_content,
                to=[user.email],
                bcc=['email-log@as207960.net'],
                reply_to=['Glauca Support <hello@glauca.digital>']
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
