from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required, permission_required
from .. import apps, forms
import grpc


def catch_epp_error(fun):
    def new_fun(request, *args, **kwargs):
        referrer = request.META.get("HTTP_REFERER")
        referrer = referrer if referrer else reverse('admin_indeb')

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
        if form.is_valid():
            domain = apps.epp_client.get_domain(form.cleaned_data["domain"])
    else:
        form = forms.DomainSearchForm()

    return render(request, "domains/admin/domain_info.html", {
        "domain_form": form,
        "domain_info": domain
    })


@login_required
@permission_required('domains.access_eppclient', raise_exception=True)
@catch_epp_error
def balance_switch(request):
    info = apps.epp_client.stub.BalanceInfo(apps.epp_api.epp_pb2.RegistryInfo(
        registry_name='switch'
    ))
    return render(request, "domains/admin/balance_switch.html", {
        "balance": info.balance,
        "currency": info.currency
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
