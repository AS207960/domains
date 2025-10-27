from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
from domains.views import emails
import requests
import csv
import datetime
import dataclasses
import domains.models


@dataclasses.dataclass
class NSFlags:
    nxdomain_error: bool = False
    servfail_error: bool = False
    timeout_error: bool = False
    less_than_two_ns: bool = False
    less_than_two_ns_with_aaaa: bool = False
    less_than_two_aaaa: bool = False
    not_resolvable_over_ipv6: bool = False
    no_aaaa_at_apex: bool = False

    @classmethod
    def from_code(cls, code: int):
        return cls(
            nxdomain_error=bool(code & 2),
            servfail_error=bool(code & 4),
            timeout_error=bool(code & 8),
            less_than_two_ns=bool(code & 16),
            less_than_two_ns_with_aaaa=bool(code & 32),
            less_than_two_aaaa=bool(code & 64),
            not_resolvable_over_ipv6=bool(code & 128),
            no_aaaa_at_apex=bool(code & 256),
        )

class Command(BaseCommand):
    help = 'Processes the daily IPv6 reports from SWITCH, and emails registrants'

    def handle(self, *args, **options):
        report_url = (f"https://registrar.nic.ch/dnlist/{settings.SWITCH_REGISTRAR_ID}/"
                      f"resilience_nsip_error_report_{settings.SWITCH_REGISTRAR_ID}.csv")
        r = requests.get(report_url, auth=(settings.SWITCH_REGISTRAR_ID, settings.SWITCH_REGISTRAR_PASSWORD))
        r.raise_for_status()

        lines = csv.DictReader(r.text.splitlines()[2:])
        for line in lines:
            domain = line["Domain name"]

            domain_obj = domains.models.DomainRegistration.objects.filter(domain=domain).first()
            if not domain_obj:
                continue
            user = domain_obj.get_user()

            error_date = datetime.date.fromisoformat(line["Error date"])
            error_code = NSFlags.from_code(int(line["NSIP SC"]))

            if user:
                emails.send_email(user, {
                    "subject": "IPv6 error report",
                    "content": render_to_string("domains_email/switch_ipv6_report.html", {
                        "domain": domain_obj,
                        "error_date": error_date,
                        "ipv6_status": error_code,
                    })
                })
