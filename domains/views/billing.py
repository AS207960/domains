from django.conf import settings
import django_keycloak_auth.clients
import decimal
import requests
import dataclasses
import typing
import json


@dataclasses.dataclass
class ChargeResult:
    success: bool
    charge_state_id: typing.Optional[str]
    error: typing.Optional[str]
    redirect_uri: typing.Optional[str]


@dataclasses.dataclass
class ChargeState:
    status: str
    redirect_uri: typing.Optional[str]
    account: typing.Optional[str]
    last_error: typing.Optional[str]


def charge_account(username: str, amount: decimal.Decimal, descriptor: str, charge_id: str, can_reject=True,
                   off_session=True, return_uri=None) -> ChargeResult:
    client_token = django_keycloak_auth.clients.get_access_token()
    r = requests.post(
        f"{settings.BILLING_URL}/charge_user/{username}/", json={
            "amount": int(decimal.Decimal(100) * amount),
            "descriptor": descriptor,
            "id": charge_id,
            "can_reject": can_reject,
            "off_session": off_session,
            "return_uri": return_uri
        }, headers={
            "Authorization": f"Bearer {client_token}"
        }
    )
    try:
        data = r.json()
    except json.JSONDecodeError:
        return ChargeResult(
            success=False,
            error='There was an unexpected error.',
            redirect_uri=None,
            charge_state_id=None
        )

    if r.status_code in (402, 404, 302):
        return ChargeResult(
            success=False,
            error=data.get("message"),
            redirect_uri=data.get("redirect_uri"),
            charge_state_id=data.get("charge_state_id")
        )
    elif r.status_code == 200:
        return ChargeResult(
            success=True,
            error=None,
            redirect_uri=None,
            charge_state_id=data.get("charge_state_id")
        )
    else:
        return ChargeResult(
            success=False,
            error='There was an unexpected error.',
            redirect_uri=None,
            charge_state_id=None
        )


def get_charge_state(charge_state_id: str) -> ChargeState:
    client_token = django_keycloak_auth.clients.get_access_token()
    r = requests.get(
        f"{settings.BILLING_URL}/get_charge_state/{charge_state_id}/", headers={
            "Authorization": f"Bearer {client_token}"
        }
    )
    try:
        data = r.json()
    except json.JSONDecodeError:
        return ChargeState(
            status="unknown",
            account=None,
            redirect_uri=None,
            last_error="There was an unexpected error."
        )

    status = data.get("status")
    last_error = data.get("last_error")
    if status not in ("unknown", "processing", "failed", "completed"):
        status = "unknown"
        last_error = "There was an unexpected error."

    return ChargeState(
        status=status,
        account=data.get("account"),
        redirect_uri=data.get("redirect_uri"),
        last_error=last_error
    )


def reverse_charge(charge_id: str):
    client_token = django_keycloak_auth.clients.get_access_token()
    r = requests.post(
        f"{settings.BILLING_URL}/reverse_charge/", json={
            "id": charge_id
        }, headers={
            "Authorization": f"Bearer {client_token}"
        }
    )
    if r.status_code == 200:
        return None
    else:
        return 'There was an unexpected error'
