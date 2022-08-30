import django_countries
import dataclasses
import domains.views.billing
import domains.apps
import decimal
import as207960_utils.rpc


@dataclasses.dataclass
class CountryState:
    iso_code: str
    emoji: str
    name: str


def map_country(cc):
    country_name = dict(django_countries.countries)[cc]
    country_emoji = chr(ord(cc[0]) + 127397) + chr(ord(cc[1]) + 127397)

    return CountryState(
        iso_code=cc,
        emoji=country_emoji,
        name=country_name,
    )


class CountryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "selected_billing_country" in request.session:
            selected_country = request.session["selected_billing_country"].upper()
        else:
            username = request.user.username if request.user.is_authenticated else None
            try:
                price_resp = domains.views.billing.convert_currency(
                    decimal.Decimal(0), "GBP", username, domains.apps.get_ip(request), None, timeout=3
                )
                selected_country = price_resp.country.upper()
            except as207960_utils.rpc.TimeoutError:
                selected_country = "GB"

            request.session["selected_billing_country"] = selected_country

        request.country = map_country(selected_country)
        response = self.get_response(request)

        return response


class CountryDummyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "selected_billing_country" in request.session:
            selected_country = request.session["selected_billing_country"].upper()
        else:
            selected_country = "GB"

        request.country = map_country(selected_country)
        response = self.get_response(request)

        return response
