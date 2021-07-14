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
from django.views.decorators.http import require_POST
from django.shortcuts import redirect


@require_POST
def update_country(request):
    if "country_update" in request.POST:
        request.session["selected_billing_country"] = request.POST["country_update"]

    if "HTTP_REFERER" in request.META:
        return redirect(request.META["HTTP_REFERER"])
    else:
        return redirect('index')


@dataclasses.dataclass
class Price:
    amount: decimal.Decimal
    amount_inc_vat: decimal.Decimal
    taxable: bool
    country: str
    currency: str


def convert_currency(
        amount: decimal.Decimal, source_currency: str, username: typing.Optional[str], remote_ip: typing.Optional[str],
        selected_country: typing.Optional[str], timeout=0,
) -> Price:
    msg = billing_pb2.BillingRequest(
        convert_currency=billing_pb2.ConvertCurrencyRequest(
            from_currency=source_currency,
            to_currency="GBP",
            amount=int(round(amount * decimal.Decimal(100))),
            username=google.protobuf.wrappers_pb2.StringValue(
                value=username
            ) if username else None,
            remote_ip=google.protobuf.wrappers_pb2.StringValue(
                value=str(remote_ip)
            ) if remote_ip else None,
            country_selection=google.protobuf.wrappers_pb2.StringValue(
                value=selected_country
            ) if selected_country else None
        )
    )
    msg_response = billing_pb2.ConvertCurrencyResponse()
    msg_response.ParseFromString(apps.rpc_client.call('billing_rpc', msg.SerializeToString(), timeout=timeout))

    amount = (decimal.Decimal(msg_response.amount) / decimal.Decimal(100)).quantize(decimal.Decimal('1.00'))
    amount_inc_vat = (decimal.Decimal(msg_response.amount_inc_vat) / decimal.Decimal(100)).quantize(decimal.Decimal('1.00'))
    return Price(
        amount=amount,
        amount_inc_vat=amount_inc_vat,
        taxable=msg_response.taxable,
        country=msg_response.used_country,
        currency="GBP"
    )


@dataclasses.dataclass
class ChargeResult:
    success: bool
    charge_state_id: typing.Optional[str]
    error: typing.Optional[str]
    redirect_uri: typing.Optional[str]
    immediate_completion: bool


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
            charge_state_id=charge_response.charge_state_id,
            immediate_completion=charge_response.state == billing_pb2.COMPLETED
        )
    elif charge_response.result == billing_pb2.ChargeUserResponse.REDIRECT:
        return ChargeResult(
            success=False,
            error=None,
            redirect_uri=charge_response.redirect_uri,
            charge_state_id=charge_response.charge_state_id,
            immediate_completion=False
        )
    elif charge_response.result == billing_pb2.ChargeUserResponse.FAIL:
        return ChargeResult(
            success=False,
            error=charge_response.message,
            redirect_uri=None,
            charge_state_id=charge_response.charge_state_id,
            immediate_completion=False
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
