from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import Http404
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import django_keycloak_auth.clients
import ipaddress
import grpc
import uuid
from concurrent.futures import ThreadPoolExecutor
from .. import models, apps, forms, zone_info
from . import billing, gchat_bot


def domain_prices(request):
    zones = list(map(lambda z: {
        "zone": z[0],
        "currency": z[1].pricing.currency,
        "registration": z[1].pricing.representative_registration(),
        "renewal": z[1].pricing.representative_renewal(),
        "restore": z[1].pricing.representative_restore(),
        "transfer": z[1].pricing.representative_transfer(),
    }, zone_info.ZONES))

    return render(request, "domains/domain_prices.html", {
        "domains": zones
    })


@login_required
def domains(request):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domains = models.DomainRegistration.get_object_list(access_token)
    active_domains = user_domains.filter(pending=False, deleted=False)
    deleted_domains = user_domains.filter(deleted=True)
    pending_domains = user_domains.filter(pending=True, deleted=False)
    pending_transfers = models.PendingDomainTransfer.get_object_list(access_token)
    domains_data = []
    error = None
    try:
        with ThreadPoolExecutor() as executor:
            domains_data = list(executor.map(lambda d: (d.id, apps.epp_client.get_domain(d.domain)), active_domains))
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()

    return render(request, "domains/domains.html", {
        "domains": domains_data,
        "deleted_domains": deleted_domains,
        "pending_domains": pending_domains,
        "pending_transfers": pending_transfers,
        "error": error,
        "registration_enabled": settings.REGISTRATION_ENABLED
    })


@login_required
def domain(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    error = None
    domain_data = None
    registrant = None
    admin = None
    billing = None
    tech = None
    host_objs = []

    registrant_form = forms.DomainContactForm(
        user=request.user,
        contact_type='registrant',
        domain_id=domain_id,
    )
    registrant_form.fields['contact'].required = True
    admin_contact_form = forms.DomainContactForm(
        user=request.user,
        contact_type='admin',
        domain_id=domain_id,
    )
    billing_contact_form = forms.DomainContactForm(
        user=request.user,
        contact_type='billing',
        domain_id=domain_id,
    )
    tech_contact_form = forms.DomainContactForm(
        user=request.user,
        contact_type='tech',
        domain_id=domain_id,
    )
    new_host_form = forms.HostSearchForm(
        domain_name=user_domain.domain
    )
    host_object_form = forms.DomainHostObjectForm(
        user=request.user,
        domain_id=domain_id
    )
    host_addr_form = forms.DomainHostAddrForm(
        domain_id=domain_id
    )
    ds_form = forms.DomainDSDataForm(
        domain_id=domain_id
    )
    dnskey_form = forms.DomainDNSKeyDataForm(
        domain_id=domain_id
    )

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)

        if apps.epp_api.rgp_pb2.RedemptionPeriod in domain_data.rgp_state:
            user_domain.deleted = True
            user_domain.save()
            return redirect('domains')

        if request.method == "POST" and request.POST.get("type") == "host_search":
            new_host_form = forms.HostSearchForm(
                request.POST,
                domain_name=user_domain.domain
            )
            if new_host_form.is_valid():
                host = f"{new_host_form.cleaned_data['host']}.{domain_data.name}"
                try:
                    available, reason = apps.epp_client.check_host(host, domain_data.registry_name)
                except grpc.RpcError as rpc_error:
                    error = rpc_error.details()
                else:
                    if not available:
                        if not reason:
                            new_host_form.add_error('host', "Host name unavailable")
                        else:
                            new_host_form.add_error('host', f"Host name unavailable: {reason}")
                    else:
                        return redirect('host_create', host)

        if domain_info.registrant_supported:
            registrant = models.Contact.get_contact(domain_data.registrant, domain_data.registry_name, request.user)
            registrant_form.set_cur_id(cur_id=domain_data.registrant, registry_id=domain_data.registry_name)
        else:
            registrant = user_domain.registrant_contact
            registrant_form.fields['contact'].value = user_domain.registrant_contact.id

        if domain_data.admin:
            admin = models.Contact.get_contact(domain_data.admin.contact_id, domain_data.registry_name, request.user)
            admin_contact_form.set_cur_id(cur_id=domain_data.admin.contact_id, registry_id=domain_data.registry_name)
        elif user_domain.admin_contact:
            admin = user_domain.admin_contact
            admin_contact_form.fields['contact'].value = user_domain.admin_contact.id

        if domain_data.billing:
            billing = models.Contact.get_contact(domain_data.billing.contact_id, domain_data.registry_name, request.user)
            billing_contact_form.set_cur_id(cur_id=domain_data.billing.contact_id, registry_id=domain_data.registry_name)
        elif user_domain.billing_contact:
            billing = user_domain.billing_contact
            billing_contact_form.fields['contact'].value = user_domain.billing_contact.id

        if domain_data.tech:
            tech = models.Contact.get_contact(domain_data.tech.contact_id, domain_data.registry_name, request.user)
            tech_contact_form.set_cur_id(cur_id=domain_data.tech.contact_id, registry_id=domain_data.registry_name)
        elif user_domain.admin_contact:
            tech = user_domain.tech_contact
            tech_contact_form.fields['contact'].value = user_domain.tech_contact.id

        admin_contact_form.fields['contact'].required = domain_info.admin_required
        billing_contact_form.fields['contact'].required = domain_info.billing_required
        tech_contact_form.fields['contact'].required = domain_info.tech_required

        host_objs = list(map(lambda h: models.NameServer.get_name_server(
            h,
            domain_data.registry_name,
            request.user
        ), domain_data.hosts))

        host_object_form = forms.DomainHostObjectForm(
            user=request.user,
            domain_id=domain_id,
            registry_id=domain_data.registry_name
        )
    except grpc.RpcError as rpc_error:
        return render(request, "domains/error.html", {
            "error": rpc_error.details(),
            "back_url": referrer
        })

    return render(request, "domains/domain.html", {
        "domain_id": domain_id,
        "domain_info": domain_info,
        "domain_obj": user_domain,
        "domain": domain_data,
        "error": error,
        "registrant": registrant,
        "admin": admin,
        "billing": billing,
        "tech": tech,
        "hosts": host_objs,
        "registrant_form": registrant_form,
        "admin_contact_form": admin_contact_form,
        "billing_contact_form": billing_contact_form,
        "tech_contact_form": tech_contact_form,
        "new_host_form": new_host_form,
        "host_object_form": host_object_form,
        "host_addr_form": host_addr_form,
        "ds_form": ds_form,
        "dnskey_form": dnskey_form,
        "registration_enabled": settings.REGISTRATION_ENABLED
    })


