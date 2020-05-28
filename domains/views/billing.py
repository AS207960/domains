from django.conf import settings
from django.utils.safestring import mark_safe
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
        return mark_safe(
            'Unable to charge your account. '
            'Please <a href="https://billing.as207960.net" class="alert-link" target="_blank">top-up</a> your account.'
        )
    elif r.status_code == 404:
        return mark_safe(
            'Unable to charge your account. '
            'Please <a href="https://billing.as207960.net" class="alert-link" target="_blank">set-up</a> your account.'
        )
    elif r.status_code == 200:
        return None
    else:
        return 'There was an unexpected error'
