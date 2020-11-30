from django.conf import settings
import django_keycloak_auth.clients
import decimal
import requests
import dataclasses
import typing
import json
import uuid
import retry
from ..proto import billing_pb2
from .. import apps
import google.protobuf.wrappers_pb2


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
                   off_session=True, return_uri=None, notif_queue=None) -> ChargeResult:
    charge_request = billing_pb2.BillingRequest(
        charge_user=billing_pb2.ChargeUserRequest(
            amount=int(decimal.Decimal(100) * amount),
            id=charge_id,
            descriptor=descriptor,
            can_reject=can_reject,
            off_session=off_session,
            user_id=username,
            return_uri=google.protobuf.wrappers_pb2.StringValue(
                value=return_uri
            ) if return_uri else None,
            notif_queue=google.protobuf.wrappers_pb2.StringValue(
                value=notif_queue
            ) if notif_queue else None
        )
    )
    charge_response = billing_pb2.ChargeUserResponse()
    charge_response.ParseFromString(apps.rpc_client.call('billing_rpc', charge_request.SerializeToString()))

    if charge_response.result == billing_pb2.ChargeUserResponse.SUCCESS:
        return ChargeResult(
            success=True,
            error=None,
            redirect_uri=None,
            charge_state_id=charge_response.charge_state_id
        )
    elif charge_response.result == billing_pb2.ChargeUserResponse.REDIRECT:
        return ChargeResult(
            success=False,
            error=None,
            redirect_uri=charge_response.redirect_uri,
            charge_state_id=charge_response.charge_state_id
        )
    elif charge_response.result == billing_pb2.ChargeUserResponse.FAIL:
        return ChargeResult(
            success=False,
            error=charge_response.message,
            redirect_uri=None,
            charge_state_id=charge_response.charge_state_id
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
    if status not in ("unknown", "pending", "processing", "failed", "completed"):
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

    def run_request(*args, **kwargs):
        r = requests.post(*args, **kwargs)
        r.raise_for_status()

    retry.api.retry_call(run_request, fargs=(
        f"{settings.BILLING_URL}/reverse_charge/",
    ), fkwargs={
        "json": {
            "id": charge_id
        },
        "headers": {
            "Authorization": f"Bearer {client_token}",
            "Idempotency-Key": str(uuid.uuid4())
        },
        "timeout": 5
    }, delay=1, tries=10)