@login_required
@require_POST
def update_domain_contact(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    form = forms.DomainContactForm(
        request.POST,
        user=request.user,
        contact_type=None,
        domain_id=user_domain.id,
    )

    contact_type = request.POST.get("type")

    if contact_type == 'admin':
        form.fields['contact'].required = domain_info.admin_required
    elif contact_type == 'billing':
        form.fields['contact'].required = domain_info.billing_required
    elif contact_type == 'tech':
        form.fields['contact'].required = domain_info.tech_required

    if form.is_valid():
        contact_type = form.cleaned_data['type']
        try:
            contact = form.cleaned_data['contact']
            if contact_type != "registrant":
                if contact_type == 'admin':
                    user_domain.admin_contact = contact
                    if domain_info.admin_supported:
                        if contact:
                            contact_id = contact.get_registry_id(domain_data.registry_name)
                            domain_data.set_contact(contact_type, contact_id.registry_contact_id)
                        else:
                            domain_data.set_contact(contact_type, None)
                elif contact_type == 'tech':
                    user_domain.tech_contact = contact
                    if domain_info.tech_supported:
                        if contact:
                            contact_id = contact.get_registry_id(domain_data.registry_name)
                            domain_data.set_contact(contact_type, contact_id.registry_contact_id)
                        else:
                            domain_data.set_contact(contact_type, None)
                elif contact_type == 'billing':
                    user_domain.billing_contact = contact
                    if domain_info.billing_supported:
                        if contact:
                            contact_id = contact.get_registry_id(domain_data.registry_name)
                            domain_data.set_contact(contact_type, contact_id.registry_contact_id)
                        else:
                            domain_data.set_contact(contact_type, None)

                user_domain.save()
            elif domain_info.registrant_change_supported:
                if domain_info.registrant_supported:
                    contact_id = contact.get_registry_id(domain_data.registry_name)
                    domain_data.set_registrant(contact_id.registry_contact_id)

                user_domain.registrant_contact = contact
                user_domain.save()
        except grpc.RpcError as rpc_error:
            error = rpc_error.details()
            return render(request, "domains/error.html", {
                "error": error,
                "back_url": referrer
            })

    return redirect(referrer)


@login_required
@require_POST
def domain_block_transfer(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    if domain_info.transfer_lock_supported:
        try:
            domain_data.add_states([apps.epp_api.DomainStatus(status=3)])
        except grpc.RpcError as rpc_error:
            error = rpc_error.details()
            return render(request, "domains/error.html", {
                "error": error,
                "back_url": referrer
            })

    return redirect(referrer)


@login_required
@require_POST
def domain_del_block_transfer(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    if domain_info.transfer_lock_supported:
        try:
            domain_data.del_states([apps.epp_api.DomainStatus(status=3)])
        except grpc.RpcError as rpc_error:
            error = rpc_error.details()
            return render(request, "domains/error.html", {
                "error": error,
                "back_url": referrer
            })

    return redirect(referrer)


@login_required
def domain_regen_transfer_code(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    new_auth_info = models.make_secret()

    try:
        domain_data.set_auth_info(new_auth_info)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    user_domain.auth_info = new_auth_info
    user_domain.save()

    return redirect(referrer)


@login_required
@require_POST
def add_domain_host_obj(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    form = forms.DomainHostObjectForm(
        request.POST,
        user=request.user,
        domain_id=user_domain.id,
        registry_id=domain_data.registry_name
    )
    if form.is_valid():
        host_obj = form.cleaned_data['host']

        try:
            host_available, _ = apps.epp_client.check_host(host_obj, domain_data.registry_name)
        except grpc.RpcError as rpc_error:
            error = rpc_error.details()
            return render(request, "domains/error.html", {
                "error": error,
                "back_url": referrer
            })

        if host_available:
            try:
                apps.epp_client.create_host(host_obj, [], domain_data.registry_name)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
                return render(request, "domains/error.html", {
                    "error": error,
                    "back_url": referrer
                })

        try:
            domain_data.add_host_objs([host_obj])
        except grpc.RpcError as rpc_error:
            error = rpc_error.details()
            return render(request, "domains/error.html", {
                "error": error,
                "back_url": referrer
            })

    return redirect(referrer)


@login_required
@require_POST
def add_domain_host_addr(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    form = forms.DomainHostAddrForm(
        request.POST,
        domain_id=user_domain.id
    )
    if form.is_valid():
        host_name = form.cleaned_data['host']
        host_addr = form.cleaned_data['address']
        if host_addr:
            address = ipaddress.ip_address(host_addr)
            ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.UNKNOWN
            if address.version == 4:
                ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.IPv4
            elif address.version == 6:
                ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.IPv6
            addrs = [apps.epp_qapi.IPAddress(
                address=address.compressed,
                ip_type=ip_type
            )]
        else:
            addrs = []
        try:
            domain_data.add_host_addrs([(host_name, addrs)])
        except grpc.RpcError as rpc_error:
            error = rpc_error.details()
            return render(request, "domains/error.html", {
                "error": error,
                "back_url": referrer
            })

    return redirect(referrer)


@login_required
@require_POST
def add_domain_ds_data(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    form = forms.DomainDSDataForm(
        request.POST,
        domain_id=domain_id
    )
    if form.is_valid():
        try:
            domain_data.add_ds_data([apps.epp_api.SecDNSDSData(
                key_tag=form.cleaned_data['key_tag'],
                algorithm=form.cleaned_data['algorithm'],
                digest_type=form.cleaned_data['digest_type'],
                digest=form.cleaned_data['digest'],
                key_data=None
            )])
        except grpc.RpcError as rpc_error:
            error = rpc_error.details()
            return render(request, "domains/error.html", {
                "error": error,
                "back_url": referrer
            })

    return redirect(referrer)


@login_required
@require_POST
def delete_domain_ds_data(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    try:
        domain_data.del_ds_data([apps.epp_api.SecDNSDSData(
            key_tag=int(request.POST.get('key_tag')),
            algorithm=int(request.POST.get('algorithm')),
            digest_type=int(request.POST.get('digest_type')),
            digest=request.POST.get('digest'),
            key_data=None
        )])
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    return redirect(referrer)


@login_required
@require_POST
def add_domain_dnskey_data(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    form = forms.DomainDNSKeyDataForm(
        request.POST,
        domain_id=domain_id
    )
    if form.is_valid():
        try:
            domain_data.add_dnskey_data([apps.epp_api.SecDNSKeyData(
                flags=form.cleaned_data['flags'],
                protocol=form.cleaned_data['protocol'],
                algorithm=form.cleaned_data['algorithm'],
                public_key=form.cleaned_data['public_key'],
            )])
        except grpc.RpcError as rpc_error:
            error = rpc_error.details()
            return render(request, "domains/error.html", {
                "error": error,
                "back_url": referrer
            })

    return redirect(referrer)


@login_required
@require_POST
def delete_domain_dnskey_data(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    try:
        domain_data.del_dnskey_data([apps.epp_api.SecDNSKeyData(
            flags=int(request.POST.get('flags')),
            protocol=int(request.POST.get('protocol')),
            algorithm=int(request.POST.get('algorithm')),
            public_key=request.POST.get('public_key'),
        )])
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    return redirect(referrer)


@login_required
def delete_domain_sec_dns(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    try:
        domain_data.del_secdns_all()
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    return redirect(referrer)


@login_required
def delete_domain_host_obj(request, domain_id, host_name):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    try:
        domain_data.del_host_objs([host_name])
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    return redirect(referrer)


@login_required
def domain_search(request):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not settings.REGISTRATION_ENABLED or not models.DomainRegistration.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    error = None

    if request.method == "POST":
        form = forms.DomainSearchForm(request.POST)
        if form.is_valid():
            zone, sld = zone_info.get_domain_info(form.cleaned_data['domain'])
            if zone:
                pending_domain = models.DomainRegistration.objects.filter(
                    domain=form.cleaned_data['domain']
                ).first()
                if pending_domain:
                    form.add_error('domain', "Domain unavailable")
                else:
                    try:
                        available, reason, _ = apps.epp_client.check_domain(form.cleaned_data['domain'])
                    except grpc.RpcError as rpc_error:
                        error = rpc_error.details()
                    else:
                        if not available:
                            if not reason:
                                form.add_error('domain', "Domain unavailable")
                            else:
                                form.add_error('domain', f"Domain unavailable: {reason}")
                        else:
                            return redirect('domain_register', form.cleaned_data['domain'])
            else:
                form.add_error('domain', "Unsupported or invalid domain")
    else:
        form = forms.DomainSearchForm()

    return render(request, "domains/domain_search.html", {
        "domain_form": form,
        "error": error
    })


@login_required
def domain_register(request, domain_name):
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    error = None

    zone, sld = zone_info.get_domain_info(domain_name)
    if not zone:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone_price, registry_name = zone.pricing, zone.registry
    price_decimal = zone_price.representative_registration()

    if request.method == "POST":
        form = forms.DomainRegisterForm(
            request.POST,
            zone=zone,
            user=request.user
        )
        if form.is_valid():
            pending_domain = models.DomainRegistration.objects.filter(
                domain=domain_name
            ).first()
            if pending_domain:
                raise Http404
            try:
                available, _, registry_id = apps.epp_client.check_domain(domain_name)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
            else:
                if not available:
                    raise Http404

                registrant = form.cleaned_data['registrant']
                admin_contact = form.cleaned_data['admin']
                billing_contact = form.cleaned_data['billing']
                tech_contact = form.cleaned_data['tech']
                period = form.cleaned_data['period']

                success = True
                for host in ('ns1.as207960.net', 'ns2.as207960.net'):
                    try:
                        host_available, _ = apps.epp_client.check_host(host, registry_id)
                    except grpc.RpcError as rpc_error:
                        error = rpc_error.details()
                        success = False
                    else:
                        if host_available:
                            try:
                                apps.epp_client.create_host(host, [], registry_id)
                            except grpc.RpcError as rpc_error:
                                error = rpc_error.details()
                                success = False

                if success:
                    request.session['period_unit'] = period.unit
                    request.session['period_value'] = period.value
                    request.session['registrant_id'] = str(registrant.id)
                    request.session['admin_id'] = str(admin_contact.id) if admin_contact else None
                    request.session['billing_id'] = str(billing_contact.id) if billing_contact else None
                    request.session['tech_id'] = str(tech_contact.id) if tech_contact else None
                    return redirect('domain_register_confirm', domain_name)
    else:
        form = forms.DomainRegisterForm(
            zone=zone,
            user=request.user
        )

    return render(request, "domains/domain_form.html", {
        "domain_form": form,
        "domain_name": domain_name,
        "price_decimal": price_decimal,
        "currency": zone_price.currency,
        "zone_info": zone,
        "error": error
    })


@login_required
def domain_register_confirm(request, domain_name):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not settings.REGISTRATION_ENABLED or not models.DomainRegistration.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone, sld = zone_info.get_domain_info(domain_name)
    if not zone:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    period = apps.epp_api.Period(
        value=request.session['period_value'],
        unit=request.session['period_unit']
    )
    zone_price, registry_name = zone.pricing, zone.registry
    domain_id = uuid.uuid4()
    auth_info = models.make_secret()

    billing_value = zone_price.registration(sld, unit=period.unit, value=period.value)
    if billing_value is None:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    if request.method == "POST" and request.POST.get("register") == "true":
        registrant = models.Contact.objects.get(id=request.session['registrant_id'])
        admin_id = request.session.get('admin_id')
        billing_id = request.session.get('billing_id')
        tech_id = request.session.get('tech_id')
        admin_contact = models.Contact.objects.get(id=admin_id) if admin_id else None
        billing_contact = models.Contact.objects.get(id=billing_id) if billing_id else None
        tech_contact = models.Contact.objects.get(id=tech_id) if tech_id else None

        try:
            _, _, registry_id = apps.epp_client.check_domain(domain_name)
        except grpc.RpcError as rpc_error:
            return render(request, "domains/error.html", {
                "error": rpc_error.details(),
                "back_url": referrer
            })

        billing_error = billing.charge_account(
            request.user.username,
            billing_value,
            f"{domain_name} domain registration",
            f"dm_{domain_id}"
        )
        if billing_error:
            return render(request, "domains/error.html", {
                "error": billing_error,
                "back_url": referrer
            })
        if zone.direct_registration_supported:
            try:
                contact_objs = []
                if zone.admin_supported and admin_contact:
                    contact_objs.append(apps.epp_api.DomainContact(
                        contact_type="admin",
                        contact_id=admin_contact.get_registry_id(registry_id).registry_contact_id
                    ))
                if zone.billing_supported and billing_contact:
                    contact_objs.append(apps.epp_api.DomainContact(
                        contact_type="billing",
                        contact_id=billing_contact.get_registry_id(registry_id).registry_contact_id
                    ))
                if zone.tech_supported and tech_contact:
                    contact_objs.append(apps.epp_api.DomainContact(
                        contact_type="tech",
                        contact_id=tech_contact.get_registry_id(registry_id).registry_contact_id
                    ))

                pending, _, _, _ = apps.epp_client.create_domain(
                    domain=domain_name,
                    period=period,
                    registrant=registrant.get_registry_id(registry_id).registry_contact_id,
                    contacts=contact_objs,
                    name_servers=[apps.epp_api.DomainNameServer(
                        host_obj='ns1.as207960.net',
                        host_name=None,
                        address=[]
                    ), apps.epp_api.DomainNameServer(
                        host_obj='ns2.as207960.net',
                        host_name=None,
                        address=[]
                    )],
                    auth_info=auth_info,
                )
            except grpc.RpcError as rpc_error:
                billing.charge_account(
                    request.user.username,
                    -billing_value,
                    f"{domain_name} domain registration",
                    f"dm_{domain_id}"
                )
                return render(request, "domains/error.html", {
                    "error": rpc_error.details(),
                    "back_url": referrer
                })
        else:
            pending = True

        del request.session['period_unit']
        del request.session['period_value']
        del request.session['registrant_id']
        del request.session['admin_id']
        del request.session['billing_id']
        del request.session['tech_id']

        domain_obj = models.DomainRegistration(
            id=domain_id,
            domain=domain_name,
            user=request.user,
            auth_info=auth_info,
            registrant_contact=registrant,
            admin_contact=admin_contact,
            tech_contact=tech_contact,
            billing_contact=billing_contact
        )
        if pending:
            domain_obj.pending = True
            domain_obj.save()
            if not zone.direct_registration_supported:
                gchat_bot.request_registration(domain_obj, registry_id, period)
            else:
                gchat_bot.notify_registration(domain_obj, registry_id, period)

            return render(request, "domains/domain_pending.html", {
                "domain_name": domain_name
            })
        else:
            domain_obj.save()
            gchat_bot.notify_registration(domain_obj, registry_id, period)
            return redirect('domain', domain_obj.id)

    return render(request, "domains/register_domain_confirm.html", {
        "domain": domain_name,
        "price_decimal": billing_value,
        "back_url": referrer,
    })


@login_required
def delete_domain(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'delete'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    can_delete = True

    if request.method == "POST":
        if can_delete and request.POST.get("delete") == "true":
            try:
                pending, _registry_name, _transaction_id, _fee_data = apps.epp_client.delete_domain(user_domain.domain)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
                return render(request, "domains/error.html", {
                    "error": error,
                    "back_url": referrer
                })

            if not (domain_info.restore_supported or not pending):
                user_domain.delete()
            else:
                user_domain.deleted = True
                user_domain.save()
            return redirect('domains')

    return render(request, "domains/delete_domain.html", {
        "domain": user_domain,
        "can_delete": can_delete,
        "back_url": referrer
    })


@login_required
def renew_domain(request, domain_id):
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)

    zone, sld = zone_info.get_domain_info(user_domain.domain)
    if not zone:
        raise Http404

    zone_price, _ = zone.pricing, zone.registry
    price_decimal = zone_price.representative_renewal()

    if request.method == "POST":
        form = forms.DomainRenewForm(
            request.POST,
            zone_info=zone
        )

        if form.is_valid():
            period = form.cleaned_data['period']
            request.session['period_unit'] = period.unit
            request.session['period_value'] = period.value

            return redirect('renew_domain_confirm', domain_id)
    else:
        form = forms.DomainRenewForm(zone_info=zone)

    return render(request, "domains/renew_domain.html", {
        "domain": user_domain,
        "domain_name": user_domain.domain,
        "zone_info": zone,
        "domain_form": form,
        "price_decimal": price_decimal,
        "currency": zone_price.currency,
    })


@login_required
def renew_domain_confirm(request, domain_id):
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not settings.REGISTRATION_ENABLED:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=False)

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone, sld = zone_info.get_domain_info(user_domain.domain)
    if not zone:
        raise Http404

    zone_price, _ = zone.pricing, zone.registry

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    period = apps.epp_api.Period(
        value=request.session['period_value'],
        unit=request.session['period_unit']
    )

    billing_value = zone_price.renewal(sld, unit=period.unit, value=period.value)
    if billing_value is None:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    if request.method == "POST" and request.POST.get("renew") == "true":
        billing_error = billing.charge_account(
            request.user.username,
            billing_value,
            f"{user_domain.domain} domain renewal",
            f"dm_renew_{domain_id}"
        )
        if billing_error:
            return render(request, "domains/error.html", {
                "error": billing_error,
                "back_url": referrer
            })

        try:
            _pending, _new_expiry, registry_id = apps.epp_client.renew_domain(
                user_domain.domain, period, domain_data.expiry_date
            )
        except grpc.RpcError as rpc_error:
            billing.charge_account(
                request.user.username,
                -billing_value,
                f"{user_domain.domain} domain renewal",
                f"dm_renew_{domain_id}"
            )
            error = rpc_error.details()
            return render(request, "domains/error.html", {
                "error": error,
                "back_url": referrer
            })

        del request.session['period_unit']
        del request.session['period_value']

        gchat_bot.notify_renew(user_domain, registry_id, period)

        return redirect('domain', domain_id)

    return render(request, "domains/renew_domain_confirm.html", {
        "domain": user_domain,
        "price_decimal": billing_value,
        "back_url": referrer,
    })


@login_required
def restore_domain(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, pending=False, deleted=True)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone, sld = zone_info.get_domain_info(user_domain.domain)
    if not zone:
        raise Http404

    zone_price, _ = zone.pricing, zone.registry
    billing_value = zone_price.restore(sld)

    if request.method == "POST" and request.POST.get("restore") == "true":
        billing_error = billing.charge_account(
            request.user.username,
            billing_value,
            f"{user_domain.domain} domain restore",
            f"dm_restore_{domain_id}"
        )
        if billing_error:
            return render(request, "domains/error.html", {
                "error": billing_error,
                "back_url": reverse('domain', args=(domain_id,))
            })

        if zone.direct_restore_supported:
            try:
                pending, registry_id = apps.epp_client.restore_domain(user_domain.domain)
                user_domain.deleted = pending
                user_domain.pending = pending
                user_domain.save()
                gchat_bot.notify_restore(user_domain, registry_id)
            except grpc.RpcError as rpc_error:
                billing.charge_account(
                    request.user.username,
                    -billing_value,
                    f"{user_domain.domain} domain restore",
                    f"dm_restore_{domain_id}"
                )
                error = rpc_error.details()
                return render(request, "domains/error.html", {
                    "error": error,
                    "back_url": reverse('domain', args=(domain_id,))
                })
        else:
            gchat_bot.request_restore(user_domain)
            pending = True

        if pending:
            return render(request, "domains/domain_restore_pending.html", {
                "domain_name": user_domain.domain
            })
        else:
            return redirect('domain', domain_id)

    return render(request, "domains/restore_domain.html", {
        "domain": user_domain,
        "price_decimal": billing_value
    })


@login_required
def domain_transfer_query(request):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not settings.REGISTRATION_ENABLED or not models.DomainRegistration.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    error = None

    if request.method == "POST":
        form = forms.DomainSearchForm(request.POST)

        if form.is_valid():
            zone, sld = zone_info.get_domain_info(form.cleaned_data['domain'])
            if zone:
                if not zone.transfer_supported:
                    form.add_error('domain', "Extension not yet supported for transfers")
                else:
                    try:
                        if zone.pre_transfer_query_supported:
                            available, _, _ = apps.epp_client.check_domain(form.cleaned_data['domain'])
                        else:
                            available = False
                    except grpc.RpcError as rpc_error:
                        error = rpc_error.details()
                    else:
                        if not available:
                            if zone.pre_transfer_query_supported:
                                try:
                                    domain_data = apps.epp_client.get_domain(form.cleaned_data['domain'])
                                except grpc.RpcError as rpc_error:
                                    error = rpc_error.details()
                                else:
                                    if any(s in domain_data.statuses for s in (3, 7, 8, 10, 15)):
                                        form.add_error('domain', "Domain not eligible for transfer")
                                    else:
                                        return redirect('domain_transfer', form.cleaned_data['domain'])
                            else:
                                return redirect('domain_transfer', form.cleaned_data['domain'])
                        else:
                            form.add_error('domain', "Domain does not exist")
            else:
                form.add_error('domain', "Unsupported or invalid domain")

    else:
        form = forms.DomainSearchForm()

    return render(request, "domains/domain_transfer_query.html", {
        "domain_form": form,
        "error": error
    })


@login_required
def domain_transfer(request, domain_name):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not settings.REGISTRATION_ENABLED or not models.DomainRegistration.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    error = None

    zone, sld = zone_info.get_domain_info(domain_name)
    if not zone or not zone.transfer_supported:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone_price, registry_name = zone.pricing, zone.registry
    price_decimal = zone_price.transfer(sld)

    if request.method == "POST":
        form = forms.DomainTransferForm(request.POST, zone=zone, user=request.user)

        if form.is_valid():
            try:
                available, _, registry_id = apps.epp_client.check_domain(domain_name)
                if not zone.pre_transfer_query_supported:
                    available = False
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
            else:
                if not available:
                    domain_id = uuid.uuid4()
                    billing_error = billing.charge_account(
                        request.user.username,
                        price_decimal,
                        f"{domain_name} domain transfer",
                        f"dm_transfer_{domain_id}"
                    )
                    if billing_error:
                        error = billing_error
                    else:
                        registrant = form.cleaned_data['registrant']  # type: models.Contact
                        admin_contact = form.cleaned_data['admin']  # type: models.Contact
                        tech_contact = form.cleaned_data['tech']  # type: models.Contact
                        billing_contact = form.cleaned_data['billing']  # type: models.Contact

                        if zone.direct_transfer_supported:
                            try:
                                transfer_data = apps.epp_client.transfer_request_domain(
                                    domain_name,
                                    form.cleaned_data['auth_code']
                                )
                            except grpc.RpcError as rpc_error:
                                billing.charge_account(
                                    request.user.username,
                                    -price_decimal,
                                    f"{domain_name} domain transfer",
                                    f"dm_transfer_{domain_id}"
                                )
                                error = rpc_error.details()
                            else:
                                if transfer_data.status == 5:
                                    domain_data = apps.epp_client.get_domain(domain_name)
                                    registrant_id = registrant.get_registry_id(registry_id)
                                    domain_data.set_registrant(registrant_id.registry_contact_id)
                                    if tech_contact and zone.tech_supported:
                                        tech_contact_id = tech_contact.get_registry_id(registry_id)
                                        domain_data.set_tech(tech_contact_id.registry_contact_id)
                                    if admin_contact and zone.admin_supported:
                                        admin_contact_id = admin_contact.get_registry_id(registry_id)
                                        domain_data.set_admin(admin_contact_id.registry_contact_id)
                                    if billing_contact and zone.billing_supported:
                                        billing_contact_id = billing_contact.get_registry_id(registry_id)
                                        domain_data.set_billing(billing_contact_id.registry_contact_id)

                                    domain_obj = models.DomainRegistration(
                                        id=domain_id,
                                        domain=domain_name,
                                        user=request.user,
                                        auth_info=form.cleaned_data['auth_code'],
                                        registrant_contact=registrant,
                                        admin_contact=admin_contact,
                                        tech_contact=tech_contact,
                                        billing_contact=billing_contact
                                    )
                                    domain_obj.save()
                                    gchat_bot.notify_transfer(domain_obj, registry_id)
                                    return redirect('domain', domain_obj.id)
                                else:
                                    domain_obj = models.PendingDomainTransfer(
                                        id=domain_id,
                                        domain=domain_name,
                                        user=request.user,
                                        auth_info=form.cleaned_data['auth_code'],
                                        registrant_contact=registrant,
                                        admin_contact=admin_contact,
                                        tech_contact=tech_contact,
                                        billing_contact=billing_contact
                                    )
                                    domain_obj.save()
                                    gchat_bot.notify_transfer_pending(domain_obj, registry_id)
                                    return render(request, "domains/domain_transfer_pending.html", {
                                        "domain_name": domain_name
                                    })
                        else:
                            domain_obj = models.PendingDomainTransfer(
                                id=domain_id,
                                domain=domain_name,
                                user=request.user,
                                auth_info=form.cleaned_data['auth_code'],
                                registrant_contact=registrant,
                                admin_contact=admin_contact,
                                tech_contact=tech_contact,
                                billing_contact=billing_contact
                            )
                            domain_obj.save()
                            gchat_bot.request_transfer(domain_obj, registry_id)
                            return render(request, "domains/domain_transfer_pending.html", {
                                "domain_name": domain_name
                            })
                else:
                    raise Http404
    else:
        form = forms.DomainTransferForm(zone=zone, user=request.user)

    return render(request, "domains/domain_transfer.html", {
        "domain_form": form,
        "domain_name": domain_name,
        "price_decimal": price_decimal,
        "zone_info": zone,
        "error": error
    })
