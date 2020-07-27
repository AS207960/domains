from django.conf import settings
from concurrent.futures import ThreadPoolExecutor
import decimal
import django_keycloak_auth.clients
import requests
import typing
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

    def fees(self, sld):
        return {
            "periods": list(map(lambda p: {
                "period": p,
                "create": self.registration(sld, p.value, p.unit),
                "renew": self.renewal(sld, p.value, p.unit),
            }, self.periods)),
            "restore": self.restore(sld),
            "transfer": self.transfer(sld),
        }

    def registration(self, _sld: str, value=1, unit=0):
        if apps.epp_api.Period(
            unit=unit,
            value=value
        ) not in self.periods:
            return None
        return (decimal.Decimal(self.price) / decimal.Decimal(100)) * _mul(value, unit)

    def renewal(self, _sld: str, value=1, unit=0):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        return (decimal.Decimal(self._renewal) / decimal.Decimal(100)) * _mul(value, unit)

    def restore(self, _sld: str):
        return decimal.Decimal(self._restore) / decimal.Decimal(100)

    def transfer(self, _sld: str, value=1, unit=0):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        return (decimal.Decimal(self._transfer) / decimal.Decimal(100)) * _mul(value, unit)


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

    def fees(self, sld):
        return {
            "periods": list(map(lambda p: {
                "period": p,
                "create": self.registration(sld, p.value, p.unit),
                "renew": self.renewal(sld, p.value, p.unit),
            }, self.periods)),
            "restore": self.restore(sld),
            "transfer": self.transfer(sld),
        }

    def registration(self, sld: str, value=1, unit=0):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        return (decimal.Decimal(
            self.lengths.get(len(sld), self.standard_price)
        ) / decimal.Decimal(100)) * _mul(value, unit)

    def renewal(self, _sld: str, value=1, unit=0):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        return (decimal.Decimal(self._renewal) / decimal.Decimal(100)) * _mul(value, unit)

    def restore(self, _sld: str):
        return decimal.Decimal(self._restore) / decimal.Decimal(100)

    def transfer(self, _sld: str, value=1, unit=0):
        if apps.epp_api.Period(
                unit=unit,
                value=value
        ) not in self.periods:
            return None
        return (decimal.Decimal(self._transfer) / decimal.Decimal(100)) * _mul(value, unit)


class MarkupPrice:
    def __init__(
            self, price: int, markup: decimal.Decimal, tld: str, currency: typing.Optional[str], display_currency=None,
            periods=None, restore=0, renewal=None, transfer=0
    ):
        self.price = price
        self._tld = tld
        self._markup = markup
        self._currency = currency
        self._display_currency = display_currency if display_currency else currency
        self._renewal = renewal if renewal else price
        self._restore = restore
        self._transfer = transfer
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

    def fees(self, sld):
        domain = f"{sld}.{self._tld}"

        commands_split = [[apps.epp_api.fee_pb2.FeeCommand(
            command=apps.epp_api.fee_pb2.Transfer,
            period=None
        ), apps.epp_api.fee_pb2.FeeCommand(
            command=apps.epp_api.fee_pb2.Restore,
            period=None
        )]]

        for period in self.periods:
            commands_split.append([apps.epp_api.fee_pb2.FeeCommand(
                command=apps.epp_api.fee_pb2.Create,
                period=period.to_pb()
            ), apps.epp_api.fee_pb2.FeeCommand(
                command=apps.epp_api.fee_pb2.Renew,
                period=period.to_pb()
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
                "fee": self._convert_fee(f)
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
            "restore": self._convert_fee(restore_command) if restore_command else None,
            "transfer": self._convert_fee(transfer_command) if transfer_command else None,
        }

    def _convert_fee(self, command):
        total_fee = decimal.Decimal(0)
        for fee in command.fees:
            total_fee += decimal.Decimal(fee.value)
        for credit in command.credits:
            total_fee += decimal.Decimal(credit.value)

        final_fee = total_fee * self._markup

        client_token = django_keycloak_auth.clients.get_access_token()
        r = requests.post(
            f"{settings.BILLING_URL}/convert_currency/", json={
                "amount": str(final_fee),
                "from": command.currency,
                "to": "GBP",
            }, headers={
                "Authorization": f"Bearer {client_token}"
            }
        )
        r_data = r.json()
        fee = decimal.Decimal(r_data.get("amount")).quantize(decimal.Decimal('1.00'))
        return fee

    def _get_fee(self, sld, value, unit, command):
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
                    period=period.to_pb() if unit is not None else None
                )]
            )
        ))
        if not resp.HasField("fee_check"):
            return None
        if not resp.fee_check.available:
            return None
        command = resp.fee_check.commands[0]

        return self._convert_fee(command)

    def registration(self, sld: str, value=1, unit=0):
        return self._get_fee(sld, value, unit, apps.epp_api.fee_pb2.Create)

    def renewal(self, sld: str, value=None, unit=None):
        return self._get_fee(sld, value, unit, apps.epp_api.fee_pb2.Renew)

    def restore(self, sld: str):
        fee = self._get_fee(sld, None, None, apps.epp_api.fee_pb2.Restore)
        if not fee:
            return self.representative_restore()
        else:
            return fee

    def transfer(self, sld: str, value=None, unit=None):
        return self._get_fee(sld, value, unit, apps.epp_api.fee_pb2.Transfer)


