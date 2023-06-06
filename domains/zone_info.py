import pytz
import decimal
import typing
import datetime
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from django.utils import timezone
import domains.views.billing

from . import apps


def _mul(value, unit):
    if unit == 1:
        return decimal.Decimal(value) / decimal.Decimal(12)
    else:
        return decimal.Decimal(value)


class SimplePrice:
    def __init__(self, price: int, periods=None, restore=0, renewal=None, transfer=0):
        self.price = price
        self._renewal = renewal if renewal else price
        self._restore = restore
        self._transfer = transfer
        self.periods = list(periods) if periods else list(map(lambda i: apps.epp_api.Period(
            unit=0,
            value=i
        ), range(1, 11)))
        self.default_value = self.periods[0].value
        self.default_unit = self.periods[0].unit

    @property
    def currency(self):
        return "GBP"

    def representative_registration(self):
        return decimal.Decimal(self.price) / decimal.Decimal(100)

    def representative_renewal(self):
        return decimal.Decimal(self._renewal) / decimal.Decimal(100) if self._renewal is not None else None

    def representative_restore(self):
        return decimal.Decimal(self._restore) / decimal.Decimal(100) if self._restore is not None else None

    def representative_transfer(self):
        return decimal.Decimal(self._transfer) / decimal.Decimal(100) if self._transfer is not None else None

    def fees(self, country: str, username, sld):
        return {
            "periods": list(map(lambda p: {
                "period": p,
                "create": self.registration(country, username, sld, p.value, p.unit, local_currency=True),
                "renew": self.renewal(country, username, sld, p.value, p.unit, local_currency=True),
            }, self.periods)),
            "restore": self.restore(country, username, sld, local_currency=True),
            "transfer": self.transfer(country, username, sld, local_currency=True),
        }

    def registration(self, country: str, username, sld: str, value=None, unit=None, local_currency=False):
        if value is None:
            value = self.default_value
        if unit is None:
            unit = self.default_unit
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        fee = (decimal.Decimal(self.price) / decimal.Decimal(100)) * _mul(value, unit)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )

    def renewal(self, country: str, username, sld: str, value=1, unit=0, local_currency=False):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        fee = (decimal.Decimal(self._renewal) / decimal.Decimal(100)) * _mul(value, unit)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )

    def restore(self, country: str, username, sld: str, local_currency=False):
        fee = decimal.Decimal(self._restore) / decimal.Decimal(100)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )

    def transfer(self,  country: str, username, sld: str, value=1, unit=0, local_currency=False):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        fee = (decimal.Decimal(self._transfer) / decimal.Decimal(100)) * _mul(value, unit)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )


class Nominet2021PromotionalPrice:
    def __init__(self, price: int):
        self.price = price
        self._renewal = price
        self.periods = list(map(lambda i: apps.epp_api.Period(
            unit=0,
            value=i
        ), range(1, 11)))
        self.default_value = self.periods[0].value
        self.default_unit = self.periods[0].unit
        self._start = datetime.datetime(2021, 10, 1, 0, 0, 0, tzinfo=pytz.timezone("Europe/London"))
        self._end = datetime.datetime(2021, 11, 30, 23, 59, 59, tzinfo=pytz.timezone("Europe/London"))

    @property
    def currency(self):
        return "GBP"

    def representative_registration(self):
        now = timezone.now()
        if now >= self._start and now <= self._end:
            return decimal.Decimal("2.09")
        else:
            return decimal.Decimal(self.price) / decimal.Decimal(100)

    def representative_renewal(self):
        return decimal.Decimal(self._renewal) / decimal.Decimal(100) if self._renewal is not None else None

    def representative_restore(self):
        return None

    def representative_transfer(self):
        return decimal.Decimal(0)

    def fees(self, country: str, username, sld):
        return {
            "periods": list(map(lambda p: {
                "period": p,
                "create": self.registration(country, username, sld, p.value, p.unit, local_currency=True),
                "renew": self.renewal(country, username, sld, p.value, p.unit, local_currency=True),
            }, self.periods)),
            "restore": self.restore(country, username, sld, local_currency=True),
            "transfer": self.transfer(country, username, sld, local_currency=True),
        }

    def registration(self, country: str, username, sld: str, value=None, unit=None, local_currency=False):
        if value is None:
            value = self.default_value
        if unit is None:
            unit = self.default_unit
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None

        now = timezone.now()
        if now >= self._start and now <= self._end and unit == 0:
            fee = decimal.Decimal("2.09")
            value -= 1
        else:
            fee = decimal.Decimal(0)

        fee += (decimal.Decimal(self.price) / decimal.Decimal(100)) * _mul(value, unit)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )

    def renewal(self, country: str, username, sld: str, value=1, unit=0, local_currency=False):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        fee = (decimal.Decimal(self._renewal) / decimal.Decimal(100)) * _mul(value, unit)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )

    def restore(self, country: str, username, sld: str, local_currency=False):
        return None

    def transfer(self,  country: str, username, sld: str, value=1, unit=0, local_currency=False):
        fee = decimal.Decimal(0)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )


class LengthPrice:
    def __init__(self, standard_price: int, lengths, periods=None, restore=0, renewal=None, transfer=0):
        self.standard_price = standard_price
        self.lengths = lengths
        self._renewal = renewal if renewal else standard_price
        self._restore = restore
        self._transfer = transfer
        self.periods = periods if periods else list(map(lambda i: apps.epp_api.Period(
            unit=0,
            value=i
        ), range(1, 11)))

    @property
    def currency(self):
        return "GBP"

    def representative_registration(self):
        return decimal.Decimal(self.standard_price) / decimal.Decimal(100)

    def representative_renewal(self):
        return decimal.Decimal(self._renewal) / decimal.Decimal(100) if self._renewal is not None else None

    def representative_restore(self):
        return decimal.Decimal(self._restore) / decimal.Decimal(100) if self._restore is not None else None

    def representative_transfer(self):
        return decimal.Decimal(self._transfer) / decimal.Decimal(100) if self._transfer is not None else None

    def fees(self, country: str, username, sld):
        return {
            "periods": list(map(lambda p: {
                "period": p,
                "create": self.registration(country, username, sld, p.value, p.unit, local_currency=True),
                "renew": self.renewal(country, username,sld, p.value, p.unit, local_currency=True),
            }, self.periods)),
            "restore": self.restore(country, username, sld, local_currency=True),
            "transfer": self.transfer(country, username, sld, local_currency=True),
        }

    def registration(self, country: str, username, sld: str, value=1, unit=0, local_currency=False):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        fee = (decimal.Decimal(
            self.lengths.get(len(sld), self.standard_price)
        ) / decimal.Decimal(100)) * _mul(value, unit)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )

    def renewal(self, country: str, username, sld: str, value=1, unit=0, local_currency=False):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        fee = (decimal.Decimal(self._renewal) / decimal.Decimal(100)) * _mul(value, unit)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )

    def restore(self, country: str, username, sld: str, local_currency=False):
        fee = decimal.Decimal(self._restore) / decimal.Decimal(100)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )

    def transfer(self, country: str, username, sld: str, value=1, unit=0, local_currency=False):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        fee = (decimal.Decimal(self._transfer) / decimal.Decimal(100)) * _mul(value, unit)
        return domains.views.billing.convert_currency(
            fee, "GBP", username, None, country, local_currency=local_currency
        )


class MarkupPrice:
    def __init__(
            self, price: int, markup: decimal.Decimal, tld: str, currency: typing.Optional[str], display_currency=None,
            periods=None, restore=0, renewal=None, transfer=0, phase=None, sub_phase=None
    ):
        self.price = price
        self._tld = tld
        self._markup = markup
        self._currency = currency
        self._display_currency = display_currency if display_currency else currency
        self._renewal = renewal if renewal else price
        self._restore = restore
        self._transfer = transfer
        self._phase = phase
        self._sub_phase = sub_phase
        self.periods = list(periods) if periods else list(map(lambda i: apps.epp_api.Period(
            unit=0,
            value=i
        ), range(1, 11)))

    @property
    def currency(self):
        return self._display_currency

    def representative_registration(self):
        return decimal.Decimal(self.price) / decimal.Decimal(100)

    def representative_renewal(self):
        return decimal.Decimal(self._renewal) / decimal.Decimal(100) if self._renewal is not None else None

    def representative_restore(self):
        return decimal.Decimal(self._restore) / decimal.Decimal(100) if self._restore is not None else None

    def representative_transfer(self):
        return decimal.Decimal(self._transfer) / decimal.Decimal(100) if self._transfer is not None else None

    def fees(self, country: str, username, sld):
        domain = f"{sld}.{self._tld}"

        commands_split = [[apps.epp_api.fee_pb2.FeeCommand(
            command=apps.epp_api.fee_pb2.Transfer,
            period=None,
            phase=apps.epp_api.StringValue(value=self._phase) if self._phase else None,
            sub_phase=apps.epp_api.StringValue(value=self._sub_phase) if self._sub_phase else None,
        ), apps.epp_api.fee_pb2.FeeCommand(
            command=apps.epp_api.fee_pb2.Restore,
            period=None,
            phase=apps.epp_api.StringValue(value=self._phase) if self._phase else None,
            sub_phase=apps.epp_api.StringValue(value=self._sub_phase) if self._sub_phase else None,
        )]]

        for period in self.periods:
            commands_split.append([apps.epp_api.fee_pb2.FeeCommand(
                command=apps.epp_api.fee_pb2.Create,
                period=period.to_pb(),
                phase=apps.epp_api.StringValue(value=self._phase) if self._phase else None,
                sub_phase=apps.epp_api.StringValue(value=self._sub_phase) if self._sub_phase else None,
            ), apps.epp_api.fee_pb2.FeeCommand(
                command=apps.epp_api.fee_pb2.Renew,
                period=period.to_pb(),
                phase=apps.epp_api.StringValue(value=self._phase) if self._phase else None,
                sub_phase=apps.epp_api.StringValue(value=self._sub_phase) if self._sub_phase else None,
            )])

        commands_resp = []

        with ThreadPoolExecutor() as e:
            resps = e.map(lambda commands: apps.epp_client.stub.DomainCheck(apps.epp_api.domain_pb2.DomainCheckRequest(
                name=domain,
                fee_check=apps.epp_api.fee_pb2.FeeCheck(
                    currency=apps.epp_api.StringValue(value=self._currency) if self._currency else None,
                    commands=commands
                )
            )), commands_split)

        for resp in resps:
            if not resp.HasField("fee_check"):
                return {
                    "periods": [],
                    "restore": None,
                    "transfer": None
                }
            if not resp.fee_check.available:
                return {
                    "periods": [],
                    "restore": None,
                    "transfer": None
                }
            commands_resp.extend(resp.fee_check.commands)

        restore_command = next(filter(lambda c: c.command == apps.epp_api.fee_pb2.Restore, commands_resp), None)
        transfer_command = next(filter(lambda c: c.command == apps.epp_api.fee_pb2.Transfer, commands_resp), None)
        create_commands = list(filter(lambda c: c.command == apps.epp_api.fee_pb2.Create, commands_resp))
        renew_commands = list(filter(lambda c: c.command == apps.epp_api.fee_pb2.Renew, commands_resp))

        def map_fee(f):
            period = apps.epp_api.Period.from_pb(f.period)
            return {
                "period": period,
                "fee": self._convert_fee(f, country, username, True)
            }

        with ThreadPoolExecutor() as e:
            create_periods = list(e.map(map_fee, create_commands))
            renew_periods = list(e.map(map_fee, renew_commands))
        periods = []

        for create_period in create_periods:
            periods.append({
                "period": create_period["period"],
                "create": create_period["fee"],
                "renew": None
            })

        for renew_period in renew_periods:
            found = False
            for period in periods:
                if period["period"] == renew_period["period"]:
                    found = True
                    period["renew"] = renew_period["fee"]

            if not found:
                periods.append({
                    "period": renew_period["period"],
                    "create": None,
                    "renew": renew_period["fee"]
                })

        return {
            "periods": periods,
            "restore": self._convert_fee(restore_command, country, username, True) if restore_command else None,
            "transfer": self._convert_fee(transfer_command, country, username, True) if transfer_command else None,
        }

    def _convert_fee(self, command, country, username, local_currency, available=True):
        total_fee = decimal.Decimal(0)
        for fee in command.fees:
            total_fee += decimal.Decimal(fee.value)
        for credit in command.credits:
            total_fee += decimal.Decimal(credit.value)

        final_fee = total_fee * self._markup
        return domains.views.billing.convert_currency(
            final_fee, command.currency, username, None, country, available=available, local_currency=local_currency,
            timeout=3
        )

    def _get_fee(self, sld, value, unit, command, country, username, local_currency):
        domain = f"{sld}.{self._tld}"
        if unit is not None:
            period = apps.epp_api.Period(
                unit=unit,
                value=value
            )
            if period not in self.periods:
                return None

        resp = apps.epp_client.stub.DomainCheck(apps.epp_api.domain_pb2.DomainCheckRequest(
            name=domain,
            fee_check=apps.epp_api.fee_pb2.FeeCheck(
                currency=apps.epp_api.StringValue(value=self._currency) if self._currency else None,
                commands=[apps.epp_api.fee_pb2.FeeCommand(
                    command=command,
                    period=period.to_pb() if unit is not None else None,
                    phase=apps.epp_api.StringValue(value=self._phase) if self._phase else None,
                    sub_phase=apps.epp_api.StringValue(value=self._sub_phase) if self._sub_phase else None,
                )]
            )
        ))
        if not resp.HasField("fee_check"):
            return None
        if not resp.fee_check.available:
            return None
        command = resp.fee_check.commands[0]

        return self._convert_fee(command, country, username, local_currency, available=resp.available)

    def registration(self, country: str, username, sld: str, value=1, unit=0, local_currency=False):
        return self._get_fee(
            sld, value, unit, apps.epp_api.fee_pb2.Create, country=country, username=username,
            local_currency=local_currency
        )

    def renewal(self, country: str, username, sld: str, value=None, unit=None, local_currency=False):
        return self._get_fee(
            sld, value, unit, apps.epp_api.fee_pb2.Renew, country=country, username=username,
            local_currency=local_currency
        )

    def restore(self, country: str, username, sld: str, local_currency=False):
        fee = self._get_fee(
            sld, None, None, apps.epp_api.fee_pb2.Restore, country=country, username=username,
            local_currency=local_currency
        )
        if not fee:
            return self.representative_restore()
        else:
            return fee

    def transfer(self, country: str, username, sld: str, value=None, unit=None, local_currency=False):
        return self._get_fee(
            sld, value, unit, apps.epp_api.fee_pb2.Transfer, country=country, username=username,
            local_currency=local_currency
        )


