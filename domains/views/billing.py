from django.conf import settings
import django_keycloak_auth.clients
import decimal
import requests


def charge_account(username: str, amount: decimal.Decimal, descriptor: str, charge_id: str, can_reject=True):
    client_token = django_keycloak_auth.clients.get_access_token()
    r = requests.post(
        f"{settings.BILLING_URL}/charge_user/{username}/", json={
            "amount": int(decimal.Decimal(100) * amount),
            "descriptor": descriptor,
            "id": charge_id,
            "can_reject": can_reject
        }, headers={
            "Authorization": f"Bearer {client_token}"
        }
    )
    if r.status_code == 402:
        return 'Unable to charge your account. Please to go to billing.as207960.net to top-up.'
    elif r.status_code == 200:
        return None
    else:
        return 'There was an unexpected error'