class DomainInfo:
    REGISTRY_NOMINET = "nominet"
    REGISTRY_SWITCH = "switch"
    REGISTRY_TRAFICOM = "traficom"
    REGISTRY_AFILIAS = "afilias"
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

    def __init__(self, registry, pricing, notice=None):
        self.registry = registry
        self.pricing = pricing
        self.notice = notice

    @property
    def direct_registration_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_VERISIGN,
            self.REGISTRY_CENTRALNIC_CCTLD
        )

    @property
    def direct_transfer_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            # self.REGISTRY_DENIC
        )

    @property
    def direct_restore_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
        )

    @property
    def transfer_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_DENIC,
            self.REGISTRY_VERISIGN_COMNET,
            self.REGISTRY_PIR,
            self.REGISTRY_GOOGLE,
        )

    @property
    def pre_transfer_query_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_AFILIAS,
            self.REGISTRY_NOMINET,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_VERISIGN,
            self.REGISTRY_CENTRALNIC_CCTLD
        )

    @property
    def renew_supported(self):
        return self.registry not in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_DENIC
        )

    @property
    def restore_supported(self):
        return self.registry not in (
            self.REGISTRY_NOMINET,
        )

    @property
    def transfer_lock_supported(self):
        return self.registry not in (
            self.REGISTRY_NOMINET,
            self.REGISTRY_SWITCH,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_EURID
        )

    @property
    def fee_supported(self):
        return self.registry not in (
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_NOMINET,
            self.REGISTRY_SWITCH
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
        )

    @property
    def ds_data_supported(self):
        return self.registry not in (
            self.REGISTRY_DENIC
        )

    @property
    def admin_supported(self):
        return self.registry not in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_NOMINET,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_VERISIGN,
            self.REGISTRY_DNSBELGIUM,
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
            self.REGISTRY_INTERLINK,
            self.REGISTRY_GOOGLE,
        )

    @property
    def tech_supported(self):
        return self.registry not in (
            self.REGISTRY_NOMINET,
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
            self.REGISTRY_INTERLINK,
            self.REGISTRY_GOOGLE,
        )

    @property
    def billing_supported(self):
        return self.registry not in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_NOMINET,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_VERISIGN,
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
            self.REGISTRY_INTERLINK,
            self.REGISTRY_GOOGLE,
        )