class DomainInfo:
    REGISTRY_NOMINET = "nominet"
    REGISTRY_NOMINET_SPECIAL = "nominet-special"
    REGISTRY_NOMINET_RRPPROXY = "nominet-rrpproxy"
    REGISTRY_SWITCH = "switch"
    REGISTRY_TRAFICOM = "traficom"
    REGISTRY_AFILIAS = "afilias"
    REGISTRY_AFNIC = "afnic"
    REGISTRY_DENIC = "denic"
    REGISTRY_VERISIGN = "verisign"
    REGISTRY_DONUTS = "donuts"
    REGISTRY_VERISIGN_COMNET = "verisign-comnet"
    REGISTRY_PIR = "pir"
    REGISTRY_CENTRALNIC_CCTLD = "centralni-ccctld"
    REGISTRY_CENTRALNIC = "centralnic"
    REGISTRY_NOMINET_GTLD = "nominet-gtld"
    REGISTRY_DNSBELGIUM = "dnsbelgium"
    REGISTRY_INTERLINK = "interlink"
    REGISTRY_EURID = "eurid"
    REGISTRY_GOOGLE = "google"
    REGISTRY_SHORTDOT = "shortdot"
    REGISTRY_RADIX = "radix"
    REGISTRY_ZODIAC_LEO = "zodiac-leo"
    REGISTRY_GMO = "gmo"
    REGISTRY_DOT_STRATEGY = "dot-strategy"
    REGISTRY_MTLD = "mtld"
    REGISTRY_REGISTRY_PRO = "registry-pro"
    REGISTRY_WHOIS_THERE = "knock-knock-whois-there"
    REGISTRY_CORE = "core"
    REGISTRY_CLUB_DOMAINS = "club-domains"
    REGISTRY_MINDS_MACHINES = "minds-machines"
    REGISTRY_INFIBEAM = "infibeam"
    REGISTRY_ICB = "ICB"
    REGISTRY_CO = "CO"
    REGISTRY_KENIC = "kenic"
    REGISTRY_AKEP = "akep"
    REGISTRY_AMNIC = "amnic"
    REGISTRY_UNIREGISTRY = "uniregistry"
    REGISTRY_AFMOF = "afmoc"
    REGISTRY_NIXI = "nixi"
    REGISTRY_FDSRDDS = "fdsrdds"
    REGISTRY_RNIDS = "rnids"
    REGISTRY_NICAT = "nicat"
    REGISTRY_CIRA = "cira"
    REGISTRY_ISNIC = "isnic"
    REGISTRY_GODADDY = "godaddy"
    REGISTRY_GODADDY_CCTLD = "godaddy-cctld"
    REGISTRY_MNI = "mni"
    REGISTRY_US = "us"
    REGISTRY_NASK = "nask"
    REGISTRY_PLAN_BEE = "plan-bee"
    REGISTRY_REDES = "redes"
    REGISTRY_SIDN = "sidn"
    REGISTRY_MDMA = "mdma"
    REGISTRY_COCCA = "cocca"

    def __init__(self, registry, pricing, notice=None, transfer_instructions=None):
        self.registry = registry
        self.pricing = pricing
        self.notice = notice
        self.transfer_instructions = transfer_instructions

    @property
    def supported_dnssec_algorithms(self):
        if self.registry == self.REGISTRY_TRAFICOM:
            return 7, 8, 10, 13
        elif self.registry == self.REGISTRY_SWITCH:
            return 8, 10, 13, 14, 15, 16
        elif self.registry == self.REGISTRY_VERISIGN:
            return 5, 7, 8, 10, 12, 13, 14, 15, 16, 253, 254
        elif self.registry == self.REGISTRY_ISNIC:
            return 3, 5, 7, 8, 10, 12, 13, 14, 15, 16, 253, 254
        elif self.registry == self.REGISTRY_MNI:
            return ()
        else:
            return 5, 7, 8, 10, 13, 14, 15, 16

    @property
    def supported_dnssec_digests(self):
        if self.registry == self.REGISTRY_SWITCH:
            return 2, 4
        if self.registry == self.REGISTRY_ISNIC:
            return 1, 2, 3, 4
        if self.registry == self.REGISTRY_MNI:
            return ()
        else:
            return 1, 2, 4

    @property
    def supports_cds(self):
        if self.registry == self.REGISTRY_SWITCH:
            return True
        else:
            return False

    @property
    def redemption_period(self):
        if self.registry in (self.REGISTRY_SWITCH, self.REGISTRY_DNSBELGIUM, self.REGISTRY_EURID):
            return datetime.timedelta(days=40)
        elif self.registry == self.REGISTRY_PIR:
            return datetime.timedelta(days=35)
        elif self.registry == self.REGISTRY_NICAT:
            return datetime.timedelta(days=59)
        elif self.registry == self.REGISTRY_AMNIC:
            return datetime.timedelta(days=15)
        elif self.registry == self.REGISTRY_NASK:
            return datetime.timedelta(days=0)
        elif self.registry in (self.REGISTRY_AFMOF, self.REGISTRY_FDSRDDS, self.REGISTRY_MNI):
            return datetime.timedelta(days=28)
        else:
            return datetime.timedelta(days=30)

    @property
    def expiry_offset(self):
        if self.registry == self.REGISTRY_KENIC:
            return datetime.timedelta(days=-21)
        else:
            return datetime.timedelta(days=0)

    @property
    def renews_if_not_deleted(self):
        return self.registry not in (
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_KENIC,
        )

    @property
    def direct_registration_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_VERISIGN,
            self.REGISTRY_CENTRALNIC_CCTLD,
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_GODADDY_CCTLD,
        )

    @property
    def direct_transfer_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_DENIC,
            self.REGISTRY_CENTRALNIC_CCTLD,
            self.REGISTRY_VERISIGN,
            self.REGISTRY_GODADDY_CCTLD,
        )

    @property
    def info_with_auth_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_VERISIGN,
            self.REGISTRY_GODADDY_CCTLD,
        )

    @property
    def keysys_de(self):
        return self.registry in (
            self.REGISTRY_DENIC
        )

    @property
    def disclosure_supported(self):
        return self.registry not in (
            self.REGISTRY_AFILIAS,
            self.REGISTRY_GODADDY_CCTLD,
        )

    @property
    def transfer_supported(self):
        return self.registry in (
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_SWITCH,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_DENIC,
            self.REGISTRY_AFNIC,
            self.REGISTRY_VERISIGN_COMNET,
            self.REGISTRY_PIR,
            self.REGISTRY_GOOGLE,
            self.REGISTRY_VERISIGN,
            self.REGISTRY_SHORTDOT,
            self.REGISTRY_RADIX,
            self.REGISTRY_CENTRALNIC,
            self.REGISTRY_CENTRALNIC_CCTLD,
            self.REGISTRY_NOMINET_GTLD,
            self.REGISTRY_DONUTS,
            self.REGISTRY_ZODIAC_LEO,
            self.REGISTRY_GMO,
            self.REGISTRY_DOT_STRATEGY,
            self.REGISTRY_MTLD,
            self.REGISTRY_REGISTRY_PRO,
            self.REGISTRY_WHOIS_THERE,
            self.REGISTRY_CORE,
            self.REGISTRY_EURID,
            self.REGISTRY_INTERLINK,
            self.REGISTRY_CLUB_DOMAINS,
            self.REGISTRY_AFILIAS,
            self.REGISTRY_MINDS_MACHINES,
            self.REGISTRY_INFIBEAM,
            self.REGISTRY_DNSBELGIUM,
            self.REGISTRY_ICB,
            self.REGISTRY_CO,
            self.REGISTRY_KENIC,
            self.REGISTRY_AKEP,
            self.REGISTRY_AMNIC,
            self.REGISTRY_UNIREGISTRY,
            self.REGISTRY_AFMOF,
            self.REGISTRY_NIXI,
            self.REGISTRY_FDSRDDS,
            self.REGISTRY_RNIDS,
            self.REGISTRY_NICAT,
            self.REGISTRY_CIRA,
            self.REGISTRY_ISNIC,
            self.REGISTRY_GODADDY,
            self.REGISTRY_MNI,
            self.REGISTRY_US,
            self.REGISTRY_NASK,
            self.REGISTRY_PLAN_BEE,
            self.REGISTRY_REDES,
            self.REGISTRY_GODADDY_CCTLD,
            self.REGISTRY_SIDN,
            self.REGISTRY_MDMA,
            self.REGISTRY_COCCA,
        )

    @property
    def pre_transfer_query_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_AFILIAS,
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_CENTRALNIC_CCTLD,
            self.REGISTRY_ISNIC,
            self.REGISTRY_GODADDY_CCTLD,
        )

    @property
    def standard_auth_code_procedure(self):
        return self.registry not in (
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_NOMINET_RRPPROXY,
            self.REGISTRY_DNSBELGIUM,
            self.REGISTRY_DENIC,
            self.REGISTRY_AMNIC,
            self.REGISTRY_EURID,
            self.REGISTRY_ISNIC,
            self.REGISTRY_REDES,
        )

    @property
    def auth_code_for_transfer(self):
        return self.registry not in (
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_NOMINET_RRPPROXY,
            self.REGISTRY_ISNIC,
        )

    @property
    def renew_supported(self):
        return self.registry not in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_DENIC,
            self.REGISTRY_DNSBELGIUM,
            self.REGISTRY_NICAT,
            self.REGISTRY_SIDN,
        )

    @property
    def direct_renew_supported(self):
        return self.registry not in (
            self.REGISTRY_ISNIC,
        )

    @property
    def restore_supported(self):
        return self.registry not in (
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_NOMINET_RRPPROXY,
            self.REGISTRY_KENIC,
            self.REGISTRY_AKEP,
            self.REGISTRY_RNIDS,
            self.REGISTRY_NASK,
        )

    @property
    def direct_restore_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_ISNIC,
        )

    @property
    def transfer_lock_supported(self):
        return self.registry not in (
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_SWITCH,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_EURID,
            self.REGISTRY_DNSBELGIUM,
            self.REGISTRY_KENIC,
            self.REGISTRY_NICAT,
            self.REGISTRY_ISNIC,
            self.REGISTRY_NASK,
            self.REGISTRY_REDES,
            self.REGISTRY_SIDN,
        )

    @property
    def registry_lock_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
        )

    @property
    def fee_supported(self):
        return self.registry not in (
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_SWITCH,
            self.REGISTRY_ISNIC,
        )

    @property
    def registrant_supported(self):
        return self.registry not in (
            self.REGISTRY_VERISIGN
        )

    @property
    def registrant_change_supported(self):
        return self.registry not in (
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_DNSBELGIUM,
            self.REGISTRY_KENIC,
            self.REGISTRY_AKEP,
            self.REGISTRY_AMNIC,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_REDES,
        )

    @property
    def ds_data_supported(self):
        return self.registry not in (
            self.REGISTRY_DENIC,
            self.REGISTRY_EURID,
        )

    @property
    def admin_supported(self):
        return self.registry not in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_VERISIGN,
            self.REGISTRY_DNSBELGIUM,
            self.REGISTRY_ISNIC,
        )

    @property
    def admin_required(self):
        return self.registry in (
            self.REGISTRY_AFILIAS,
            self.REGISTRY_DONUTS,
            self.REGISTRY_VERISIGN_COMNET,
            self.REGISTRY_PIR,
            self.REGISTRY_CENTRALNIC_CCTLD,
            self.REGISTRY_CENTRALNIC,
            self.REGISTRY_NOMINET_GTLD,
            self.REGISTRY_EURID,
            self.REGISTRY_AFNIC,
            self.REGISTRY_INTERLINK,
            self.REGISTRY_GOOGLE,
            self.REGISTRY_SHORTDOT,
            self.REGISTRY_RADIX,
            self.REGISTRY_ZODIAC_LEO,
            self.REGISTRY_GMO,
            self.REGISTRY_DOT_STRATEGY,
            self.REGISTRY_MTLD,
            self.REGISTRY_REGISTRY_PRO,
            self.REGISTRY_WHOIS_THERE,
            self.REGISTRY_CORE,
            self.REGISTRY_CLUB_DOMAINS,
            self.REGISTRY_NOMINET_RRPPROXY,
            self.REGISTRY_MINDS_MACHINES,
            self.REGISTRY_INFIBEAM,
            self.REGISTRY_ICB,
            self.REGISTRY_CO,
            self.REGISTRY_KENIC,
            self.REGISTRY_AKEP,
            self.REGISTRY_AMNIC,
            self.REGISTRY_UNIREGISTRY,
            self.REGISTRY_AFMOF,
            self.REGISTRY_NIXI,
            self.REGISTRY_FDSRDDS,
            self.REGISTRY_RNIDS,
            self.REGISTRY_NICAT,
            self.REGISTRY_CIRA,
            self.REGISTRY_GODADDY,
            self.REGISTRY_MNI,
            self.REGISTRY_US,
            self.REGISTRY_NASK,
            self.REGISTRY_PLAN_BEE,
            self.REGISTRY_REDES,
            self.REGISTRY_GODADDY_CCTLD,
            self.REGISTRY_SIDN,
            self.REGISTRY_MDMA,
            self.REGISTRY_COCCA,
        )

    @property
    def tech_supported(self):
        return self.registry not in (
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_VERISIGN,
        )

    @property
    def tech_required(self):
        return self.registry in (
            self.REGISTRY_AFILIAS,
            self.REGISTRY_DONUTS,
            self.REGISTRY_VERISIGN_COMNET,
            self.REGISTRY_PIR,
            self.REGISTRY_CENTRALNIC_CCTLD,
            self.REGISTRY_CENTRALNIC,
            self.REGISTRY_NOMINET_GTLD,
            self.REGISTRY_EURID,
            self.REGISTRY_AFNIC,
            self.REGISTRY_INTERLINK,
            self.REGISTRY_GOOGLE,
            self.REGISTRY_SHORTDOT,
            self.REGISTRY_RADIX,
            self.REGISTRY_ZODIAC_LEO,
            self.REGISTRY_GMO,
            self.REGISTRY_DOT_STRATEGY,
            self.REGISTRY_MTLD,
            self.REGISTRY_REGISTRY_PRO,
            self.REGISTRY_WHOIS_THERE,
            self.REGISTRY_CORE,
            self.REGISTRY_CLUB_DOMAINS,
            self.REGISTRY_NOMINET_RRPPROXY,
            self.REGISTRY_MINDS_MACHINES,
            self.REGISTRY_INFIBEAM,
            self.REGISTRY_ICB,
            self.REGISTRY_CO,
            self.REGISTRY_KENIC,
            self.REGISTRY_AMNIC,
            self.REGISTRY_AKEP,
            self.REGISTRY_UNIREGISTRY,
            self.REGISTRY_AFMOF,
            self.REGISTRY_NIXI,
            self.REGISTRY_FDSRDDS,
            self.REGISTRY_RNIDS,
            self.REGISTRY_NICAT,
            self.REGISTRY_CIRA,
            self.REGISTRY_ISNIC,
            self.REGISTRY_GODADDY,
            self.REGISTRY_MNI,
            self.REGISTRY_US,
            self.REGISTRY_NASK,
            self.REGISTRY_PLAN_BEE,
            self.REGISTRY_REDES,
            self.REGISTRY_GODADDY_CCTLD,
            self.REGISTRY_SIDN,
            self.REGISTRY_MDMA,
            self.REGISTRY_COCCA,
        )

    @property
    def billing_supported(self):
        return self.registry not in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_VERISIGN,
            self.REGISTRY_DNSBELGIUM,
            self.REGISTRY_ISNIC,
        )

    @property
    def billing_required(self):
        return self.registry in (
            self.REGISTRY_AFILIAS,
            self.REGISTRY_DONUTS,
            self.REGISTRY_VERISIGN_COMNET,
            self.REGISTRY_PIR,
            self.REGISTRY_CENTRALNIC_CCTLD,
            self.REGISTRY_CENTRALNIC,
            self.REGISTRY_NOMINET_GTLD,
            self.REGISTRY_EURID,
            self.REGISTRY_AFNIC,
            self.REGISTRY_INTERLINK,
            self.REGISTRY_GOOGLE,
            self.REGISTRY_SHORTDOT,
            self.REGISTRY_RADIX,
            self.REGISTRY_ZODIAC_LEO,
            self.REGISTRY_GMO,
            self.REGISTRY_DOT_STRATEGY,
            self.REGISTRY_MTLD,
            self.REGISTRY_REGISTRY_PRO,
            self.REGISTRY_WHOIS_THERE,
            self.REGISTRY_CORE,
            self.REGISTRY_CLUB_DOMAINS,
            self.REGISTRY_NOMINET_RRPPROXY,
            self.REGISTRY_MINDS_MACHINES,
            self.REGISTRY_INFIBEAM,
            self.REGISTRY_ICB,
            self.REGISTRY_CO,
            self.REGISTRY_KENIC,
            self.REGISTRY_AMNIC,
            self.REGISTRY_AKEP,
            self.REGISTRY_UNIREGISTRY,
            self.REGISTRY_AFMOF,
            self.REGISTRY_NIXI,
            self.REGISTRY_FDSRDDS,
            self.REGISTRY_RNIDS,
            self.REGISTRY_NICAT,
            self.REGISTRY_CIRA,
            self.REGISTRY_GODADDY,
            self.REGISTRY_MNI,
            self.REGISTRY_US,
            self.REGISTRY_NASK,
            self.REGISTRY_PLAN_BEE,
            self.REGISTRY_REDES,
            self.REGISTRY_SIDN,
            self.REGISTRY_MDMA,
            self.REGISTRY_COCCA,
        )

    @property
    def pre_create_host_objects(self):
        return self.registry in (
            self.REGISTRY_NOMINET,
            self.REGISTRY_NOMINET_SPECIAL,
            self.REGISTRY_SWITCH,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_AFILIAS,
            self.REGISTRY_CENTRALNIC_CCTLD,
            self.REGISTRY_VERISIGN,
            self.REGISTRY_ISNIC,
            self.REGISTRY_GODADDY_CCTLD,
        )

    @property
    def period_required_for_transfer(self):
        return self.registry in (
            self.REGISTRY_GODADDY_CCTLD,
        )


