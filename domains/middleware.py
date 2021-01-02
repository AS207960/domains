import django_countries
import dataclasses
import domains.views.billing
import domains.apps
import decimal


@dataclasses.dataclass
class CountryState:
    iso_code: str
    emoji: str
    name: str


class CountryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "selected_billing_country" in request.session:
            selected_country = request.session["selected_billing_country"].upper()
        else:
            username = request.user.username if request.user.is_authenticated else None
            price_resp = domains.views.billing.convert_currency(
                decimal.Decimal(0), "GBP", username, domains.apps.get_ip(request), None
            )
            selected_country = price_resp.country.upper()

        country_name = dict(django_countries.countries)[selected_country]
        country_emoji = chr(ord(selected_country[0]) + 127397) + chr(ord(selected_country[1]) + 127397)

        request.country = CountryState(
            iso_code=selected_country,
            emoji=country_emoji,
            name=country_name,
        )

        response = self.get_response(request)

        return response
