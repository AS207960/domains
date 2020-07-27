from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required, permission_required
from .. import apps, forms
import grpc


def catch_epp_error(fun):
    def new_fun(request, *args, **kwargs):
        referrer = request.META.get("HTTP_REFERER")
        referrer = referrer if referrer else reverse('admin_index')

        try:
            return fun(request, *args, **kwargs)
        except grpc.RpcError as rpc_error:
            return render(request, "domains/error.html", {
                "error": rpc_error.details(),
                "back_url": referrer
            })

    return new_fun


@login_required
@permission_required('domains.access_eppclient', raise_exception=True)
@catch_epp_error
def index(request):
    return render(request, "domains/admin/index.html")


@login_required
@permission_required('domains.access_eppclient', raise_exception=True)
@catch_epp_error
def domain_info(request):
    domain = None

    if request.method == "POST":
        form = forms.DomainSearchForm(request.POST)
        form.helper.form_action = request.get_full_path()
        if form.is_valid():
            domain = apps.epp_client.get_domain(form.cleaned_data["domain"])
    else:
        form = forms.DomainSearchForm()
        form.helper.form_action = request.get_full_path()

    return render(request, "domains/admin/domain_info.html", {
        "domain_form": form,
        "domain_info": domain
    })


@login_required
@permission_required('domains.access_eppclient', raise_exception=True)
@catch_epp_error
def domain_transfer_info(request):
    domain = None

    if request.method == "POST":
        form = forms.DomainSearchForm(request.POST)
        form.helper.form_action = request.get_full_path()
        if form.is_valid():
            domain = apps.epp_client.transfer_query_domain(form.cleaned_data["domain"])
    else:
        form = forms.DomainSearchForm()
        form.helper.form_action = request.get_full_path()

    return render(request, "domains/admin/domain_transfer_info.html", {
        "domain_form": form,
        "transfer_info": domain,
        "title": "Domain transfer info"
    })


@login_required
@permission_required('domains.access_eppclient', raise_exception=True)
@catch_epp_error
def domain_transfer_request(request):
    domain = None

    if request.method == "POST":
        form = forms.AdminDomainTransferForm(request.POST)
        form.helper.form_action = request.get_full_path()
        if form.is_valid():
            domain = apps.epp_client.transfer_request_domain(
                form.cleaned_data["domain"], form.cleaned_data["auth_code"], form.cleaned_data["period"]
            )
    else:
        form = forms.AdminDomainTransferForm()
        form.helper.form_action = request.get_full_path()

    return render(request, "domains/admin/domain_transfer_info.html", {
        "domain_form": form,
        "transfer_info": domain,
        "title": "Domain transfer request"
    })


@login_required
@permission_required('domains.access_eppclient', raise_exception=True)
@catch_epp_error
def balance(request, registry_name):
    info = apps.epp_client.stub.BalanceInfo(apps.epp_api.epp_pb2.RegistryInfo(
        registry_name=registry_name
    ))
    return render(request, "domains/admin/balance.html", {
        "balance": {
            "balance": info.balance,
            "credit_limit": info.credit_limit.value if info.HasField("credit_limit") else None,
            "available_credit": info.available_credit.value if info.HasField("available_credit") else None,
            "fixed_credit_threshold": info.fixed_credit_threshold.value
            if info.HasField("fixed_credit_threshold") else None,
            "percentage_credit_threshold": info.percentage_credit_threshold.value
            if info.HasField("percentage_credit_threshold") else None,
            "currency": info.currency
        },
        "registry": registry_name
    })


@login_required
@permission_required('domains.access_eppclient', raise_exception=True)
@catch_epp_error
def nominet_tags(request):
    info = apps.epp_client.stub.NominetTagList(apps.epp_api.epp_pb2.RegistryInfo(
        registry_name='nominet'
    ))
    return render(request, "domains/admin/nominet_tags.html", {
        "tags": list(map(lambda t: {
            "tag": t.tag,
            "name": t.name,
            "trading_name": t.trading_name.value if t.HasField("trading_name") else None,
            "handshake": t.handshake
        }, info.tags))
    })