if settings.DEBUG:
    ZONES = (
        ('uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, Nominet2021PromotionalPrice(917))),
        ('co.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, Nominet2021PromotionalPrice(917))),
        ('org.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, Nominet2021PromotionalPrice(917))),
        ('me.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, Nominet2021PromotionalPrice(917))),
        ('ltd.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET_SPECIAL, SimplePrice(8000, periods=[apps.epp_api.Period(
            unit=0,
            value=2
        )]))),
        ('plc.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET_SPECIAL, SimplePrice(8000, periods=[apps.epp_api.Period(
            unit=0,
            value=2
        )]))),
        ('net.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET_SPECIAL, SimplePrice(8000, periods=[apps.epp_api.Period(
            unit=0,
            value=2
        )]))),
        ('ch', DomainInfo(DomainInfo.REGISTRY_SWITCH, SimplePrice(1400, periods=[apps.epp_api.Period(
            unit=0,
            value=1
        )]))),
        ('li', DomainInfo(DomainInfo.REGISTRY_SWITCH, SimplePrice(1400, periods=[apps.epp_api.Period(
            unit=0,
            value=1
        )]))),
        # ('ae.org', LengthPrice(1600, {2: 17000})),
        # ('br.com', LengthPrice(3200, {2: 17000})),
        # ('cn.com', LengthPrice(1400, {2: 17000}, renewal=3000)),
        # ('co.com', SimplePrice(2000, restore=4000)),
        # ('co.nl', SimplePrice(700, restore=5000)),
        # ('co.no', SimplePrice(1600, restore=5000)),
        # ('com.de', LengthPrice(500, {2: 12500})),
        # ('com.se', SimplePrice(900)),
        # ('de.com', LengthPrice(1400, {2: 12500})),
        # ('eu.com', LengthPrice(1400, {2: 12500})),
        # ('fm', SimplePrice(7500, restore=3500)),
        # ('fo', SimplePrice(4500, restore=4500)),
        # ('gb.net', SimplePrice(700)),
        # ('gd', SimplePrice(2500, restore=4300)),
        # ('gr.com', SimplePrice(1500)),
        # ('hu.net', SimplePrice(2500)),
        # ('in.net', SimplePrice(700)),
        # ('jp.net', SimplePrice(900)),
        # ('jpn.com', SimplePrice(3200)),
        # ('mex.com', SimplePrice(1200)),
        ('pw', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2700, renewal=2700, currency=None, display_currency='USD', tld='pw',
                        markup=decimal.Decimal("1.5"))
        )),
        # ('radio.am', SimplePrice(1400, restore=3500)),
        # ('radio.fm', SimplePrice(1400, restore=3500)),
        # ('ru.com', SimplePrice(3000)),
        # ('sa.com', SimplePrice(4500)),
        # ('se.net', SimplePrice(2700)),
        # ('uk.com', SimplePrice(2100)),
        # ('uk.net', SimplePrice(2100)),
        # ('us.com', SimplePrice(1900)),
        # ('us.org', SimplePrice(1900)),
        # ('vg', SimplePrice(2500, restore=4500)),
        # ('za.com', SimplePrice(4700)),
        ('fi', DomainInfo(DomainInfo.REGISTRY_TRAFICOM, SimplePrice(2500, periods=map(lambda i: apps.epp_api.Period(
            unit=0,
            value=i
        ), range(1, 6))))),
        ('me', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(1400, currency='EUR', tld='me', markup=decimal.Decimal("1.25"))
        )),
        ('de', DomainInfo(
            DomainInfo.REGISTRY_DENIC,
            MarkupPrice(1368, renewal=1080, restore=4500, currency='USD', display_currency='EUR', tld='de',
                        markup=decimal.Decimal("1.5"))
        )),
        ('tv', DomainInfo(
            DomainInfo.REGISTRY_GODADDY_CCTLD,
            MarkupPrice(2566, restore=4000, currency='USD', tld='tv', markup=decimal.Decimal("1.25"), phase="open")
        )),
        ('cc', DomainInfo(DomainInfo.REGISTRY_VERISIGN, SimplePrice(825, restore=4000))),
        ('dev', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2940, transfer=2940, restore=22500, currency=None, display_currency='USD', tld='dev',
                        markup=decimal.Decimal("1.4")),
            notice=".dev is a HSTS preload zone, meaning you'll need to deploy HTTPS on any website hosted on a "
                   ".dev domain."
        )),
        ('is', DomainInfo(
            DomainInfo.REGISTRY_ISNIC,
            SimplePrice(3583, periods=[apps.epp_api.Period(
                unit=0,
                value=1
            )]),
            transfer_instructions="Make sure to change the admin and billing contact to \"AC396-IS\" at "
                                  "your previous registrar."
        )),
    )