if settings.DEBUG:
    ZONES = (
        ('uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.Period(
            unit=0,
            value=2
        )]))),
        ('co.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.Period(
            unit=0,
            value=2
        )]))),
        ('org.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.Period(
            unit=0,
            value=2
        )]))),
        ('me.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.Period(
            unit=0,
            value=2
        )]))),
        ('ltd.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.Period(
            unit=0,
            value=2
        )]))),
        ('plc.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.Period(
            unit=0,
            value=2
        )]))),
        ('net.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.Period(
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
            MarkupPrice(2700, renewal=2700, currency=None, display_currency='USD', tld='pw', markup=decimal.Decimal("1.5"))
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
            MarkupPrice(1368, renewal=1080, restore=4500, currency='USD', display_currency='EUR', tld='de', markup=decimal.Decimal("1.5"))
        )),
        ('tv', DomainInfo(
            DomainInfo.REGISTRY_VERISIGN,
            MarkupPrice(2566, restore=4000, currency='USD', tld='tv', markup=decimal.Decimal("1.25"))
        )),
        ('cc', DomainInfo(DomainInfo.REGISTRY_VERISIGN, SimplePrice(825, restore=4000))),
        ('dev', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2940, transfer=2940, restore=22500, currency=None, display_currency='USD', tld='dev', markup=decimal.Decimal("1.4")),
            notice=".dev is a HSTS preload zone, meaning you'll need to deploy HTTPS on any website hosted on a "
                   ".dev domain."
        )),
    )
