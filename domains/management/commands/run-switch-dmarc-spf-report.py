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
class DMARCFlags:
    no_measurement_data: bool = False
    has_txt_data: bool = False
    no_dmarc_record: bool = False
    syntax_error: bool = False
    more_than_one_dmarc_record: bool = False
    dmarc_none_policy: bool = False
    dmarc_pct_below_100: bool = False
    invalid_dmarc_tag: bool = False
    invalid_dmarc_tag_value: bool = False

    @classmethod
    def from_code(cls, code: int):
        return cls(
            no_measurement_data=bool(code & 1),
            has_txt_data=bool(code & 2),
            no_dmarc_record=bool(code & 32),
            syntax_error=bool(code & 64),
            more_than_one_dmarc_record=bool(code & 128),
            dmarc_none_policy=bool(code & 256),
            dmarc_pct_below_100=bool(code & 512),
            invalid_dmarc_tag=bool(code & 1024),
            invalid_dmarc_tag_value=bool(code & 2048),
        )


@dataclasses.dataclass
class SPFFlags:
    no_measurement_data: bool = False
    has_txt_data: bool = False
    no_spf_record: bool = False
    syntax_error: bool = False
    more_than_one_spf_record: bool = False
    prohibited_all_qualifier: bool = False
    ipv4_prefix_too_large: bool = False
    ipv6_prefix_too_large: bool = False
    too_many_dns_lookups: bool = False
    too_many_void_lookups: bool = False
    redirect_loop: bool = False
    include_loop: bool = False
    included_record_does_not_exist: bool = False

    @classmethod
    def from_code(cls, code: int):
        return cls(
            no_measurement_data=bool(code & 1),
            has_txt_data=bool(code & 2),
            no_spf_record=bool(code & 32),
            syntax_error=bool(code & 64),
            more_than_one_spf_record=bool(code & 128),
            prohibited_all_qualifier=bool(code & 256),
            ipv4_prefix_too_large=bool(code & 512),
            ipv6_prefix_too_large=bool(code & 1024),
            too_many_dns_lookups=bool(code & 2048),
            too_many_void_lookups=bool(code & 4096),
            redirect_loop=bool(code & 8192),
            include_loop=bool(code & 16384),
            included_record_does_not_exist=bool(code & 32768),
        )


class Command(BaseCommand):
    help = 'Processes the daily DMARC and SPF reports from SWITCH, and emails registrants'

    def handle(self, *args, **options):
        report_url = (f"https://registrar.nic.ch/dnlist/{settings.SWITCH_REGISTRAR_ID}/"
                      f"resilience_dmarc_spf_error_report_{settings.SWITCH_REGISTRAR_ID}.csv")
        r = requests.get(report_url, auth=(settings.SWITCH_REGISTRAR_ID, settings.SWITCH_REGISTRAR_PASSWORD))
        r.raise_for_status()

        lines = csv.DictReader(r.text.splitlines()[1:])
        for line in lines:
            domain = line["Domain name"]

            domain_obj = domains.models.DomainRegistration.objects.filter(domain=domain).first()
            if not domain_obj:
                continue

            error_date = datetime.date.fromisoformat(line["Error date"])
            dmarc_code = DMARCFlags.from_code(int(line["DMARC SC"])) if line.get("DMARC SC") else None
            spf_code = SPFFlags.from_code(int(line["SPF SC"])) if line.get("SPF SC") else None
            report_url = line["Report URL"] if line.get("Report URL") else None

            if dmarc_code or spf_code:
                user = domain_obj.get_user()
                if user:
                    emails.send_email(user, {
                        "subject": "DMARC/SPF error report",
                        "content": render_to_string("domains_email/switch_dmarc_spf_report.html", {
                            "domain": domain_obj,
                            "error_date": error_date,
                            "dmarc_status": dmarc_code,
                            "spf_status": spf_code,
                            "report_url": report_url,
                        })
                    })