else:
    ZONES = (
        ('com', DomainInfo(
            DomainInfo.REGISTRY_VERISIGN_COMNET,
            MarkupPrice(2234, transfer=2234, restore=16200, currency=None, display_currency='USD', tld='com',
                        markup=decimal.Decimal("1.5"))
        )),
        ('net', DomainInfo(
            DomainInfo.REGISTRY_VERISIGN_COMNET,
            MarkupPrice(3009, transfer=3009, restore=15120, currency=None, display_currency='USD', tld='net',
                        markup=decimal.Decimal("1.4"))
        )),
        ('name', DomainInfo(
            DomainInfo.REGISTRY_VERISIGN_COMNET,
            MarkupPrice(2002, transfer=2002, restore=14400, currency=None, display_currency='USD', tld='name',
                        markup=decimal.Decimal("1.6"))
        )),
        ('org', DomainInfo(
            DomainInfo.REGISTRY_PIR,
            MarkupPrice(2758, transfer=2758, restore=15660, currency=None, display_currency='USD', tld='org',
                        markup=decimal.Decimal("1.45"))
        )),
        ('ch', DomainInfo(DomainInfo.REGISTRY_SWITCH, SimplePrice(999, periods=[apps.epp_api.Period(
            unit=0,
            value=1
        )]))),
        ('li', DomainInfo(DomainInfo.REGISTRY_SWITCH, SimplePrice(999, periods=[apps.epp_api.Period(
            unit=0,
            value=1
        )]))),
        ('is', DomainInfo(
            DomainInfo.REGISTRY_ISNIC,
            SimplePrice(3583, periods=[apps.epp_api.Period(
                unit=0,
                value=1
            )]),
            transfer_instructions="Make sure to change the admin and billing contact to \"AC396-IS\" at "
                                  "your previous registrar."
        )),
        ('me', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(1760, transfer=1760, restore=14040, currency=None, display_currency='EUR', tld='me',
                        markup=decimal.Decimal("1.6"))
        )),
        ('pw', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2700, transfer=2700, currency=None, display_currency='USD', tld='pw',
                        markup=decimal.Decimal("1.7"))
        )),
        ('fm', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(12240, transfer=12240, restore=17280, currency=None, display_currency='USD', tld='fm',
                        markup=decimal.Decimal("1.4"))
        )),
        ('fo', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(6048, transfer=6048, restore=18808, currency=None, display_currency='EUR', tld='fo',
                        markup=decimal.Decimal("1.4"))
        )),
        ('gd', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(3900, transfer=3900, restore=10920, currency=None, display_currency='USD', tld='gd',
                        markup=decimal.Decimal("1.5"))
        )),
        ('vg', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(3900, transfer=3900, restore=10920, currency=None, display_currency='USD', tld='vg',
                        markup=decimal.Decimal("1.5"))
        )),
        ('ae.org', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2520, transfer=2520, restore=2520, currency=None, display_currency='USD', tld='ae.org',
                        markup=decimal.Decimal("1.6"))
        )),
        ('br.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(4752, transfer=4752, restore=4752, currency=None, display_currency='USD', tld='br.com',
                        markup=decimal.Decimal("1.4"))
        )),
        ('cn.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2352, renewal=5040, transfer=5040, restore=4752, currency=None, display_currency='USD',
                        tld='cn.com', markup=decimal.Decimal("1.6"))
        )),
        ('co.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(3120, transfer=3120, restore=9360, currency=None, display_currency='USD', tld='co.com',
                        markup=decimal.Decimal("1.5"))
        )),
        ('co.nl', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1176, transfer=1176, restore=12000, currency=None, display_currency='EUR', tld='co.nl',
                        markup=decimal.Decimal("2.2"))
        )),
        ('co.no', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2495, transfer=2495, restore=10072, currency=None, display_currency='EUR', tld='co.no',
                        markup=decimal.Decimal("1.6"))
        )),
        ('com.de', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1080, transfer=1080, restore=1080, currency=None, display_currency='EUR', tld='com.de',
                        markup=decimal.Decimal("2.7"))
        )),
        ('com.se', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1501, transfer=1501, restore=1501, currency=None, display_currency='EUR', tld='com.se',
                        markup=decimal.Decimal("2"))
        )),
        ('de.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2100, transfer=2100, restore=2100, currency=None, display_currency='EUR', tld='de.com',
                        markup=decimal.Decimal("1.6"))
        )),
        ('eu.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2100, transfer=2100, restore=2100, currency=None, display_currency='EUR', tld='eu.com',
                        markup=decimal.Decimal("1.6"))
        )),
        ('gb.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1200, transfer=1200, restore=1200, currency=None, display_currency='GBP', tld='gb.net',
                        markup=decimal.Decimal("2.2"))
        )),
        ('gr.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1890, transfer=1890, restore=1890, currency=None, display_currency='EUR', tld='gr.com',
                        markup=decimal.Decimal("1.7"))
        )),
        ('hu.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(3744, transfer=3744, restore=3744, currency=None, display_currency='EUR', tld='hu.net',
                        markup=decimal.Decimal("1.5"))
        )),
        ('in.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1440, transfer=1440, restore=1440, currency=None, display_currency='USD', tld='in.net',
                        markup=decimal.Decimal("2.2"))
        )),
        ('jp.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1680, transfer=1680, restore=1680, currency=None, display_currency='USD', tld='jp.net',
                        markup=decimal.Decimal("2.2"))
        )),
        ('jpn.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(4680, transfer=4680, restore=4680, currency=None, display_currency='USD', tld='jpn.com',
                        markup=decimal.Decimal("1.5"))
        )),
        ('mex.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2040, transfer=2040, restore=2040, currency=None, display_currency='USD', tld='mex.com',
                        markup=decimal.Decimal("1.9"))
        )),
        ('ru.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(4680, transfer=4680, restore=4680, currency=None, display_currency='USD', tld='ru.com',
                        markup=decimal.Decimal("1.5"))
        )),
        ('sa.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(7056, transfer=7056, restore=7056, currency=None, display_currency='USD', tld='sa.com',
                        markup=decimal.Decimal("1.4"))
        )),
        ('se.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(3588, transfer=3588, restore=3588, currency=None, display_currency='EUR', tld='se.net',
                        markup=decimal.Decimal("1.5"))
        )),
        ('uk.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2335, transfer=2335, restore=2335, currency=None, display_currency='GBP', tld='uk.com',
                        markup=decimal.Decimal("1.5"))
        )),
        ('uk.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2335, transfer=2335, restore=2335, currency=None, display_currency='GBP', tld='uk.net',
                        markup=decimal.Decimal("1.5"))
        )),
        ('us.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2520, transfer=2520, restore=2520, currency=None, display_currency='USD', tld='us.com',
                        markup=decimal.Decimal("1.6"))
        )),
        ('us.org', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2520, transfer=2520, restore=2520, currency=None, display_currency='USD', tld='us.org',
                        markup=decimal.Decimal("1.6"))
        )),
        ('za.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(7056, transfer=7056, restore=7056, currency=None, display_currency='USD', tld='za.com',
                        markup=decimal.Decimal("1.4"))
        )),
        ('radio.am', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(178, transfer=2160, restore=8460, currency=None, display_currency='USD', tld='radio.am',
                        markup=decimal.Decimal("1.7"))
        )),
        ('radio.fm', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(178, transfer=2160, restore=8460, currency=None, display_currency='USD', tld='radio.fm',
                        markup=decimal.Decimal("1.7"))
        )),
        ('gay', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(6480, transfer=6480, restore=37500, currency=None, display_currency='USD', tld='gay',
                        markup=decimal.Decimal("1.25")),
            notice="The registry will be donating 20% of all registration revenue to LGBTQ non-profit organizations. "
                   "The .gay domain will remain safe, with anti-LGBTQ content strictly prohibited and may end in domain suspension, "
                   "outlined in the .gay Rights Protections Policy."
        )),
        ('site', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(5205, transfer=5205, restore=16500, currency=None, display_currency='USD', tld='site',
                        markup=decimal.Decimal("1.25"))
        )),
        ('website', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(3900, transfer=3900, restore=13500, currency=None, display_currency='USD', tld='website',
                        markup=decimal.Decimal("1.25"))
        )),
        ('tech', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(9390, transfer=9390, restore=16500, currency=None, display_currency='USD', tld='tech',
                        markup=decimal.Decimal("1.25"))
        )),
        ('design', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(8194, transfer=8194, restore=20160, currency=None, display_currency='USD', tld='design',
                        markup=decimal.Decimal("1.2"))
        )),
        ('xyz', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(2502, transfer=2502, restore=18000, currency=None, display_currency='USD', tld='xyz',
                        markup=decimal.Decimal("1.5"))
        )),
        ('monster', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(2554, transfer=2554, restore=16800, currency=None, display_currency='USD', tld='monster',
                        markup=decimal.Decimal("1.4"))
        )),
        ('ink', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(4709, transfer=4709, restore=12960, currency=None, display_currency='USD', tld='ink',
                        markup=decimal.Decimal("1.2"))
        )),
        ('wiki', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(4709, transfer=4709, restore=12960, currency=None, display_currency='USD', tld='wiki',
                        markup=decimal.Decimal("1.2"))
        )),
        ('de', DomainInfo(
            DomainInfo.REGISTRY_DENIC,
            MarkupPrice(1596, transfer=1260, restore=5250, currency=None, display_currency='EUR', tld='de',
                        markup=decimal.Decimal("1.75"))
        )),
        ('be', DomainInfo(
            DomainInfo.REGISTRY_DNSBELGIUM,
            MarkupPrice(2694, transfer=2694, restore=6480, currency=None, display_currency='EUR', tld='be',
                        markup=decimal.Decimal("1.35"))
        )),
        ('space', DomainInfo(
            DomainInfo.REGISTRY_RADIX,
            MarkupPrice(3893, transfer=3893, restore=13500, currency=None, display_currency='USD', tld='space',
                        markup=decimal.Decimal("1.25"))
        )),
        ('fi', DomainInfo(
            DomainInfo.REGISTRY_TRAFICOM,
            SimplePrice(1499, transfer=1499, restore=1499, periods=map(lambda i: apps.epp_api.Period(
                unit=0,
                value=i
            ), range(1, 6)))
        )),
        ('ms', DomainInfo(
            DomainInfo.REGISTRY_MNI,
            MarkupPrice(4663, transfer=4663, restore=3125, currency=None, periods=map(lambda i: apps.epp_api.Period(
                unit=0,
                value=i
            ), range(1, 6)), display_currency='USD', tld='ms', markup=decimal.Decimal("1.25"))
        )),
        ('cymru', DomainInfo(
            DomainInfo.REGISTRY_NOMINET_GTLD,
            MarkupPrice(2167, transfer=2167, restore=2688, currency=None, display_currency='GBP', tld='cymru',
                        markup=decimal.Decimal("1.4"))
        )),
        ('wales', DomainInfo(
            DomainInfo.REGISTRY_NOMINET_GTLD,
            MarkupPrice(2167, transfer=2167, restore=2688, currency=None, display_currency='GBP', tld='wales',
                        markup=decimal.Decimal("1.4"))
        )),
        ('moe', DomainInfo(
            DomainInfo.REGISTRY_INTERLINK,
            MarkupPrice(3120, transfer=3120, restore=14040, currency=None, display_currency='USD', tld='moe',
                        markup=decimal.Decimal("1.3"))
        )),
        ('earth', DomainInfo(
            DomainInfo.REGISTRY_INTERLINK,
            MarkupPrice(4056, transfer=4056, restore=17160, currency=None, display_currency='USD', tld='earth',
                        markup=decimal.Decimal("1.3"))
        )),
        ('eu', DomainInfo(
            DomainInfo.REGISTRY_EURID,
            MarkupPrice(1728, transfer=1728, restore=2880, currency=None, display_currency='EUR', tld='eu',
                        markup=decimal.Decimal("1.6"))
        )),
        ('soy', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(4478, transfer=4478, restore=21600, currency=None, display_currency='USD', tld='soy',
                        markup=decimal.Decimal("1.2"))
        )),
        ('how', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(4954, transfer=4954, restore=21600, currency=None, display_currency='USD', tld='how',
                        markup=decimal.Decimal("1.2"))
        )),
        ('page', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2436, transfer=2436, restore=26100, currency=None, display_currency='USD', tld='page',
                        markup=decimal.Decimal("1.45"))
        )),
        ('dev', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2940, transfer=2940, restore=25200, currency=None, display_currency='USD', tld='dev',
                        markup=decimal.Decimal("1.4")),
            notice=".dev is a HSTS preload zone, meaning you'll need to deploy HTTPS on any website hosted on a "
                   ".dev domain."
        )),
        ('app', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(3198, transfer=3198, restore=23400, currency=None, display_currency='USD', tld='app',
                        markup=decimal.Decimal("1.3")),
            notice=".app is a HSTS preload zone, meaning you'll need to deploy HTTPS on any website hosted on a "
                   ".app domain."
        )),
        ('new', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(84960, transfer=84960, restore=21600, currency=None, display_currency='USD', tld='new',
                        markup=decimal.Decimal("1.2")),
            notice=".new domains must allow a user to create something, without further navigation, within 100 days "
                   "of being purchased. .new is a HSTS preload zone, meaning you'll need to deploy HTTPS on any "
                   "website hosted on a .new domain."
        )),
        ('tv', DomainInfo(
            DomainInfo.REGISTRY_GODADDY_CCTLD,
            MarkupPrice(3250, transfer=3250, restore=5200, currency='USD', tld='tv', markup=decimal.Decimal("1.3"), phase="open")
        )),
        ('cc', DomainInfo(DomainInfo.REGISTRY_VERISIGN, SimplePrice(1299, transfer=1299, restore=6500))),
        ('icu', DomainInfo(
            DomainInfo.REGISTRY_SHORTDOT,
            MarkupPrice(1795, transfer=1795, restore=26520, currency=None, display_currency='USD', tld='icu',
                        markup=decimal.Decimal("1.7"))
        )),
        ('info', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(2874, transfer=2874, restore=12600, currency=None, display_currency='USD', tld='info',
                        markup=decimal.Decimal("1.4"))
        )),
        ('pet', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(3097, transfer=3097, restore=12150, currency=None, display_currency='USD', tld='pet',
                        markup=decimal.Decimal("1.35"))
        )),
        ('pink', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(3192, transfer=3192, restore=117, currency=None, display_currency='USD', tld='pink',
                        markup=decimal.Decimal("1.30"))
        )),
        ('online', DomainInfo(
            DomainInfo.REGISTRY_RADIX,
            MarkupPrice(6178, transfer=6178, restore=15840, currency=None, display_currency='USD', tld='online',
                        markup=decimal.Decimal("1.2"))
        )),
        ('wang', DomainInfo(
            DomainInfo.REGISTRY_RADIX,
            MarkupPrice(2196, transfer=2196, restore=16200, currency=None, display_currency='USD', tld='wang',
                        markup=decimal.Decimal("1.5"))
        )),
        ('store', DomainInfo(
            DomainInfo.REGISTRY_RADIX,
            MarkupPrice(9907, transfer=9907, restore=21600, currency=None, display_currency='USD', tld='store',
                        markup=decimal.Decimal("1.2"))
        )),
        ('fun', DomainInfo(
            DomainInfo.REGISTRY_RADIX,
            MarkupPrice(4072, transfer=4072, restore=18720, currency=None, display_currency='USD', tld='fun',
                        markup=decimal.Decimal("1.3"))
        )),
        ('shop', DomainInfo(
            DomainInfo.REGISTRY_GMO,
            MarkupPrice(5904, transfer=5904, restore=23040, currency=None, display_currency='USD', tld='shop',
                        markup=decimal.Decimal("1.2"))
        )),
        ('buzz', DomainInfo(
            DomainInfo.REGISTRY_DOT_STRATEGY,
            MarkupPrice(5472, transfer=5472, restore=12960, currency=None, display_currency='USD', tld='buzz',
                        markup=decimal.Decimal("1.2"))
        )),
        ('mobi', DomainInfo(
            DomainInfo.REGISTRY_MTLD,
            MarkupPrice(3234, transfer=3234, restore=14040, currency=None, display_currency='USD', tld='mobi',
                        markup=decimal.Decimal("1.3"))
        )),
        ('pro', DomainInfo(
            DomainInfo.REGISTRY_MTLD,
            MarkupPrice(3069, transfer=3069, restore=15120, currency=None, display_currency='USD', tld='pro',
                        markup=decimal.Decimal("1.4"))
        )),
        ('life', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5230, transfer=5230, restore=12960, currency=None, display_currency='USD', tld='life',
                        markup=decimal.Decimal("1.2"))
        )),
        ('business', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3526, transfer=3526, restore=14040, currency=None, display_currency='USD', tld='business',
                        markup=decimal.Decimal("1.3"))
        )),
        ('pizza', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(9363, transfer=9363, restore=12960, currency=None, display_currency='USD', tld='pizza',
                        markup=decimal.Decimal("1.2"))
        )),
        ('systems', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='systems',
                        markup=decimal.Decimal("1.3"))
        )),
        ('guide', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5252, transfer=5252, restore=12960, currency=None, display_currency='USD', tld='guide',
                        markup=decimal.Decimal("1.2"))
        )),
        ('email', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='email',
                        markup=decimal.Decimal("1.3"))
        )),
        ('academy', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='academy',
                        markup=decimal.Decimal("1.2"))
        )),
        ('live', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(4240, transfer=4240, restore=14040, currency=None, display_currency='USD', tld='live',
                        markup=decimal.Decimal("1.3"))
        )),
        ('studio', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(4240, transfer=4240, restore=14040, currency=None, display_currency='USD', tld='studio',
                        markup=decimal.Decimal("1.3"))
        )),
        ('rocks', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(2513, transfer=2513, restore=15120, currency=None, display_currency='USD', tld='rocks',
                        markup=decimal.Decimal("1.4"))
        )),
        ('accountants', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(15682, transfer=15682, restore=12960, currency=None, display_currency='USD', tld='accountants',
                        markup=decimal.Decimal("1.2"))
        )),
        ('actor', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(6561, transfer=6561, restore=12960, currency=None, display_currency='USD', tld='actor',
                        markup=decimal.Decimal("1.2"))
        )),
        ('agency', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=12960, currency=None, display_currency='USD', tld='agency',
                        markup=decimal.Decimal("1.2"))
        )),
        ('apartments', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='apartments',
                        markup=decimal.Decimal("1.2"))
        )),
        ('associates', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='associates',
                        markup=decimal.Decimal("1.2"))
        )),
        ('auction', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='auction',
                        markup=decimal.Decimal("1.2"))
        )),
        ('band', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(4240, transfer=4240, restore=14040, currency=None, display_currency='USD', tld='band',
                        markup=decimal.Decimal("1.3"))
        )),
        ('bargains', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5230, transfer=5230, restore=12960, currency=None, display_currency='USD', tld='bargains',
                        markup=decimal.Decimal("1.2"))
        )),
        ('bike', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='bike',
                        markup=decimal.Decimal("1.2"))
        )),
        ('bingo', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='bingo',
                        markup=decimal.Decimal("1.2"))
        )),
        ('botique', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='academy',
                        markup=decimal.Decimal("1.2"))
        )),
        ('build', DomainInfo(
            DomainInfo.REGISTRY_PLAN_BEE,
            MarkupPrice(10080, transfer=10080, restore=18000, currency=None, display_currency='USD', tld='build',
                        markup=decimal.Decimal("1.2"))
        )),
        ('builders', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='builders',
                        markup=decimal.Decimal("1.2"))
        )),
        ('cab', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='cab',
                        markup=decimal.Decimal("1.2"))
        )),
        ('cafe', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='cafe',
                        markup=decimal.Decimal("1.2"))
        )),
        ('camp', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8935, transfer=8935, restore=12960, currency=None, display_currency='USD', tld='camp',
                        markup=decimal.Decimal("1.2"))
        )),
        ('capital', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='capital',
                        markup=decimal.Decimal("1.2"))
        )),
        ('cards', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(4488, transfer=4488, restore=12960, currency=None, display_currency='USD', tld='cards',
                        markup=decimal.Decimal("1.2"))
        )),
        ('care', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(4488, transfer=4488, restore=12960, currency=None, display_currency='USD', tld='care',
                        markup=decimal.Decimal("1.2"))
        )),
        ('careers', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='careers',
                        markup=decimal.Decimal("1.2"))
        )),
        ('cash', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='cash',
                        markup=decimal.Decimal("1.2"))
        )),
        ('casino', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(21600, transfer=21600, restore=12960, currency=None, display_currency='USD', tld='casino',
                        markup=decimal.Decimal("1.2"))
        )),
        ('catering', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='catering',
                        markup=decimal.Decimal("1.2"))
        )),
        ('center', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='center',
                        markup=decimal.Decimal("1.3"))
        )),
        ('charity', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='charity',
                        markup=decimal.Decimal("1.2"))
        )),
        ('chat', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='chat',
                        markup=decimal.Decimal("1.2"))
        )),
        ('cheap', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5230, transfer=5230, restore=12960, currency=None, display_currency='USD', tld='cheap',
                        markup=decimal.Decimal("1.2"))
        )),
        ('church', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='church',
                        markup=decimal.Decimal("1.2"))
        )),
        ('city', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='city',
                        markup=decimal.Decimal("1.3"))
        )),
        ('cash', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='cash',
                        markup=decimal.Decimal("1.2"))
        )),
        ('claims', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8688, transfer=8688, restore=12960, currency=None, display_currency='USD', tld='claims',
                        markup=decimal.Decimal("1.2"))
        )),
        ('cleaning', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='cleaning',
                        markup=decimal.Decimal("1.2"))
        )),
        ('clinic', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='clinic',
                        markup=decimal.Decimal("1.2"))
        )),
        ('clothing', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='clothing',
                        markup=decimal.Decimal("1.2"))
        )),
        ('coach', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='coach',
                        markup=decimal.Decimal("1.2"))
        )),
        ('codes', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='codes',
                        markup=decimal.Decimal("1.2"))
        )),
        ('coffee', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='coffee',
                        markup=decimal.Decimal("1.2"))
        )),
        ('community', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='community',
                        markup=decimal.Decimal("1.2"))
        )),
        ('company', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3526, transfer=3526, restore=14040, currency=None, display_currency='USD', tld='company',
                        markup=decimal.Decimal("1.3"))
        )),
        ('computer', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='computer',
                        markup=decimal.Decimal("1.2"))
        )),
        ('condos', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8688, transfer=8688, restore=12960, currency=None, display_currency='USD', tld='condos',
                        markup=decimal.Decimal("1.2"))
        )),
        ('construction', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='construction',
                        markup=decimal.Decimal("1.2"))
        )),
        ('consulting', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='consulting',
                        markup=decimal.Decimal("1.2"))
        )),
        ('contact', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(2376, transfer=2376, restore=16200, currency=None, display_currency='USD', tld='contact',
                        markup=decimal.Decimal("1.5"))
        )),
        ('contractors', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='contractors',
                        markup=decimal.Decimal("1.2"))
        )),
        ('cool', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='cool',
                        markup=decimal.Decimal("1.2"))
        )),
        ('coupons', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8688, transfer=8688, restore=12960, currency=None, display_currency='USD', tld='coupons',
                        markup=decimal.Decimal("1.2"))
        )),
        ('credit', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(15682, transfer=15682, restore=12960, currency=None, display_currency='USD', tld='credit',
                        markup=decimal.Decimal("1.2"))
        )),
        ('creditcard', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(21600, transfer=21600, restore=12960, currency=None, display_currency='USD', tld='creditcard',
                        markup=decimal.Decimal("1.2"))
        )),
        ('cruises', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8688, transfer=8688, restore=12960, currency=None, display_currency='USD', tld='cruises',
                        markup=decimal.Decimal("1.2"))
        )),
        ('dance', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(4077, transfer=4077, restore=13500, currency=None, display_currency='USD', tld='dance',
                        markup=decimal.Decimal("1.25"))
        )),
        ('dating', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='dating',
                        markup=decimal.Decimal("1.2"))
        )),
        ('deals', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='deals',
                        markup=decimal.Decimal("1.2"))
        )),
        ('degree', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(7600, transfer=7600, restore=12960, currency=None, display_currency='USD', tld='degree',
                        markup=decimal.Decimal("1.2"))
        )),
        ('delivery', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='delivery',
                        markup=decimal.Decimal("1.2"))
        )),
        ('democrat', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='democrat',
                        markup=decimal.Decimal("1.2"))
        )),
        ('dental', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='dental',
                        markup=decimal.Decimal("1.2"))
        )),
        ('dentist', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8774, transfer=8774, restore=12960, currency=None, display_currency='USD', tld='dentist',
                        markup=decimal.Decimal("1.2"))
        )),
        ('diamonds', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='diamonds',
                        markup=decimal.Decimal("1.2"))
        )),
        ('digital', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='digital',
                        markup=decimal.Decimal("1.2"))
        )),
        ('direct', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='direct',
                        markup=decimal.Decimal("1.2"))
        )),
        ('directory', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='directory',
                        markup=decimal.Decimal("1.3"))
        )),
        ('discount', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='discount',
                        markup=decimal.Decimal("1.2"))
        )),
        ('doctor', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(15682, transfer=15682, restore=12960, currency=None, display_currency='USD', tld='doctor',
                        markup=decimal.Decimal("1.2"))
        )),
        ('dog', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='dog',
                        markup=decimal.Decimal("1.2"))
        )),
        ('domains', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='domains',
                        markup=decimal.Decimal("1.2"))
        )),
        ('education', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='education',
                        markup=decimal.Decimal("1.3"))
        )),
        ('energy', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(15682, transfer=15682, restore=12960, currency=None, display_currency='USD', tld='energy',
                        markup=decimal.Decimal("1.2"))
        )),
        ('engineer', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='engineer',
                        markup=decimal.Decimal("1.2"))
        )),
        ('engineering', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='engineering',
                        markup=decimal.Decimal("1.2"))
        )),
        ('enterprises', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='enterprises',
                        markup=decimal.Decimal("1.3"))
        )),
        ('equipment', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='equipment',
                        markup=decimal.Decimal("1.3"))
        )),
        ('estate', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='estate',
                        markup=decimal.Decimal("1.2"))
        )),
        ('events', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='events',
                        markup=decimal.Decimal("1.2"))
        )),
        ('exchange', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='exchange',
                        markup=decimal.Decimal("1.2"))
        )),
        ('expert', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='expert',
                        markup=decimal.Decimal("1.2"))
        )),
        ('exposed', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='exposed',
                        markup=decimal.Decimal("1.3"))
        )),
        ('express', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='express',
                        markup=decimal.Decimal("1.2"))
        )),
        ('fail', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='fail',
                        markup=decimal.Decimal("1.2"))
        )),
        ('family', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='family',
                        markup=decimal.Decimal("1.2"))
        )),
        ('farm', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='farm',
                        markup=decimal.Decimal("1.2"))
        )),
        ('finance', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='finance',
                        markup=decimal.Decimal("1.2"))
        )),
        ('financial', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='financial',
                        markup=decimal.Decimal("1.2"))
        )),
        ('fish', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='fish',
                        markup=decimal.Decimal("1.2"))
        )),
        ('fitness', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='fitness',
                        markup=decimal.Decimal("1.2"))
        )),
        ('flights', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='flights',
                        markup=decimal.Decimal("1.2"))
        )),
        ('florist', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='florist',
                        markup=decimal.Decimal("1.2"))
        )),
        ('football', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='football',
                        markup=decimal.Decimal("1.3"))
        )),
        ('forsale', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='forsale',
                        markup=decimal.Decimal("1.2"))
        )),
        ('foundation', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='foundation',
                        markup=decimal.Decimal("1.2"))
        )),
        ('fund', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8688, transfer=8688, restore=12960, currency=None, display_currency='USD', tld='fund',
                        markup=decimal.Decimal("1.2"))
        )),
        ('furniture', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='furniture',
                        markup=decimal.Decimal("1.2"))
        )),
        ('futbol', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(2693, transfer=2693, restore=16200, currency=None, display_currency='USD', tld='futbol',
                        markup=decimal.Decimal("1.5"))
        )),
        ('fyi', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='fyi',
                        markup=decimal.Decimal("1.3"))
        )),
        ('gallery', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='gallery',
                        markup=decimal.Decimal("1.3"))
        )),
        ('games', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3529, transfer=3529, restore=14040, currency=None, display_currency='USD', tld='games',
                        markup=decimal.Decimal("1.3"))
        )),
        ('gifts', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='gifts',
                        markup=decimal.Decimal("1.2"))
        )),
        ('gives', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='gives',
                        markup=decimal.Decimal("1.2"))
        )),
        ('glass', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='glass',
                        markup=decimal.Decimal("1.2"))
        )),
        ('gmbh', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='gmbh',
                        markup=decimal.Decimal("1.2")),
            notice="This TLD is restricted to entities registered as a GmbH"
        )),
        ('gold', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(15682, transfer=15682, restore=12960, currency=None, display_currency='USD', tld='gold',
                        markup=decimal.Decimal("1.2"))
        )),
        ('golf', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='golf',
                        markup=decimal.Decimal("1.2"))
        )),
        ('graphics', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='graphics',
                        markup=decimal.Decimal("1.3"))
        )),
        ('gratis', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=12960, currency=None, display_currency='USD', tld='gratis',
                        markup=decimal.Decimal("1.3"))
        )),
        ('gripe', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='gripe',
                        markup=decimal.Decimal("1.2"))
        )),
        ('group', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3526, transfer=3526, restore=14040, currency=None, display_currency='USD', tld='group',
                        markup=decimal.Decimal("1.3"))
        )),
        ('guide', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='guide',
                        markup=decimal.Decimal("1.2"))
        )),
        ('guru', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='guru',
                        markup=decimal.Decimal("1.2"))
        )),
        ('haus', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='haus',
                        markup=decimal.Decimal("1.2"))
        )),
        ('healthcare', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='healthcare',
                        markup=decimal.Decimal("1.2"))
        )),
        ('hockey', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='hockey',
                        markup=decimal.Decimal("1.2"))
        )),
        ('holdings', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8688, transfer=8688, restore=12960, currency=None, display_currency='USD', tld='holdings',
                        markup=decimal.Decimal("1.2"))
        )),
        ('holiday', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='holiday',
                        markup=decimal.Decimal("1.2"))
        )),
        ('hospital', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8688, transfer=8688, restore=12960, currency=None, display_currency='USD', tld='hospital',
                        markup=decimal.Decimal("1.2"))
        )),
        ('house', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='house',
                        markup=decimal.Decimal("1.2"))
        )),
        ('immo', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='immo',
                        markup=decimal.Decimal("1.2"))
        )),
        ('immobilien', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='immobilien',
                        markup=decimal.Decimal("1.2"))
        )),
        ('industries', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='industries',
                        markup=decimal.Decimal("1.2"))
        )),
        ('insitute', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='institute',
                        markup=decimal.Decimal("1.3"))
        )),
        ('insure', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='insure',
                        markup=decimal.Decimal("1.2"))
        )),
        ('international', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='international',
                        markup=decimal.Decimal("1.3"))
        )),
        ('investments', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(15682, transfer=15682, restore=12960, currency=None, display_currency='USD', tld='investments',
                        markup=decimal.Decimal("1.2"))
        )),
        ('irish', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(6120, transfer=6120, restore=12960, currency=None, display_currency='USD', tld='irish',
                        markup=decimal.Decimal("1.2"))
        )),
        ('jetzt', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3742, transfer=3742, restore=14040, currency=None, display_currency='USD', tld='jetzt',
                        markup=decimal.Decimal("1.3"))
        )),
        ('jewelry', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='jewelry',
                        markup=decimal.Decimal("1.2"))
        )),
        ('kaufen', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='kaufen',
                        markup=decimal.Decimal("1.2"))
        )),
        ('kitchen', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='kitchen',
                        markup=decimal.Decimal("1.2"))
        )),
        ('land', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='land',
                        markup=decimal.Decimal("1.2"))
        )),
        ('lawyer', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8774, transfer=8774, restore=12960, currency=None, display_currency='USD', tld='lawyer',
                        markup=decimal.Decimal("1.2"))
        )),
        ('lease', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8688, transfer=8688, restore=12960, currency=None, display_currency='USD', tld='lease',
                        markup=decimal.Decimal("1.2"))
        )),
        ('legal', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='legal',
                        markup=decimal.Decimal("1.2"))
        )),
        ('life', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5230, transfer=5230, restore=12960, currency=None, display_currency='USD', tld='life',
                        markup=decimal.Decimal("1.2"))
        )),
        ('lighting', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='lighting',
                        markup=decimal.Decimal("1.3"))
        )),
        ('limited', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='limited',
                        markup=decimal.Decimal("1.2"))
        )),
        ('limo', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8935, transfer=8935, restore=12960, currency=None, display_currency='USD', tld='limo',
                        markup=decimal.Decimal("1.2"))
        )),
        ('loans', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(15682, transfer=15682, restore=12960, currency=None, display_currency='USD', tld='loans',
                        markup=decimal.Decimal("1.2"))
        )),
        ('ltd', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='ltd',
                        markup=decimal.Decimal("1.3"))
        )),
        ('maison', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='maison',
                        markup=decimal.Decimal("1.2"))
        )),
        ('management', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='management',
                        markup=decimal.Decimal("1.3"))
        )),
        ('market', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5230, transfer=5230, restore=12960, currency=None, display_currency='USD', tld='market',
                        markup=decimal.Decimal("1.2"))
        )),
        ('marketing', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='marketing',
                        markup=decimal.Decimal("1.2"))
        )),
        ('mba', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='mba',
                        markup=decimal.Decimal("1.2"))
        )),
        ('media', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='media',
                        markup=decimal.Decimal("1.2"))
        )),
        ('memorial', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='memorial',
                        markup=decimal.Decimal("1.2"))
        )),
        ('moda', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='moda',
                        markup=decimal.Decimal("1.2"))
        )),
        ('money', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='money',
                        markup=decimal.Decimal("1.2"))
        )),
        ('mortgage', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(7600, transfer=7600, restore=12960, currency=None, display_currency='USD', tld='mortgage',
                        markup=decimal.Decimal("1.2"))
        )),
        ('movie', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(46008, transfer=46080, restore=12960, currency=None, display_currency='USD', tld='movie',
                        markup=decimal.Decimal("1.2"))
        )),
        ('network', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='network',
                        markup=decimal.Decimal("1.3"))
        )),
        ('news', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(4240, transfer=4240, restore=14040, currency=None, display_currency='USD', tld='news',
                        markup=decimal.Decimal("1.3"))
        )),
        ('ninja', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3529, transfer=3529, restore=14040, currency=None, display_currency='USD', tld='ninja',
                        markup=decimal.Decimal("1.3"))
        )),
        ('observer', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(2256, transfer=2256, restore=48000, currency=None, display_currency='USD', tld='observer',
                        markup=decimal.Decimal("1.6"))
        )),
        ('partners', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='partners',
                        markup=decimal.Decimal("1.2"))
        )),
        ('parts', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='parts',
                        markup=decimal.Decimal("1.2"))
        )),
        ('photography', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='photography',
                        markup=decimal.Decimal("1.3"))
        )),
        ('photos', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='photos',
                        markup=decimal.Decimal("1.3"))
        )),
        ('pictures', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(2407, transfer=2407, restore=16200, currency=None, display_currency='USD', tld='pictures',
                        markup=decimal.Decimal("1.5"))
        )),
        ('place', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(4982, transfer=4982, restore=12960, currency=None, display_currency='USD', tld='place',
                        markup=decimal.Decimal("1.2"))
        )),
        ('plumbing', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='plumbing',
                        markup=decimal.Decimal("1.2"))
        )),
        ('plus', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='plus',
                        markup=decimal.Decimal("1.2"))
        )),
        ('productions', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='productions',
                        markup=decimal.Decimal("1.2"))
        )),
        ('properties', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='properties',
                        markup=decimal.Decimal("1.2"))
        )),
        ('pub', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='pub',
                        markup=decimal.Decimal("1.2"))
        )),
        ('recipies', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8688, transfer=8688, restore=12960, currency=None, display_currency='USD', tld='recipies',
                        markup=decimal.Decimal("1.2"))
        )),
        ('rehab', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='rehab',
                        markup=decimal.Decimal("1.2"))
        )),
        ('reise', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(15682, transfer=15682, restore=12960, currency=None, display_currency='USD', tld='reise',
                        markup=decimal.Decimal("1.2"))
        )),
        ('reisen', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='reisen',
                        markup=decimal.Decimal("1.3"))
        )),
        ('rentals', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='rentals',
                        markup=decimal.Decimal("1.2"))
        )),
        ('repair', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='repair',
                        markup=decimal.Decimal("1.2"))
        )),
        ('report', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='report',
                        markup=decimal.Decimal("1.3"))
        )),
        ('republican', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='republican',
                        markup=decimal.Decimal("1.2"))
        )),
        ('restaurant', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='restaurance',
                        markup=decimal.Decimal("1.2"))
        )),
        ('reviews', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(4077, transfer=4077, restore=13500, currency=None, display_currency='USD', tld='reviews',
                        markup=decimal.Decimal("1.25"))
        )),
        ('rip', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3529, transfer=3529, restore=14040, currency=None, display_currency='USD', tld='rip',
                        markup=decimal.Decimal("1.3"))
        )),
        ('run', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='run',
                        markup=decimal.Decimal("1.3"))
        )),
        ('sale', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='sale',
                        markup=decimal.Decimal("1.2"))
        )),
        ('salon', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8935, transfer=8935, restore=12960, currency=None, display_currency='USD', tld='salon',
                        markup=decimal.Decimal("1.2"))
        )),
        ('sarl', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='sarl',
                        markup=decimal.Decimal("1.2"))
        )),
        ('school', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='school',
                        markup=decimal.Decimal("1.2"))
        )),
        ('schule', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='schule',
                        markup=decimal.Decimal("1.3"))
        )),
        ('services', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5230, transfer=5230, restore=12960, currency=None, display_currency='USD', tld='services',
                        markup=decimal.Decimal("1.2"))
        )),
        ('sexy', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5160, transfer=5160, restore=10800, currency=None, display_currency='USD', tld='sexy',
                        markup=decimal.Decimal("1.2"))
        )),
        ('shoes', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='shoes',
                        markup=decimal.Decimal("1.2"))
        )),
        ('shopping', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5230, transfer=5230, restore=12960, currency=None, display_currency='USD', tld='shopping',
                        markup=decimal.Decimal("1.2"))
        )),
        ('show', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='show',
                        markup=decimal.Decimal("1.2"))
        )),
        ('singles', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5230, transfer=5230, restore=12960, currency=None, display_currency='USD', tld='singles',
                        markup=decimal.Decimal("1.2"))
        )),
        ('soccer', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='soccer',
                        markup=decimal.Decimal("1.3"))
        )),
        ('social', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='social',
                        markup=decimal.Decimal("1.2"))
        )),
        ('software', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='software',
                        markup=decimal.Decimal("1.2"))
        )),
        ('solar', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='solar',
                        markup=decimal.Decimal("1.2"))
        )),
        ('solutions', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='solutions',
                        markup=decimal.Decimal("1.3"))
        )),
        ('style', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='style',
                        markup=decimal.Decimal("1.2"))
        )),
        ('supplies', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='supplies',
                        markup=decimal.Decimal("1.3"))
        )),
        ('supply', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='supply',
                        markup=decimal.Decimal("1.3"))
        )),
        ('support', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='support',
                        markup=decimal.Decimal("1.3"))
        )),
        ('surgery', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='surgery',
                        markup=decimal.Decimal("1.2"))
        )),
        ('tax', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='tax',
                        markup=decimal.Decimal("1.2"))
        )),
        ('taxi', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='taxi',
                        markup=decimal.Decimal("1.2"))
        )),
        ('team', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='team',
                        markup=decimal.Decimal("1.2"))
        )),
        ('technology', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='technology',
                        markup=decimal.Decimal("1.3"))
        )),
        ('tennis', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='tennis',
                        markup=decimal.Decimal("1.2"))
        )),
        ('theatre', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(108000, transfer=108000, restore=7200, currency=None, display_currency='USD', tld='theatre',
                        markup=decimal.Decimal("1.2"))
        )),
        ('tienda', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='tienda',
                        markup=decimal.Decimal("1.2"))
        )),
        ('tips', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='tips',
                        markup=decimal.Decimal("1.3"))
        )),
        ('tires', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(15682, transfer=15682, restore=12960, currency=None, display_currency='USD', tld='tires',
                        markup=decimal.Decimal("1.2"))
        )),
        ('today', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3794, transfer=3794, restore=14040, currency=None, display_currency='USD', tld='today',
                        markup=decimal.Decimal("1.3"))
        )),
        ('tools', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='tools',
                        markup=decimal.Decimal("1.2"))
        )),
        ('tours', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='tours',
                        markup=decimal.Decimal("1.2"))
        )),
        ('town', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='town',
                        markup=decimal.Decimal("1.2"))
        )),
        ('toys', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='toys',
                        markup=decimal.Decimal("1.2"))
        )),
        ('training', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='training',
                        markup=decimal.Decimal("1.2"))
        )),
        ('travel', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(15552, transfer=15552, restore=12960, currency=None, display_currency='USD', tld='travel',
                        markup=decimal.Decimal("1.2"))
        )),
        ('university', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='university',
                        markup=decimal.Decimal("1.2"))
        )),
        ('vacations', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='vacations',
                        markup=decimal.Decimal("1.2"))
        )),
        ('ventures', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='ventures',
                        markup=decimal.Decimal("1.2"))
        )),
        ('vet', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='vet',
                        markup=decimal.Decimal("1.2"))
        )),
        ('viajes', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8688, transfer=8688, restore=12960, currency=None, display_currency='USD', tld='viajes',
                        markup=decimal.Decimal("1.2"))
        )),
        ('video', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(4240, transfer=4240, restore=14040, currency=None, display_currency='USD', tld='video',
                        markup=decimal.Decimal("1.2"))
        )),
        ('villas', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='villas',
                        markup=decimal.Decimal("1.2"))
        )),
        ('vin', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='vin',
                        markup=decimal.Decimal("1.2"))
        )),
        ('vision', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='vision',
                        markup=decimal.Decimal("1.2"))
        )),
        ('voyage', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='voyage',
                        markup=decimal.Decimal("1.2"))
        )),
        ('watch', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='watch',
                        markup=decimal.Decimal("1.2"))
        )),
        ('wine', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(8811, transfer=8811, restore=12960, currency=None, display_currency='USD', tld='wine',
                        markup=decimal.Decimal("1.2"))
        )),
        ('works', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='works',
                        markup=decimal.Decimal("1.2"))
        )),
        ('world', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='world',
                        markup=decimal.Decimal("1.2"))
        )),
        ('wtf', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='wtf',
                        markup=decimal.Decimal("1.2"))
        )),
        ('zone', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(5352, transfer=5352, restore=12960, currency=None, display_currency='USD', tld='zone',
                        markup=decimal.Decimal("1.2"))
        )),
        ('fr', DomainInfo(
            DomainInfo.REGISTRY_AFNIC,
            MarkupPrice(2055, transfer=2055, restore=3000, currency=None, display_currency='EUR', tld='fr',
                        markup=decimal.Decimal("1.5"))
        )),
        ('wf', DomainInfo(
            DomainInfo.REGISTRY_AFNIC,
            MarkupPrice(2055, transfer=2055, restore=3000, currency=None, display_currency='EUR', tld='wf',
                        markup=decimal.Decimal("1.5"))
        )),
        ('tf', DomainInfo(
            DomainInfo.REGISTRY_AFNIC,
            MarkupPrice(2055, transfer=2055, restore=3000, currency=None, display_currency='EUR', tld='tf',
                        markup=decimal.Decimal("1.5"))
        )),
        ('pm', DomainInfo(
            DomainInfo.REGISTRY_AFNIC,
            MarkupPrice(2055, transfer=2055, restore=3000, currency=None, display_currency='EUR', tld='pm',
                        markup=decimal.Decimal("1.5"))
        )),
        ('yt', DomainInfo(
            DomainInfo.REGISTRY_AFNIC,
            MarkupPrice(2055, transfer=2055, restore=3000, currency=None, display_currency='EUR', tld='yt',
                        markup=decimal.Decimal("1.5"))
        )),
        ('re', DomainInfo(
            DomainInfo.REGISTRY_AFNIC,
            MarkupPrice(2618, transfer=2618, restore=2800, currency=None, display_currency='EUR', tld='re',
                        markup=decimal.Decimal("1.4"))
        )),
        ('blog', DomainInfo(
            DomainInfo.REGISTRY_WHOIS_THERE,
            MarkupPrice(4968, transfer=4968, restore=12960, currency=None, display_currency='USD', tld='blog',
                        markup=decimal.Decimal("1.2"))
        )),
        ('cat', DomainInfo(
            DomainInfo.REGISTRY_CORE,
            MarkupPrice(4680, transfer=4680, currency=None, display_currency='USD', tld='cat',
                        markup=decimal.Decimal("1.2"))
        )),
        ('club', DomainInfo(
            DomainInfo.REGISTRY_CLUB_DOMAINS,
            MarkupPrice(2611, transfer=2611, restore=15120, currency=None, display_currency='USD', tld='club',
                        markup=decimal.Decimal("1.4"))
        )),
        ('ag', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(9000, transfer=9000, restore=9000, currency=None, display_currency='USD', tld='ag',
                        markup=decimal.Decimal("1.2"))
        )),
        ('com.ag', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(6000, transfer=6000, restore=9000, currency=None, display_currency='USD', tld='com.ag',
                        markup=decimal.Decimal("1.2"))
        )),
        ('net.ag', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(6000, transfer=6000, restore=9000, currency=None, display_currency='USD', tld='net.ag',
                        markup=decimal.Decimal("1.2"))
        )),
        ('org.ag', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(6000, transfer=6000, restore=9000, currency=None, display_currency='USD', tld='org.ag',
                        markup=decimal.Decimal("1.2"))
        )),
        ('nom.ag', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(6000, transfer=6000, restore=9000, currency=None, display_currency='USD', tld='nom.ag',
                        markup=decimal.Decimal("1.2"))
        )),
        ('co.ag', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(6000, transfer=6000, restore=9000, currency=None, display_currency='USD', tld='co.ag',
                        markup=decimal.Decimal("1.2"))
        )),
        ('bz', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(2400, transfer=2400, restore=11250, currency=None, display_currency='USD', tld='bz',
                        markup=decimal.Decimal("1.5"))
        )),
        ('com.bz', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(4550, transfer=4550, restore=9750, currency=None, display_currency='USD', tld='com.bz',
                        markup=decimal.Decimal("1.3"))
        )),
        ('net.bz', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(4550, transfer=4550, restore=9750, currency=None, display_currency='USD', tld='net.bz',
                        markup=decimal.Decimal("1.3"))
        )),
        ('co.bz', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(4550, transfer=4550, restore=9750, currency=None, display_currency='USD', tld='co.bz',
                        markup=decimal.Decimal("1.3"))
        )),
        ('lc', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(2700, transfer=2700, restore=11250, currency=None, display_currency='USD', tld='lc',
                        markup=decimal.Decimal("1.5"))
        )),
        ('com.lc', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(1950, transfer=1950, restore=11250, currency=None, display_currency='USD', tld='com.lc',
                        markup=decimal.Decimal("1.5"))
        )),
        ('net.lc', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(1950, transfer=1950, restore=11250, currency=None, display_currency='USD', tld='net.lc',
                        markup=decimal.Decimal("1.5"))
        )),
        ('org.lc', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(1950, transfer=1950, restore=11250, currency=None, display_currency='USD', tld='org.lc',
                        markup=decimal.Decimal("1.5"))
        )),
        ('co.lc', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(1950, transfer=1950, restore=11250, currency=None, display_currency='USD', tld='co.lc',
                        markup=decimal.Decimal("1.5"))
        )),
        ('p.lc', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(1950, transfer=1950, restore=11250, currency=None, display_currency='USD', tld='p.lc',
                        markup=decimal.Decimal("1.5"))
        )),
        ('l.lc', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(1950, transfer=1950, restore=11250, currency=None, display_currency='USD', tld='l.lc',
                        markup=decimal.Decimal("1.5"))
        )),
        ('mn', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(4550, transfer=4550, restore=5200, currency=None, display_currency='USD', tld='mn',
                        markup=decimal.Decimal("1.3"))
        )),
        ('pr', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(120000, transfer=120000, restore=12000, currency=None, display_currency='USD', tld='pr',
                        markup=decimal.Decimal("1.2"))
        )),
        ('sc', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(9000, transfer=9000, restore=9000, currency=None, display_currency='USD', tld='sc',
                        markup=decimal.Decimal("1.2"))
        )),
        ('vc', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(3250, transfer=3250, restore=9750, currency=None, display_currency='USD', tld='vc',
                        markup=decimal.Decimal("1.3"))
        )),
        ('llc', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(4550, transfer=4550, restore=10800, currency=None, display_currency='USD', tld='llc',
                        markup=decimal.Decimal("1.2"))
        )),
        ('garden', DomainInfo(
            DomainInfo.REGISTRY_MINDS_MACHINES,
            MarkupPrice(4288, transfer=4288, restore=3125, currency=None, display_currency='USD', tld='garden',
                        markup=decimal.Decimal("1.25"))
        )),
        ('work', DomainInfo(
            DomainInfo.REGISTRY_MINDS_MACHINES,
            MarkupPrice(2062, transfer=2062, restore=19200, currency=None, display_currency='USD', tld='work',
                        markup=decimal.Decimal("1.6"))
        )),
        ('vip', DomainInfo(
            DomainInfo.REGISTRY_MINDS_MACHINES,
            MarkupPrice(6820, transfer=6820, restore=18000, currency=None, display_currency='USD', tld='vip',
                        markup=decimal.Decimal("1.5"))
        )),
        ('uk', DomainInfo(
            DomainInfo.REGISTRY_NOMINET, Nominet2021PromotionalPrice(917),
            transfer_instructions="Make sure to change the registrar tag to \"AS207960\" at your previous registrar."
        )),
        ('co.uk', DomainInfo(
            DomainInfo.REGISTRY_NOMINET, Nominet2021PromotionalPrice(917),
            transfer_instructions="Make sure to change the registrar tag to \"AS207960\" at your previous registrar."
        )),
        ('me.uk', DomainInfo(
            DomainInfo.REGISTRY_NOMINET, Nominet2021PromotionalPrice(917),
            notice="This TLD is restricted to natural persons.",
            transfer_instructions="Make sure to change the registrar tag to \"AS207960\" at your previous registrar."
        )),
        ('org.uk', DomainInfo(
            DomainInfo.REGISTRY_NOMINET, Nominet2021PromotionalPrice(917),
            transfer_instructions="Make sure to change the registrar tag to \"AS207960\" at your previous registrar."
        )),
        ('ltd.uk', DomainInfo(
            DomainInfo.REGISTRY_NOMINET_SPECIAL, SimplePrice(917),
            notice="This TLD is restricted to UK Limited Companies.",
            transfer_instructions="Make sure to change the registrar tag to \"AS207960\" at your previous registrar."
        )),
        ('plc.uk', DomainInfo(
            DomainInfo.REGISTRY_NOMINET_SPECIAL, SimplePrice(917),
            notice="This TLD is restricted to UK Public Limited Companies.",
            transfer_instructions="Make sure to change the registrar tag to \"AS207960\" at your previous registrar."
        )),
        ('net.uk', DomainInfo(
            DomainInfo.REGISTRY_NOMINET_SPECIAL, SimplePrice(917),
            notice="This TLD is restricted to businesses in the UK telecommunications sector.",
            transfer_instructions="Make sure to change the registrar tag to \"AS207960\" at your previous registrar."
        )),
        ('scot', DomainInfo(
            DomainInfo.REGISTRY_CORE,
            MarkupPrice(4752, transfer=4752, restore=18000, currency=None, display_currency='GBP', tld='scot',
                        markup=decimal.Decimal("1.2"))
        )),
        ('ca', DomainInfo(
            DomainInfo.REGISTRY_CIRA,
            MarkupPrice(2880, transfer=2880, restore=6400, currency=None, display_currency='CAD', tld='ca',
                        markup=decimal.Decimal("1.6")),
            notice="Registrants are required to meet CIRA's Canadian presence requirements"
        )),
        ('io', DomainInfo(
            DomainInfo.REGISTRY_ICB,
            MarkupPrice(6062, transfer=6062, restore=8942, currency=None, display_currency='USD', tld='io',
                        markup=decimal.Decimal("1.2"))
        )),
        ('ac', DomainInfo(
            DomainInfo.REGISTRY_ICB,
            MarkupPrice(6062, transfer=6062, restore=8942, currency=None, display_currency='USD', tld='ac',
                        markup=decimal.Decimal("1.2"))
        )),
        ('sh', DomainInfo(
            DomainInfo.REGISTRY_ICB,
            MarkupPrice(6062, transfer=6062, restore=8942, currency=None, display_currency='USD', tld='sh',
                        markup=decimal.Decimal("1.2"))
        )),
        ('co', DomainInfo(
            DomainInfo.REGISTRY_CO,
            MarkupPrice(4352, transfer=4352, restore=14040, currency=None, display_currency='USD', tld='co',
                        markup=decimal.Decimal("1.3"), periods=map(lambda i: apps.epp_api.Period(
                    unit=0,
                    value=i
                ), range(1, 6)))
        )),
        ('ooo', DomainInfo(
            DomainInfo.REGISTRY_INFIBEAM,
            MarkupPrice(4954, transfer=4953, restore=20160, currency=None, display_currency='USD', tld='ooo',
                        markup=decimal.Decimal("1.2"))
        )),
        ('ke', DomainInfo(
            DomainInfo.REGISTRY_KENIC,
            MarkupPrice(17136, transfer=4176, currency=None, display_currency='USD', tld='ke',
                        markup=decimal.Decimal("1.2"))
        )),
        ('al', DomainInfo(
            DomainInfo.REGISTRY_AKEP,
            MarkupPrice(9360, transfer=9360, currency=None, display_currency='USD', tld='al',
                        markup=decimal.Decimal("1.2"))
        )),
        ('am', DomainInfo(
            DomainInfo.REGISTRY_AMNIC,
            MarkupPrice(
                5760, transfer=5760, restore=5040, currency=None, display_currency='USD', tld='am',
                markup=decimal.Decimal("1.2"), periods=map(lambda i: apps.epp_api.Period(
                    unit=0,
                    value=i
                ), range(1, 6))
            )
        )),
        ('lol', DomainInfo(
            DomainInfo.REGISTRY_UNIREGISTRY,
            MarkupPrice(4982, transfer=4982, restore=12960, currency=None, display_currency='USD', tld='lol',
                        markup=decimal.Decimal("1.2"))
        )),
        ('af', DomainInfo(
            DomainInfo.REGISTRY_AFMOF,
            MarkupPrice(
                14400, transfer=5040, restore=3600, currency=None, display_currency='USD', tld='af',
                markup=decimal.Decimal("1.2"), periods=map(lambda i: apps.epp_api.Period(
                    unit=0,
                    value=i
                ), range(1, 6))
            )
        )),
        ('ht', DomainInfo(
            DomainInfo.REGISTRY_FDSRDDS,
            MarkupPrice(
                16560, transfer=16560, restore=3600, currency=None, display_currency='USD', tld='ht',
                markup=decimal.Decimal("1.2"), periods=map(lambda i: apps.epp_api.Period(
                    unit=0,
                    value=i
                ), range(1, 6))
            )
        )),
        ('in', DomainInfo(
            DomainInfo.REGISTRY_NIXI,
            MarkupPrice(
                3024, transfer=3024, restore=15120, currency=None, display_currency='USD', tld='in',
                markup=decimal.Decimal("1.4"), periods=map(lambda i: apps.epp_api.Period(
                    unit=0,
                    value=i
                ), range(1, 6))
            )
        )),
        ('rs', DomainInfo(
            DomainInfo.REGISTRY_RNIDS,
            MarkupPrice(18295, transfer=8640, restore=8640, currency=None, display_currency='USD', tld='rs',
                        markup=decimal.Decimal("1.2"))
        )),
        ('at', DomainInfo(
            DomainInfo.REGISTRY_NICAT,
            MarkupPrice(
                2205, transfer=0, restore=1875, currency=None, display_currency='EUR', tld='at',
                markup=decimal.Decimal("1.5"), periods=[apps.epp_api.Period(
                    unit=0,
                    value=1
                )]
            )
        )),
        ('horse', DomainInfo(
            DomainInfo.REGISTRY_GODADDY,
            MarkupPrice(4498, transfer=4498, restore=3250, currency=None, display_currency='USD', tld='horse',
                        markup=decimal.Decimal("1.3"))
        )),
        ('us', DomainInfo(
            DomainInfo.REGISTRY_US,
            MarkupPrice(2045, transfer=2045, restore=14400, currency=None, display_currency='USD', tld='us',
                        markup=decimal.Decimal("1.6"))
        )),
        ('pl', DomainInfo(
            DomainInfo.REGISTRY_NASK,
            MarkupPrice(15600, transfer=0, restore=10400, currency=None, display_currency='PLN', tld='pl',
                        markup=decimal.Decimal("1.3"))
        )),
        ('biz.pl', DomainInfo(
            DomainInfo.REGISTRY_NASK,
            MarkupPrice(12825, transfer=0, restore=10800, currency=None, display_currency='PLN', tld='biz.pl',
                        markup=decimal.Decimal("1.35"))
        )),
        ('com.pl', DomainInfo(
            DomainInfo.REGISTRY_NASK,
            MarkupPrice(12825, transfer=0, restore=10800, currency=None, display_currency='PLN', tld='com.pl',
                        markup=decimal.Decimal("1.35"))
        )),
        ('edu.pl', DomainInfo(
            DomainInfo.REGISTRY_NASK,
            MarkupPrice(12825, transfer=0, restore=10800, currency=None, display_currency='PLN', tld='edu.pl',
                        markup=decimal.Decimal("1.35"))
        )),
        ('info.pl', DomainInfo(
            DomainInfo.REGISTRY_NASK,
            MarkupPrice(12825, transfer=0, restore=10800, currency=None, display_currency='PLN', tld='info.pl',
                        markup=decimal.Decimal("1.35"))
        )),
        ('net.pl', DomainInfo(
            DomainInfo.REGISTRY_NASK,
            MarkupPrice(12825, transfer=0, restore=10800, currency=None, display_currency='PLN', tld='net.pl',
                        markup=decimal.Decimal("1.35"))
        )),
        ('org.pl', DomainInfo(
            DomainInfo.REGISTRY_NASK,
            MarkupPrice(12825, transfer=0, restore=10800, currency=None, display_currency='PLN', tld='org.pl',
                        markup=decimal.Decimal("1.35"))
        )),
        ('waw.pl', DomainInfo(
            DomainInfo.REGISTRY_NASK,
            MarkupPrice(11116, transfer=0, restore=11200, currency=None, display_currency='PLN', tld='waw.pl',
                        markup=decimal.Decimal("1.4"))
        )),
        ('es', DomainInfo(
            DomainInfo.REGISTRY_REDES,
            MarkupPrice(
                2235, transfer=0, restore=3000, currency=None, display_currency='EUR', tld='es',
                markup=decimal.Decimal("1.5"), periods=[apps.epp_api.Period(
                    unit=0,
                    value=1
                ), apps.epp_api.Period(
                    unit=0,
                    value=2
                ), apps.epp_api.Period(
                    unit=0,
                    value=3
                ), apps.epp_api.Period(
                    unit=0,
                    value=4
                ), apps.epp_api.Period(
                    unit=0,
                    value=5
                ), apps.epp_api.Period(
                    unit=0,
                    value=10
                )]
            )
        )),
        ('org.es', DomainInfo(
            DomainInfo.REGISTRY_REDES,
            MarkupPrice(2235, transfer=0, restore=3000, currency=None, display_currency='EUR', tld='org.es',
                        markup=decimal.Decimal("1.5"), periods=[apps.epp_api.Period(
                    unit=0,
                    value=1
                ), apps.epp_api.Period(
                    unit=0,
                    value=2
                ), apps.epp_api.Period(
                    unit=0,
                    value=3
                ), apps.epp_api.Period(
                    unit=0,
                    value=4
                ), apps.epp_api.Period(
                    unit=0,
                    value=5
                ), apps.epp_api.Period(
                    unit=0,
                    value=10
                )]
            )
        )),
        ('nom.es', DomainInfo(
            DomainInfo.REGISTRY_REDES,
            MarkupPrice(
                2235, transfer=0, restore=3000, currency=None, display_currency='EUR', tld='nom.es',
                markup=decimal.Decimal("1.5"), periods=[apps.epp_api.Period(
                    unit=0,
                    value=1
                ), apps.epp_api.Period(
                    unit=0,
                    value=2
                ), apps.epp_api.Period(
                    unit=0,
                    value=3
                ), apps.epp_api.Period(
                    unit=0,
                    value=4
                ), apps.epp_api.Period(
                    unit=0,
                    value=5
                ), apps.epp_api.Period(
                    unit=0,
                    value=10
                )]
            )
        )),
        ('com.es', DomainInfo(
            DomainInfo.REGISTRY_REDES,
            MarkupPrice(
                2235, transfer=0, restore=3000, currency=None, display_currency='EUR', tld='com.es',
                markup=decimal.Decimal("1.5"), periods=[apps.epp_api.Period(
                    unit=0,
                    value=1
                ), apps.epp_api.Period(
                    unit=0,
                    value=2
                ), apps.epp_api.Period(
                    unit=0,
                    value=3
                ), apps.epp_api.Period(
                    unit=0,
                    value=4
                ), apps.epp_api.Period(
                    unit=0,
                    value=5
                ), apps.epp_api.Period(
                    unit=0,
                    value=10
                )]
            )
        )),
        ('nl', DomainInfo(
            DomainInfo.REGISTRY_NASK,
            MarkupPrice(1904, restore=1904, currency=None, display_currency='EUR', tld='nl',
                        markup=decimal.Decimal("1.6"))
        )),
        ('tel', DomainInfo(
            DomainInfo.REGISTRY_GODADDY,
            MarkupPrice(2363, restore=2363, currency=None, display_currency='USD', tld='tel',
                        markup=decimal.Decimal("1.4"))
        )),
        ('museum', DomainInfo(
            DomainInfo.REGISTRY_MDMA,
            MarkupPrice(7248, restore=3000, currency=None, display_currency='EUR', tld='museum',
                        markup=decimal.Decimal("1.2"))
        )),
        ('nf', DomainInfo(
            DomainInfo.REGISTRY_COCCA,
            MarkupPrice(17400, restore=4800, currency=None, display_currency='USD', tld='nf',
                        markup=decimal.Decimal("1.2"))
        )),
        ('blue', DomainInfo(
            DomainInfo.REGISTRY_AFILIAS,
            MarkupPrice(3192, restore=11700, currency=None, display_currency='USD', tld='blue',
                        markup=decimal.Decimal("1.3"))
        )),
        ('foo', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2940, restore=16800, currency=None, display_currency='USD', tld='foo',
                        markup=decimal.Decimal("1.4"))
        )),
        ('zip', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2940, restore=16800, currency=None, display_currency='USD', tld='zip',
                        markup=decimal.Decimal("1.4"))
        )),
        ('mov', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2940, restore=16800, currency=None, display_currency='USD', tld='mov',
                        markup=decimal.Decimal("1.4"))
        )),
        ('nexus', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2940, restore=16800, currency=None, display_currency='USD', tld='nexus',
                        markup=decimal.Decimal("1.4"))
        )),
        ('dad', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2940, restore=16800, currency=None, display_currency='USD', tld='dad',
                        markup=decimal.Decimal("1.4"))
        )),
        ('phd', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(4511, restore=13000, currency=None, display_currency='USD', tld='phd',
                        markup=decimal.Decimal("1.3"))
        )),
        ('prof', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(4511, restore=13000, currency=None, display_currency='USD', tld='prof',
                        markup=decimal.Decimal("1.3"))
        )),
        ('esq', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(4511, restore=13000, currency=None, display_currency='USD', tld='esq',
                        markup=decimal.Decimal("1.3"))
        )),
    )


def get_domain_info(domain: str) -> typing.Tuple[typing.Optional[DomainInfo], str]:
    parts = domain.rstrip(".").split(".", maxsplit=1)
    if len(parts) != 2:
        return None, domain
    sld, tld = parts
    for zone in ZONES:
        if zone[0] == tld:
            return zone[1], sld

    return None, sld