else:
    ZONES = (
        ('com', DomainInfo(
            DomainInfo.REGISTRY_VERISIGN_COMNET,
            MarkupPrice(2234, transfer=2234, restore=16200, currency=None, display_currency='USD', tld='com', markup=decimal.Decimal("1.5"))
        )),
        ('net', DomainInfo(
            DomainInfo.REGISTRY_VERISIGN_COMNET,
            MarkupPrice(3009, transfer=3009, restore=15120, currency=None, display_currency='USD', tld='net', markup=decimal.Decimal("1.4"))
        )),
        ('org', DomainInfo(
            DomainInfo.REGISTRY_PIR,
            MarkupPrice(2758, transfer=2758, restore=15660, currency=None, display_currency='USD', tld='org', markup=decimal.Decimal("1.45"))
        )),
        ('ch', DomainInfo(DomainInfo.REGISTRY_SWITCH, SimplePrice(999, periods=[apps.epp_api.Period(
            unit=0,
            value=1
        )]))),
        ('li', DomainInfo(DomainInfo.REGISTRY_SWITCH, SimplePrice(999, periods=[apps.epp_api.Period(
            unit=0,
            value=1
        )]))),
        ('pw', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2700, transfer=2700, currency=None, display_currency='USD', tld='pw', markup=decimal.Decimal("1.7"))
        )),
        ('fm', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(12240, transfer=12240, restore=17280, currency=None, display_currency='USD', tld='fm', markup=decimal.Decimal("1.4"))
        )),
        ('fo', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(6048, transfer=6048, restore=18808, currency=None, display_currency='EUR', tld='fo', markup=decimal.Decimal("1.4"))
        )),
        ('gd', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(3900, transfer=3900, restore=10920, currency=None, display_currency='USD', tld='gd', markup=decimal.Decimal("1.5"))
        )),
        ('vg', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(3900, transfer=3900, restore=10920, currency=None, display_currency='USD', tld='vg', markup=decimal.Decimal("1.5"))
        )),
        ('ae.org', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2520, transfer=2520, restore=2520, currency=None, display_currency='USD', tld='ae.org', markup=decimal.Decimal("1.6"))
        )),
        ('br.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(4752, transfer=4752, restore=4752, currency=None, display_currency='USD', tld='br.com', markup=decimal.Decimal("1.4"))
        )),
        ('cn.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2352, renewal=5040, transfer=5040, restore=4752, currency=None, display_currency='USD', tld='cn.com', markup=decimal.Decimal("1.6"))
        )),
        ('co.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(3120, transfer=3120, restore=9360, currency=None, display_currency='USD', tld='co.com', markup=decimal.Decimal("1.5"))
        )),
        ('co.nl', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1176, transfer=1176, restore=12000, currency=None, display_currency='EUR', tld='co.nl', markup=decimal.Decimal("2.2"))
        )),
        ('co.no', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2495, transfer=2495, restore=10072, currency=None, display_currency='EUR', tld='co.no', markup=decimal.Decimal("1.6"))
        )),
        ('com.de', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1080, transfer=1080, restore=1080, currency=None, display_currency='EUR', tld='com.de', markup=decimal.Decimal("2.7"))
        )),
        ('com.se', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1501, transfer=1501, restore=1501, currency=None, display_currency='EUR', tld='com.se', markup=decimal.Decimal("2"))
        )),
        ('de.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2100, transfer=2100, restore=2100, currency=None, display_currency='EUR', tld='de.com', markup=decimal.Decimal("1.6"))
        )),
        ('eu.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2100, transfer=2100, restore=2100, currency=None, display_currency='EUR', tld='eu.com', markup=decimal.Decimal("1.6"))
        )),
        ('gb.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1200, transfer=1200, restore=1200, currency=None, display_currency='GBP', tld='gb.net', markup=decimal.Decimal("2.2"))
        )),
        ('gr.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1890, transfer=1890, restore=1890, currency=None, display_currency='EUR', tld='gr.com', markup=decimal.Decimal("1.7"))
        )),
        ('hu.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(3744, transfer=3744, restore=3744, currency=None, display_currency='EUR', tld='hu.net', markup=decimal.Decimal("1.5"))
        )),
        ('in.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1440, transfer=1440, restore=1440, currency=None, display_currency='USD', tld='in.net', markup=decimal.Decimal("2.2"))
        )),
        ('jp.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(1680, transfer=1680, restore=1680, currency=None, display_currency='USD', tld='jp.net', markup=decimal.Decimal("2.2"))
        )),
        ('jpn.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(4680, transfer=4680, restore=4680, currency=None, display_currency='USD', tld='jpn.com', markup=decimal.Decimal("1.5"))
        )),
        ('mex.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2040, transfer=2040, restore=2040, currency=None, display_currency='USD', tld='mex.com', markup=decimal.Decimal("1.9"))
        )),
        ('ru.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(4680, transfer=4680, restore=4680, currency=None, display_currency='USD', tld='ru.com', markup=decimal.Decimal("1.5"))
        )),
        ('sa.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(7056, transfer=7056, restore=7056, currency=None, display_currency='USD', tld='sa.com', markup=decimal.Decimal("1.4"))
        )),
        ('se.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(3588, transfer=3588, restore=3588, currency=None, display_currency='EUR', tld='se.net', markup=decimal.Decimal("1.5"))
        )),
        ('uk.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2335, transfer=2335, restore=2335, currency=None, display_currency='GBP', tld='uk.com', markup=decimal.Decimal("1.5"))
        )),
        ('uk.net', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2335, transfer=2335, restore=2335, currency=None, display_currency='GBP', tld='uk.net', markup=decimal.Decimal("1.5"))
        )),
        ('us.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2520, transfer=2520, restore=2520, currency=None, display_currency='USD', tld='us.com', markup=decimal.Decimal("1.6"))
        )),
        ('us.org', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(2520, transfer=2520, restore=2520, currency=None, display_currency='USD', tld='us.org', markup=decimal.Decimal("1.6"))
        )),
        ('za.com', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(7056, transfer=7056, restore=7056, currency=None, display_currency='USD', tld='za.com', markup=decimal.Decimal("1.4"))
        )),
        ('radio.am', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(178, transfer=2160, restore=8460, currency=None, display_currency='USD', tld='radio.am', markup=decimal.Decimal("1.7"))
        )),
        ('radio.fm', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC_CCTLD,
            MarkupPrice(178, transfer=2160, restore=8460, currency=None, display_currency='USD', tld='radio.fm', markup=decimal.Decimal("1.7"))
        )),
        ('gay', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(6480, transfer=6480, restore=37500, currency=None, display_currency='USD', tld='gay', markup=decimal.Decimal("1.25"))
        )),
        ('site', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(5205, transfer=5205, restore=16500, currency=None, display_currency='USD', tld='site', markup=decimal.Decimal("1.25"))
        )),
        ('website', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(3900, transfer=3900, restore=13500, currency=None, display_currency='USD', tld='website', markup=decimal.Decimal("1.25"))
        )),
        ('tech', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(9390, transfer=9390, restore=16500, currency=None, display_currency='USD', tld='tech', markup=decimal.Decimal("1.25"))
        )),
        ('design', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(8194, transfer=8194, restore=20160, currency=None, display_currency='USD', tld='design', markup=decimal.Decimal("1.2"))
        )),
        ('xyz', DomainInfo(
            DomainInfo.REGISTRY_CENTRALNIC,
            MarkupPrice(2142, transfer=2142, restore=18000, currency=None, display_currency='EUR', tld='xyz', markup=decimal.Decimal("1.5"))
        )),
        ('de', DomainInfo(
            DomainInfo.REGISTRY_DENIC,
            MarkupPrice(1596, transfer=1260, restore=5250, currency=None, display_currency='EUR', tld='de', markup=decimal.Decimal("1.75"))
        )),
        ('space', DomainInfo(
            DomainInfo.REGISTRY_DONUTS,
            MarkupPrice(3893, transfer=3893, restore=13500, currency=None, display_currency='USD', tld='space', markup=decimal.Decimal("1.25"))
        )),
        ('fi', DomainInfo(DomainInfo.REGISTRY_TRAFICOM, SimplePrice(1499, periods=map(lambda i: apps.epp_api.Period(
            unit=0,
            value=i
        ), range(1, 6))))),
        ('cymru', DomainInfo(
            DomainInfo.REGISTRY_NOMINET_GTLD,
            MarkupPrice(2167, transfer=2167, restore=2688, currency=None, display_currency='GBP', tld='cymru', markup=decimal.Decimal("1.4"))
        )),
        ('wales', DomainInfo(
            DomainInfo.REGISTRY_NOMINET_GTLD,
            MarkupPrice(2167, transfer=2167, restore=2688, currency=None, display_currency='GBP', tld='wales', markup=decimal.Decimal("1.4"))
        )),
        ('moe', DomainInfo(
            DomainInfo.REGISTRY_INTERLINK,
            MarkupPrice(3120, transfer=3120, restore=14040, currency=None, display_currency='USD', tld='moe', markup=decimal.Decimal("1.3"))
        )),
        ('eu', DomainInfo(
            DomainInfo.REGISTRY_EURID,
            MarkupPrice(1728, transfer=1728, restore=2880, currency=None, display_currency='EUR', tld='eu', markup=decimal.Decimal("1.6"))
        )),
        ('soy', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(4478, transfer=4478, restore=21600, currency=None, display_currency='USD', tld='soy', markup=decimal.Decimal("1.2"))
        )),
        ('how', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(4954, transfer=4954, restore=21600, currency=None, display_currency='USD', tld='how', markup=decimal.Decimal("1.2"))
        )),
        ('page', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2436, transfer=2436, restore=26100, currency=None, display_currency='USD', tld='page', markup=decimal.Decimal("1.45"))
        )),
        ('dev', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(2940, transfer=2940, restore=25200, currency=None, display_currency='USD', tld='dev', markup=decimal.Decimal("1.4")),
            notice=".dev is a HSTS preload zone, meaning you'll need to deploy HTTPS on any website hosted on a "
                   ".dev domain."
        )),
        ('app', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(3198, transfer=3198, restore=23400, currency=None, display_currency='USD', tld='app', markup=decimal.Decimal("1.3")),
            notice=".app is a HSTS preload zone, meaning you'll need to deploy HTTPS on any website hosted on a "
                   ".app domain."
        )),
        ('new', DomainInfo(
            DomainInfo.REGISTRY_GOOGLE,
            MarkupPrice(84960, transfer=84960, restore=21600, currency=None, display_currency='USD', tld='new', markup=decimal.Decimal("1.2")),
            notice=".new domains must allow a user to create something, without further navigation, within 100 days "
                   "of being purchased. .new is a HSTS preload zone, meaning you'll need to deploy HTTPS on any "
                   "website hosted on a .new domain."
        )),
        ('tv', DomainInfo(
            DomainInfo.REGISTRY_VERISIGN,
            MarkupPrice(3250, transfer=3250, restore=5200, currency='USD', tld='tv', markup=decimal.Decimal("1.3"))
        )),
        ('cc', DomainInfo(DomainInfo.REGISTRY_VERISIGN, SimplePrice(1299, transfer=1299, restore=6500))),
    )


def get_domain_info(domain: str):
    parts = domain.rstrip(".").split(".", maxsplit=1)
    if len(parts) != 2:
        return None, domain
    sld, tld = parts
    for zone in ZONES:
        if zone[0] == tld:
            return zone[1], sld

    return None, sld
