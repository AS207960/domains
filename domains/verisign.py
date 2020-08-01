import requests
import random
import enum
import typing
import dataclasses
from django.conf import settings
from . import zone_info

if settings.DEBUG:
    NS_API_BASE = "https://ote-sugapi.verisign-grs.com/ns-api/2.0"
else:
    NS_API_BASE = "https://sugapi.verisign-grs.com/ns-api/2.0"


@dataclasses.dataclass
class SupportedTLD:
    tld: str
    checked: bool

    def __eq__(self, other):
        if isinstance(other, SupportedTLD):
            return super().__eq__(other)
        elif isinstance(other, str):
            return other == self.tld
        else:
            return False


class Availability(enum.Enum):
    AVAILABLE = enum.auto()
    REGISTERED = enum.auto()
    RESERVED = enum.auto()
    PREMIUM = enum.auto()
    UNKNOWN = enum.auto()
    INVALID = enum.auto()


@dataclasses.dataclass
class SuggestedDomain:
    name: str
    availability: Availability

    @classmethod
    def from_result(cls, res):
        if res["availability"] == "available":
            availability = Availability.AVAILABLE
        elif res["availability"] == "registered":
            availability = Availability.REGISTERED
        elif res["availability"] == "reserved":
            availability = Availability.RESERVED
        elif res["availability"] == "premium":
            availability = Availability.PREMIUM
        elif res["availability"] == "UNKNOWN":
            availability = Availability.UNKNOWN
        elif res["availability"] == "INVALID":
            availability = Availability.INVALID
        else:
            availability = Availability.UNKNOWN

        return cls(
            name=res["name"],
            availability=availability
        )


class VerisignError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


def make_verisign_request(uri, data=None):
    r = requests.get(f"{NS_API_BASE}{uri}", headers={
        "X-NameSuggestion-APIKey": settings.VERISIGN_NS_API_KEY
    }, params=data)
    data = r.json()
    if r.status_code != 200:
        raise VerisignError(data["code"], data["message"])
    return data


def get_supported_tlds() -> typing.List[SupportedTLD]:
    data = make_verisign_request("/supported-tlds")
    return list(map(lambda i: SupportedTLD(
        tld=i["unicode"],
        checked="@checked" in i["tags"] if "tags" in i else False
    ), data))


def get_intersecting_tlds() -> typing.List[SupportedTLD]:
    supported_tlds = get_supported_tlds()
    out = []
    supported_zones = list(map(lambda z: z[0], zone_info.ZONES))
    for tld in supported_tlds:
        if tld in supported_zones:
            out.append(tld)
    return out


def suggests(
        name: str,
        ip_address: typing.Optional[str] = None,
) -> typing.List[SuggestedDomain]:
    tlds = ",".join(list(map(lambda t: t.tld, get_intersecting_tlds())))
    params = {
        "use-idns": "yes",
        "tlds": tlds,
        "name": name
    }
    if ip_address:
        params["ip-address"] = ip_address

    data = make_verisign_request("/suggest", params)
    return list(map(SuggestedDomain.from_result, data["results"]))


def suggest_personal_names(
        first_name: typing.Optional[str] = None,
        last_name: typing.Optional[str] = None,
        middle_names: typing.Optional[typing.List[str]] = None
) -> typing.List[SuggestedDomain]:
    tlds = ",".join(random.choices(list(map(lambda t: t.tld, get_intersecting_tlds())), k=10))
    params = {
        "use-idns": "yes",
        "tlds": tlds
    }
    if first_name:
        params["first-name"] = first_name
    if middle_names:
        params["middle-names"] = middle_names
    if last_name:
        params["last-name"] = last_name

    data = make_verisign_request("/suggest-personal-names", params)
    return list(map(SuggestedDomain.from_result, data["results"]))


def online_presence(
        online_uri: typing.Optional[str] = None,
        online_title: typing.Optional[str] = None,
        related_uris: typing.Optional[typing.List[str]] = None,
        category: typing.Optional[str] = None,
        online_description: typing.Optional[str] = None,
        preferred_name: typing.Optional[str] = None,
        location: typing.Optional[str] = None,
        email: typing.Optional[str] = None,
) -> typing.List[SuggestedDomain]:
    tlds = ",".join(random.choices(list(map(lambda t: t.tld, get_intersecting_tlds())), k=10))
    params = {
        "tlds": tlds
    }
    if online_uri:
        params["online-presence-url"] = online_uri
    if online_title:
        params["online-presence-title"] = online_title
    if related_uris:
        params["related-urls"] = related_uris
    if category:
        params["category"] = category
    if online_description:
        params["online-presence-description"] = online_description
    if preferred_name:
        params["preferred-name"] = preferred_name
    if location:
        params["location"] = location
    if email:
        params["email"] = email

    data = make_verisign_request("/online-presence", params)
    return list(map(SuggestedDomain.from_result, data["results"]))