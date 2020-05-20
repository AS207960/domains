from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
import grpc
from .. import models, apps

@login_required
def hosts(request):
    user_hosts = models.NameServer.objects.filter(user=request.user)
    hosts_data = []
    error = None
    try:
        with ThreadPoolExecutor() as executor:
            hosts_data = executor.map(
                lambda h: (h.id, apps.epp_client.get_host(h.name_server, h.registry_id)),
                user_hosts
            )
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()

    return render(request, "domains/hosts.html", {
        "hosts": hosts_data,
        "error": error
    })


@login_required
def host(request, host_id):
    user_host = get_object_or_404(models.NameServer, id=host_id)

    if user_host.user != request.user:
        raise PermissionDenied

    error = None
    host_data = None

    try:
        host_data = apps.epp_client.get_host(user_host.name_server, user_host.registry_id)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()

    if request.method == "POST" and request.POST.get("type") == "host_create":
        address_form = forms.HostRegisterForm(request.POST)
        if address_form.is_valid():
            address = ipaddress.ip_address(address_form.cleaned_data['address'])
            ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.UNKNOWN
            if address.version == 4:
                ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.IPv4
            elif address.version == 6:
                ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.IPv6
            try:
                host_data.add_addresses([apps.epp_api.IPAddress(
                    address=address.compressed,
                    ip_type=ip_type
                )])
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
            else:
                return redirect(request.get_full_path())
    else:
        address_form = forms.HostRegisterForm()

    if request.method == "POST" and request.POST.get("type") == "host_delete":
        try:
            address = request.POST.get("address")
            ip_type = int(request.POST.get("ip_type"))
        except ValueError:
            pass
        else:
            try:
                host_data.remove_addresses([apps.epp_api.IPAddress(
                    address=address,
                    ip_type=ip_type
                )])
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
            else:
                return redirect(request.get_full_path())

    return render(request, "domains/host.html", {
        "host": host_data,
        "address_form": address_form,
        "error": error,
        "host_id": user_host.id,
    })


@login_required
def host_delete(request, host_id):
    user_host = get_object_or_404(models.NameServer, id=host_id)

    if user_host.user != request.user:
        raise PermissionDenied

    host_data = apps.epp_client.get_host(user_host.name_server, user_host.registry_id)

    can_delete = apps.epp_api.host_pb2.Linked not in host_data.statuses
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('hosts')

    if request.method == "POST":
        if can_delete and request.POST.get("delete") == "true":
            try:
                pending = apps.epp_client.delete_host(user_host.name_server, user_host.registry_id)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
                return render(request, "domains/error.html", {
                    "error": error,
                    "back_url": referrer
                })

            if not pending:
                user_host.delete()
            return redirect('hosts')

    return render(request, "domains/delete_host.html", {
        "host": host_data,
        "can_delete": can_delete,
        "back_url": referrer
    })


@login_required
def host_create(request, registry_name, host: str):
    error = None
    form = None

    valid = False
    for domain_obj in models.DomainRegistration.objects.filter(user=request.user):
        if host.endswith(domain_obj.domain):
            valid = True
            break

    if not valid:
        raise PermissionDenied

    try:
        available, _ = apps.epp_client.check_host(host, registry_name)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
    else:
        if not available:
            raise Http404

        if request.method == "POST":
            form = forms.HostRegisterForm(request.POST)
            if form.is_valid():
                address = ipaddress.ip_address(form.cleaned_data['address'])
                ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.UNKNOWN
                if address.version == 4:
                    ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.IPv4
                elif address.version == 6:
                    ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.IPv6
                try:
                    apps.epp_client.create_host(host, [apps.epp_api.IPAddress(
                        address=address.compressed,
                        ip_type=ip_type
                    )], registry_name)
                except grpc.RpcError as rpc_error:
                    error = rpc_error.details()
                else:
                    host_obj = models.NameServer(
                        name_server=host,
                        registry_id=registry_name,
                        user=request.user
                    )
                    host_obj.save()

                    return redirect('hosts')
        else:
            form = forms.HostRegisterForm()

    return render(request, "domains/host_form.html", {
        "title": "Create a host object",
        "host": host,
        "host_form": form,
        "error": error
    })