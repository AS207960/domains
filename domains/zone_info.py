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

    def __init__(self, registry, pricing):
        self.registry = registry
        self.pricing = pricing


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
        ('fi', DomainInfo(DomainInfo.REGISTRY_AFILIAS, SimplePrice(2500, periods=map(lambda i: apps.epp_api.DomainPeriod(
            unit=0,
            value=i
        ), range(1, 6))))),
        # ('me', SimplePrice(1400)),
        ('de', DomainInfo(DomainInfo.REGISTRY_DENIC, SimplePrice(1300, renewal=1150))),
    )
else:
    ZONES = (
        ('de', DomainInfo(DomainInfo.REGISTRY_DENIC, SimplePrice(1300, renewal=1150))),
    )


def get_domain_info(domain: str):
    sld, tld = domain.rstrip(".").split(".", maxsplit=1)
    for zone in ZONES:
        if zone[0] == tld:
            return zone[1], sld

    return None, sld
