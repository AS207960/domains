from django.conf import settings
from . import apps


class SimplePrice:
    def __init__(self, price: int, periods=None, restore=0, renewal=None, transfer=0):
        self.price = price
        self._renewal = renewal if renewal else price
        self._restore = restore
        self._transfer = transfer
        self.periods = list(periods) if periods else list(map(lambda i: apps.epp_api.DomainPeriod(
            unit=0,
            value=i
        ), range(1, 11)))

    def registration(self, _sld: str):
        return self.price

    def renewal(self, _sld: str):
        return self._renewal

    def restore(self, _sld: str):
        return self._restore

    def transfer(self, _sld: str):
        return self._transfer


class LengthPrice:
    def __init__(self, standard_price: int, lengths, periods=None, restore=0, renewal=None, transfer=0):
        self.standard_price = standard_price
        self.lengths = lengths
        self._renewal = renewal if renewal else standard_price
        self._restore = restore
        self._transfer = transfer
        self.periods = periods if periods else list(map(lambda i: apps.epp_api.DomainPeriod(
            unit=0,
            value=i
        ), range(1, 11)))

    def registration(self, sld: str):
        return self.lengths.get(len(sld), self.standard_price)

    def renewal(self, _sld: str):
        return self._renewal

    def restore(self, _sld: str):
        return self._restore

    def transfer(self, _sld: str):
        return self._transfer


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
    REGISTRY_CENTRALNIC = "centralnic"
    REGISTRY_NOMINET_GTLD = "nominet-gtld"
    REGISTRY_DNSBELGIUM = "dnsbelgium"

    def __init__(self, registry, pricing):
        self.registry = registry
        self.pricing = pricing

    @property
    def transfer_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_DENIC
        )

    @property
    def pre_transfer_query_supported(self):
        return self.registry in (
            self.REGISTRY_SWITCH,
            self.REGISTRY_AFILIAS,
            self.REGISTRY_NOMINET,
            self.REGISTRY_TRAFICOM,
            self.REGISTRY_VERISIGN
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
            self.REGISTRY_TRAFICOM
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
            self.REGISTRY_CENTRALNIC,
            self.REGISTRY_NOMINET_GTLD,
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
            self.REGISTRY_CENTRALNIC,
            self.REGISTRY_NOMINET_GTLD,
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
            self.REGISTRY_CENTRALNIC,
            self.REGISTRY_NOMINET_GTLD,
        )


if settings.DEBUG:
    ZONES = (
        ('uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.DomainPeriod(
            unit=0,
            value=2
        )]))),
        ('co.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.DomainPeriod(
            unit=0,
            value=2
        )]))),
        ('org.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.DomainPeriod(
            unit=0,
            value=2
        )]))),
        ('me.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.DomainPeriod(
            unit=0,
            value=2
        )]))),
        ('ltd.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.DomainPeriod(
            unit=0,
            value=2
        )]))),
        ('plc.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.DomainPeriod(
            unit=0,
            value=2
        )]))),
        ('net.uk', DomainInfo(DomainInfo.REGISTRY_NOMINET, SimplePrice(8000, periods=[apps.epp_api.DomainPeriod(
            unit=0,
            value=2
        )]))),
        ('ch', DomainInfo(DomainInfo.REGISTRY_SWITCH, SimplePrice(1400))),
        ('li', DomainInfo(DomainInfo.REGISTRY_SWITCH, SimplePrice(1400))),
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
        # ('pw', SimplePrice(1800)),
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
        ('fi', DomainInfo(DomainInfo.REGISTRY_TRAFICOM, SimplePrice(2500, periods=map(lambda i: apps.epp_api.DomainPeriod(
            unit=0,
            value=i
        ), range(1, 6))))),
        # ('me', SimplePrice(1400)),
        ('de', DomainInfo(DomainInfo.REGISTRY_DENIC, SimplePrice(1300, renewal=1150, restore=3200))),
        ('tv', DomainInfo(DomainInfo.REGISTRY_VERISIGN, SimplePrice(2566, restore=4000))),
        ('cc', DomainInfo(DomainInfo.REGISTRY_VERISIGN, SimplePrice(825, restore=4000))),
    )
else:
    ZONES = (
        ('com', DomainInfo(DomainInfo.REGISTRY_VERISIGN_COMNET, SimplePrice(1519, transfer=1519, restore=9115))),
        ('net', DomainInfo(DomainInfo.REGISTRY_VERISIGN_COMNET, SimplePrice(2039, transfer=2039, restore=9115))),
        ('org', DomainInfo(DomainInfo.REGISTRY_PIR, SimplePrice(1869, transfer=1869, restore=9115))),
        ('gay', DomainInfo(DomainInfo.REGISTRY_CENTRALNIC, SimplePrice(4379, transfer=4379, restore=25400))),
        ('site', DomainInfo(DomainInfo.REGISTRY_CENTRALNIC, SimplePrice(3219, transfer=3219, restore=11200))),
        ('website', DomainInfo(DomainInfo.REGISTRY_CENTRALNIC, SimplePrice(2639, transfer=2639, restore=9119))),
        ('tech', DomainInfo(DomainInfo.REGISTRY_CENTRALNIC, SimplePrice(6299, transfer=6299, restore=11200))),
        ('xyz', DomainInfo(DomainInfo.REGISTRY_CENTRALNIC, SimplePrice(1449, transfer=1449, restore=11200))),
        ('de', DomainInfo(DomainInfo.REGISTRY_DENIC, SimplePrice(1300, transfer=1150, renewal=1150, restore=3200))),
        ('ch', DomainInfo(DomainInfo.REGISTRY_SWITCH, SimplePrice(999))),
        ('li', DomainInfo(DomainInfo.REGISTRY_SWITCH, SimplePrice(999))),
        ('space', DomainInfo(DomainInfo.REGISTRY_DONUTS, SimplePrice(3199, transfer=3199, restore=9230))),
        ('fi', DomainInfo(DomainInfo.REGISTRY_TRAFICOM, SimplePrice(1400, periods=map(lambda i: apps.epp_api.DomainPeriod(
            unit=0,
            value=i
        ), range(1, 6))))),
        ('cymru', DomainInfo(DomainInfo.REGISTRY_NOMINET_GTLD, SimplePrice(1569, transfer=1569, restore=1949))),
        ('wales', DomainInfo(DomainInfo.REGISTRY_NOMINET_GTLD, SimplePrice(1569, transfer=1569, restore=1949))),
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
