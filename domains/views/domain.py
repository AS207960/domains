from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import django_keycloak_auth.clients
import ipaddress
import grpc
import idna
import jwt
import json
import urllib.parse
import datetime
from concurrent.futures import ThreadPoolExecutor
from .. import models, apps, forms, zone_info, tasks
from . import gchat_bot


def index(request):
    form = forms.DomainSearchForm()
    tlds = list(map(lambda z: z[0], sorted(zone_info.ZONES, key=lambda z: z[0])))

    return render(request, "domains/index.html", {
        "registration_enabled": settings.REGISTRATION_ENABLED,
        "domain_form": form,
        "tlds": json.dumps(tlds),
        "register_url": request.build_absolute_uri(reverse('domain_register', args=("$domain.$tld",)))
    })


def domain_prices(request):
    zones = list(map(lambda z: {
        "zone": z[0],
        "currency": z[1].pricing.currency,
        "registration": z[1].pricing.representative_registration(),
        "renewal": z[1].pricing.representative_renewal(),
        "restore": z[1].pricing.representative_restore(),
        "transfer": z[1].pricing.representative_transfer(),
    }, sorted(zone_info.ZONES, key=lambda z: z[0])))

    return render(request, "domains/domain_prices.html", {
        "domains": zones
    })


def domain_price_query(request):
    if request.method == "POST":
        form = forms.DomainSearchForm(request.POST)
        form.helper.form_action = request.get_full_path()
        if form.is_valid():
            try:
                domain_idna = idna.encode(form.cleaned_data['domain'], uts46=True).decode()
            except idna.IDNAError as e:
                form.add_error('domain', f"Invalid Unicode: {e}")
            else:
                zone, sld = zone_info.get_domain_info(domain_idna)
                if zone:
                    try:
                        data = zone.pricing.fees(
                            request.country.iso_code, request.user.username if request.user.is_authenticated else None,
                            sld
                        )
                        return render(request, "domains/domain_price_query.html", {
                            "domain_form": form,
                            "domain_data": data
                        })
                    except grpc.RpcError as rpc_error:
                        return render(request, "domains/domain_price_query.html", {
                            "error": rpc_error.details(),
                            "domain_form": form
                        })
                else:
                    form.add_error('domain', "Unsupported or invalid domain")

    else:
        form = forms.DomainSearchForm()
        form.helper.form_action = request.get_full_path()

    return render(request, "domains/domain_price_query.html", {
        "domain_form": form
    })


@login_required
def domains(request):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domains = models.DomainRegistration.get_object_list(access_token).filter(former_domain=False)
    registration_orders = models.DomainRegistrationOrder.get_object_list(access_token).exclude(state=models.AbstractOrder.STATE_COMPLETED)
    transfer_orders = models.DomainTransferOrder.get_object_list(access_token).exclude(state=models.AbstractOrder.STATE_COMPLETED)
    renew_orders = models.DomainRenewOrder.get_object_list(access_token).exclude(state=models.AbstractOrder.STATE_COMPLETED)
    restore_orders = models.DomainRestoreOrder.get_object_list(access_token).exclude(state=models.AbstractOrder.STATE_COMPLETED)
    error = None

    active_domains = []
    deleted_domains = []

    def get_domain(d):
        if d.deleted:
            deleted_domains.append(d)
        else:
            try:
                domain_data = apps.epp_client.get_domain(d.domain)
                if apps.epp_api.rgp_pb2.RedemptionPeriod in domain_data.rgp_state:
                    d.deleted = True
                    d.deleted_date = timezone.now()
                    d.save()
                    deleted_domains.append(d)
                else:
                    active_domains.append({
                        "id": d.id,
                        "obj": d,
                        "domain": domain_data
                    })
            except grpc.RpcError as rpc_error:
                active_domains.append({
                    "id": d.id,
                    "obj": d,
                    "error": rpc_error.details()
                })

    with ThreadPoolExecutor() as executor:
        executor.map(get_domain, user_domains)

    return render(request, "domains/domains.html", {
        "domains": active_domains,
        "deleted_domains": deleted_domains,
        "registration_orders": registration_orders,
        "transfer_orders": transfer_orders,
        "renew_orders": renew_orders,
        "restore_orders": restore_orders,
        "error": error,
        "registration_enabled": settings.REGISTRATION_ENABLED
    })


@login_required
def domain(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if user_domain.former_domain:
        return render(request, "domains/error.html", {
            "error": "This domain is no longer registered with us.",
            "back_url": referrer
        })

    if user_domain.deleted:
        return render(request, "domains/error.html", {
            "error": "This domain has been deleted, and is in its redemption grace period.",
            "back_url": referrer
        })

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    sharing_data = {
        "referrer": settings.OIDC_CLIENT_ID,
        "referrer_uri": request.build_absolute_uri()
    }
    sharing_data_uri = urllib.parse.urlencode(sharing_data)
    sharing_uri = f"{settings.KEYCLOAK_SERVER_URL}/auth/realms/{settings.KEYCLOAK_REALM}/account/resource/" \
                  f"{user_domain.resource_id}?{sharing_data_uri}"

    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    error = None
    domain_data = None
    registrant = None
    admin = None
    billing = None
    tech = None
    is_hexdns = False
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
    host_object_form_set = forms.DomainHostObjectFormSet(
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
    
    ds_form.fields['algorithm'].choices = list(filter(
        lambda c: c[0] in domain_info.supported_dnssec_algorithms, ds_form.fields['algorithm'].choices
    ))
    dnskey_form.fields['algorithm'].choices = list(filter(
        lambda c: c[0] in domain_info.supported_dnssec_algorithms, dnskey_form.fields['algorithm'].choices
    ))
    ds_form.fields['digest_type'].choices = list(filter(
        lambda c: c[0] in domain_info.supported_dnssec_digests, ds_form.fields['digest_type'].choices
    ))

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)

        if apps.epp_api.rgp_pb2.RedemptionPeriod in domain_data.rgp_state:
            user_domain.deleted = True
            user_domain.deleted_date = timezone.now()
            user_domain.save()
            return redirect('domains')

        if request.method == "POST" and request.POST.get("type") == "host_search":
            new_host_form = forms.HostSearchForm(
                request.POST,
                domain_name=user_domain.domain
            )
            if new_host_form.is_valid():
                try:
                    host_idna = idna.encode(new_host_form.cleaned_data['host'], uts46=True).decode()
                except idna.IDNAError as e:
                    new_host_form.add_error('host', f"Invalid Unicode: {e}")
                else:
                    host = f"{host_idna}.{domain_data.name}"
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
            registrant = models.Contact.get_contact(domain_data.registrant, domain_data.registry_name, request.user, domain_info)
            registrant_form.set_cur_id(cur_id=domain_data.registrant, registry_id=domain_data.registry_name)
        else:
            registrant = user_domain.registrant_contact
            registrant_form.fields['contact'].value = user_domain.registrant_contact.id

        if domain_data.admin and domain_info.admin_supported:
            admin = models.Contact.get_contact(domain_data.admin.contact_id, domain_data.registry_name, request.user, domain_info)
            admin_contact_form.set_cur_id(cur_id=domain_data.admin.contact_id, registry_id=domain_data.registry_name)
        elif user_domain.admin_contact:
            admin = user_domain.admin_contact
            admin_contact_form.fields['contact'].value = user_domain.admin_contact.id

        if domain_data.billing and domain_info.billing_supported:
            billing = models.Contact.get_contact(domain_data.billing.contact_id, domain_data.registry_name, request.user, domain_info)
            billing_contact_form.set_cur_id(cur_id=domain_data.billing.contact_id, registry_id=domain_data.registry_name)
        elif user_domain.billing_contact:
            billing = user_domain.billing_contact
            billing_contact_form.fields['contact'].value = user_domain.billing_contact.id

        if domain_data.tech and domain_info.tech_supported:
            tech = models.Contact.get_contact(domain_data.tech.contact_id, domain_data.registry_name, request.user, domain_info)
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

        if all(
                any(
                    (hns == ns.host_obj.lower() if ns.host_obj else hns == ns.host_name.lower())
                    for ns in domain_data.name_servers
                )
                for hns in ("ns1.as207960.net", "ns2.as207960.net")
        ):
            is_hexdns = True

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
        "host_object_form_set": host_object_form_set,
        "host_addr_form": host_addr_form,
        "ds_form": ds_form,
        "dnskey_form": dnskey_form,
        "registration_enabled": settings.REGISTRATION_ENABLED,
        "registry_lock_enabled": settings.REGISTRY_LOCK_ENABLED,
        "is_hexdns": is_hexdns,
        "sharing_uri": sharing_uri
    })


@login_required
@require_POST
def update_domain_contact(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
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
                            contact_id = contact.get_registry_id(domain_data.registry_name, domain_info)
                            domain_data.set_contact(contact_type, contact_id.registry_contact_id)
                        else:
                            domain_data.set_contact(contact_type, None)
                elif contact_type == 'tech':
                    user_domain.tech_contact = contact
                    if domain_info.tech_supported:
                        if contact:
                            contact_id = contact.get_registry_id(domain_data.registry_name, domain_info)
                            domain_data.set_contact(contact_type, contact_id.registry_contact_id)
                        else:
                            domain_data.set_contact(contact_type, None)
                elif contact_type == 'billing':
                    user_domain.billing_contact = contact
                    if domain_info.billing_supported:
                        if contact:
                            contact_id = contact.get_registry_id(domain_data.registry_name, domain_info)
                            domain_data.set_contact(contact_type, contact_id.registry_contact_id)
                        else:
                            domain_data.set_contact(contact_type, None)

                user_domain.save()
            elif domain_info.registrant_change_supported:
                if domain_info.registrant_supported:
                    contact_id = contact.get_registry_id(domain_data.registry_name, domain_info)
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    form_set = forms.DomainHostObjectFormSet(
        request.POST,
        domain_id=user_domain.id,
    )
    if form_set.is_valid():
        hosts = []

        action = request.POST.get("action")

        for form in form_set.forms:
            host_obj = form.cleaned_data.get('host')
            if host_obj:
                try:
                    host_idna = idna.encode(host_obj, uts46=True).decode()
                    hosts.append(host_idna)
                except idna.IDNAError:
                    pass

        if domain_info.pre_create_host_objects:
            for host_obj in hosts:
                try:
                    host_available, _ = apps.epp_client.check_host(host_obj, domain_data.registry_name)

                    if host_available:
                        if domain_info.registry == domain_info.REGISTRY_ISNIC:
                            if user_domain.tech_contact:
                                zone_contact = user_domain.tech_contact
                            else:
                                zone_contact = user_domain.registrant_contact

                            isnic_zone_contact = zone_contact.get_registry_id(domain_data.registry_name, domain_info)
                        else:
                            isnic_zone_contact = None

                        apps.epp_client.create_host(host_obj, [], domain_data.registry_name, isnic_zone_contact.registry_contact_id)
                except grpc.RpcError as rpc_error:
                    error = rpc_error.details()
                    return render(request, "domains/error.html", {
                        "error": error,
                        "back_url": referrer
                    })

        try:
            domain_data.add_host_objs(hosts, replace=action=="Replace")
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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

    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
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
    
    if not domain_data.can_update:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    if host_name == "all":
        host_objs = []
        for ns in domain_data.name_servers:
            if ns.host_obj:
                host_objs.append(ns.host_obj)
    else:
        host_objs = [host_name]

    try:
        domain_data.del_host_objs(host_objs)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    return redirect(referrer)


@login_required
def domain_hexdns(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    domain_jwt = jwt.encode({
        "iat": datetime.datetime.utcnow(),
        "nbf": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        "iss": "urn:as207960:domains",
        "aud": ["urn:as207960:hexdns"],
        "domain": user_domain.domain,
        "domain_id": user_domain.id,
        "sub": request.user.username,
    }, settings.JWT_PRIV_KEY, algorithm='ES384')

    return redirect(f"{settings.HEXDNS_URL}/setup_domains_zone/?domain_token={domain_jwt}")


def _domain_search(request, domain_name):
    try:
        domain_idna = domain_name.encode('idna').decode()
    except UnicodeError as e:
        return "invalid", f"Invalid Unicode: {e}"
    else:
        zone, sld = zone_info.get_domain_info(domain_idna)
        if zone:
            pending_domain = models.DomainRegistration.objects.filter(
                domain=domain_name, former_domain=False
            ).first()
            if pending_domain:
                return "invalid", "Domain unavailable"
            else:
                try:
                    available, reason, _ = apps.epp_client.check_domain(domain_idna)
                except grpc.RpcError as rpc_error:
                    return "error", rpc_error.details()
                else:
                    if not available:
                        if not reason:
                            return "invalid", "Domain unavailable"
                        else:
                            return "invalid", f"Domain unavailable: {reason}"
                    else:
                        if request.user.is_authenticated:
                            return "resp", redirect('domain_register', domain_idna)
                        else:
                            return "resp", redirect('domain_search_success', domain_idna)
        else:
            return "invalid", "Unsupported or invalid domain"


def domain_search(request):
    error = None

    if request.method == "POST" or request.GET.get("domain"):
        if request.method == "POST":
            form = forms.DomainSearchForm(request.POST)
        else:
            form = forms.DomainSearchForm({
                "domain": request.GET.get("domain")
            })
        if form.is_valid():
            domain_search_term = form.cleaned_data['domain']
            resp = _domain_search(request, domain_search_term)
            if resp is not None:
                if resp[0] == "error":
                    error = resp[1]
                elif resp[0] == "invalid":
                    form.add_error('domain', resp[1])
                elif resp[0] == "resp":
                    return resp[1]
    else:
        form = forms.DomainSearchForm()

    return render(request, "domains/domain_search.html", {
        "domain_form": form,
        "error": error
    })


def domain_search_gay(request):
    error = None

    if request.method == "POST":
        form = forms.DomainSearchForm(request.POST)
        if form.is_valid():
            domain_name = f"{form.cleaned_data['domain']}.gay"
            resp = _domain_search(request, domain_name)
            if resp is not None:
                if resp[0] == "error":
                    error = resp[1]
                elif resp[0] == "invalid":
                    error = resp[1]
                elif resp[0] == "resp":
                    return resp[1]

    return render(request, "domains/domain_search_gay.html", {
        "error": error
    })


def domain_search_success(request, domain_name):
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    zone, sld = zone_info.get_domain_info(domain_name)
    if not zone:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    price_decimal = zone.pricing.registration(
        request.country.iso_code, request.user.username if request.user.is_authenticated else None, sld
    )

    return render(request, "domains/domain_search_success.html", {
        "domain": domain_name,
        "price_decimal": price_decimal,
    })


@login_required
def domain_register(request, domain_name):
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)

    if not settings.REGISTRATION_ENABLED or not models.DomainRegistrationOrder.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    user_addresses = models.Contact.get_object_list(access_token)
    user_contacts = models.ContactAddress.get_object_list(access_token)
    if not user_contacts.count() or not user_addresses.count():
        request.session["after_setup_uri"] = request.get_full_path()
        return render(request, "domains/domain_create_contact.html")

    error = None

    zone, sld = zone_info.get_domain_info(domain_name)
    if not zone:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_unicode = domain_name.encode().decode('idna')
    except UnicodeError:
        domain_unicode = domain_name

    zone_price, registry_name, zone_notice = zone.pricing, zone.registry, zone.notice

    if request.method == "POST":
        form = forms.DomainRegisterForm(
            request.POST,
            zone=zone,
            user=request.user
        )
        if form.is_valid():
            registrant = form.cleaned_data['registrant']
            admin_contact = form.cleaned_data['admin']
            billing_contact = form.cleaned_data['billing']
            tech_contact = form.cleaned_data['tech']
            period = form.cleaned_data['period']

            billing_value = zone_price.registration(
                request.country.iso_code, request.user.username, sld, unit=period.unit, value=period.value
            ).amount
            if billing_value is None:
                return render(request, "domains/error.html", {
                    "error": "You don't have permission to perform this action",
                    "back_url": referrer
                })

            order = models.DomainRegistrationOrder(
                domain=domain_name,
                period_unit=period.unit,
                period_value=period.value,
                registrant_contact=registrant,
                admin_contact=admin_contact,
                billing_contact=billing_contact,
                tech_contact=tech_contact,
                user=request.user,
                price=billing_value,
                auth_info=models.make_secret(),
                off_session=False,
            )
            order.save()
            tasks.process_domain_registration.delay(order.id)
            return redirect('domain_register_confirm', order.id)
    else:
        form = forms.DomainRegisterForm(
            zone=zone,
            user=request.user
        )

    price_decimal = zone_price.registration(request.country.iso_code, request.user.username, sld)

    return render(request, "domains/domain_form.html", {
        "domain_form": form,
        "domain_name": domain_unicode,
        "price_decimal": price_decimal,
        "zone_notice": zone_notice,
        "zone_info": zone,
        "error": error
    })


def confirm_order(request, order, pending_template, passed_off_template=None):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    referrer = reverse('domains')

    if not order.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    if order.state == order.STATE_NEEDS_PAYMENT:
        if "charge_state_id" in request.GET:
            return render(request, "domains/domain_order_processing.html", {
                "domain_name": order.unicode_domain
            })
        return redirect(order.redirect_uri)
    elif order.state == order.STATE_PENDING_APPROVAL:
        if order.last_error and passed_off_template:
            return render(request, passed_off_template, {
                "domain_name": order.unicode_domain
            })

        zone, sld = zone_info.get_domain_info(order.domain)

        return render(request, pending_template, {
            "domain_name": order.unicode_domain,
            "zone": zone,
        })
    elif order.state == order.STATE_FAILED:
        return render(request, "domains/error.html", {
            "error": order.last_error,
            "back_url": referrer
        })
    elif order.state == order.STATE_COMPLETED:
        return redirect('domain', order.domain_obj.id)
    else:
        return render(request, "domains/domain_order_processing.html", {
            "domain_name": order.unicode_domain
        })


@login_required
def domain_register_confirm(request, order_id):
    registration_order = get_object_or_404(models.DomainRegistrationOrder, id=order_id)

    return confirm_order(
        request, registration_order, "domains/domain_pending.html", "domains/domain_passed_off.html"
    )


@login_required
def delete_domain(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'delete'):
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

    can_delete = domain_data.can_delete

    if request.method == "POST":
        if can_delete and request.POST.get("delete") == "true":
            try:
                pending, registry_name, _transaction_id, _fee_data = apps.epp_client.delete_domain(user_domain.domain)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
                return render(request, "domains/error.html", {
                    "error": error,
                    "back_url": referrer
                })

            gchat_bot.notify_delete.delay(user_domain.id, registry_name)
            if not domain_info.restore_supported:
                user_domain.former_domain = True
                user_domain.save()
            else:
                user_domain.deleted = True
                user_domain.deleted_date = timezone.now()
                user_domain.save()
            return redirect('domains')

    return render(request, "domains/delete_domain.html", {
        "domain": domain_data,
        "can_delete": can_delete,
        "back_url": referrer
    })


@login_required
def transfer_out_domain(request, domain_id, transfer_action):
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if transfer_action not in ("reject", "approve"):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.deleted or user_domain.former_domain:
        return render(request, "domains/error.html", {
            "error": "This domain is no longer registered with us",
            "back_url": referrer
        })

    if not user_domain.has_scope(access_token, 'delete') or not user_domain.transfer_out_pending:
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

    if request.method == "POST" and request.POST.get("confirm") == "true":
        if transfer_action == "approve":
            if domain_info.direct_restore_supported:
                try:
                    transfer_obj = apps.epp_client.transfer_accept_domain(user_domain.domain, "")
                except grpc.RpcError as rpc_error:
                    error = rpc_error.details()
                    return render(request, "domains/error.html", {
                        "error": error,
                        "back_url": referrer
                    })

                if not transfer_obj.pending:
                    user_domain.transfer_out_pending = False
                    user_domain.former_domain = True
                    user_domain.save()
                    return redirect('domains')
            else:
                gchat_bot.request_transfer_accept.delay(user_domain.id, domain_data.registry_name)
                return render(request, "domains/transfer_out_domain_pending.html", {
                    "domain": user_domain,
                    "action": transfer_action,
                    "back_url": reverse('domains')
                })
        elif transfer_action == "reject":
            if domain_info.direct_restore_supported:
                try:
                    transfer_obj = apps.epp_client.transfer_reject_domain(user_domain.domain, "")
                except grpc.RpcError as rpc_error:
                    error = rpc_error.details()
                    return render(request, "domains/error.html", {
                        "error": error,
                        "back_url": referrer
                    })

                if not transfer_obj.pending:
                    user_domain.transfer_out_pending = False
                    user_domain.former_domain = False
                    user_domain.save()
                    return redirect('domain', user_domain.id)
            else:
                gchat_bot.request_transfer_reject.delay(user_domain.id, domain_data.registry_name)
                return render(request, "domains/transfer_out_domain_pending.html", {
                    "domain": user_domain,
                    "action": transfer_action,
                    "back_url": reverse('domains')
                })

    return render(request, "domains/transfer_out_domain.html", {
        "domain": user_domain,
        "action": transfer_action,
        "back_url": referrer
    })


@login_required
def renew_domain(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)

    if not user_domain.has_scope(access_token, 'edit') or \
            not models.DomainRenewOrder.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone, sld = zone_info.get_domain_info(user_domain.domain)
    if not zone:
        raise Http404

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    if not domain_data.can_renew:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone_price, _ = zone.pricing, zone.registry

    if request.method == "POST":
        form = forms.DomainRenewForm(
            request.POST,
            zone_info=zone
        )

        if form.is_valid():
            period = form.cleaned_data['period']

            period = apps.epp_api.Period(
                value=period.value,
                unit=period.unit
            )

            billing_value = zone_price.renewal(
                country=request.country.iso_code, username=request.user.username, sld=sld,
                unit=period.unit, value=period.value
            ).amount
            if billing_value is None:
                return render(request, "domains/error.html", {
                    "error": "You don't have permission to perform this action",
                    "back_url": referrer
                })

            order = models.DomainRenewOrder(
                domain=user_domain.domain,
                domain_obj=user_domain,
                period_unit=period.unit,
                period_value=period.value,
                user=request.user,
                price=billing_value,
                off_session=False,
            )
            order.save()
            tasks.process_domain_renewal.delay(order.id)

            return redirect('renew_domain_confirm', order.id)
    else:
        form = forms.DomainRenewForm(zone_info=zone)

    price_decimal = zone_price.renewal(request.country.iso_code, request.user.username, sld)

    return render(request, "domains/renew_domain.html", {
        "domain": user_domain,
        "domain_name": user_domain.domain,
        "zone_info": zone,
        "domain_form": form,
        "price_decimal": price_decimal,
        "currency": "GBP",
    })


@login_required
def renew_domain_confirm(request, order_id):
    renew_order = get_object_or_404(models.DomainRenewOrder, id=order_id)

    return confirm_order(request, renew_order, "domains/domain_pending.html", "domains/domain_passed_off.html")


@login_required
def restore_domain(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=True, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit') or \
            not models.DomainRestoreOrder.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone, sld = zone_info.get_domain_info(user_domain.domain)
    if not zone:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone_price, _ = zone.pricing, zone.registry
    billing_value = zone_price.restore(request.country.iso_code, request.user.username, sld).amount

    order = models.DomainRestoreOrder(
        domain=user_domain.domain,
        domain_obj=user_domain,
        price=billing_value,
        user=request.user,
        off_session=False,
    )
    order.save()
    tasks.process_domain_restore.delay(order.id)

    return redirect('restore_domain_confirm', order.id)


@login_required
def restore_domain_confirm(request, order_id):
    restore_order = get_object_or_404(models.DomainRestoreOrder, id=order_id)

    return confirm_order(
        request, restore_order, "domains/domain_restore_pending.html", "domains/domain_passed_off.html"
    )


def domain_transfer_query(request):
    error = None

    if request.method == "POST":
        form = forms.DomainSearchForm(request.POST)
        form.helper.form_action = request.get_full_path()

        if form.is_valid():
            try:
                domain_idna = idna.encode(form.cleaned_data['domain'], uts46=True).decode()
            except idna.IDNAError as e:
                form.add_error('domain', f"Invalid Unicode: {e}")
            else:
                zone, sld = zone_info.get_domain_info(domain_idna)
                if zone:
                    if not zone.transfer_supported:
                        form.add_error('domain', "Extension not yet supported for transfers")
                    else:
                        try:
                            if zone.pre_transfer_query_supported:
                                available, _, _ = apps.epp_client.check_domain(domain_idna)
                                available = not available
                            else:
                                available = True
                        except grpc.RpcError as rpc_error:
                            error = rpc_error.details()
                        else:
                            if available:
                                if zone.pre_transfer_query_supported:
                                    try:
                                        domain_data = apps.epp_client.get_domain(domain_idna)
                                    except grpc.RpcError as rpc_error:
                                        error = rpc_error.details()
                                    else:
                                        if any(s in domain_data.statuses for s in (3, 7, 8, 10, 15)):
                                            available = False
                                            form.add_error('domain', "Domain not eligible for transfer (check transfer lock)")
                            else:
                                form.add_error('domain', "Domain does not exist")

                            if available:
                                if request.user.is_authenticated:
                                    return redirect('domain_transfer', domain_idna)
                                else:
                                    return redirect('domain_transfer_search_success', domain_idna)
                else:
                    form.add_error('domain', "Unsupported or invalid domain")
    else:
        form = forms.DomainSearchForm()
        form.helper.form_action = request.get_full_path()

    return render(request, "domains/domain_transfer_query.html", {
        "domain_form": form,
        "error": error
    })


def domain_transfer_search_success(request, domain_name):
    return render(request, "domains/domain_transfer_search_success.html", {
        "domain": domain_name,
    })


@login_required
def domain_transfer(request, domain_name):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not settings.REGISTRATION_ENABLED or not models.DomainTransferOrder.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    user_addresses = models.Contact.get_object_list(access_token)
    user_contacts = models.ContactAddress.get_object_list(access_token)
    if not user_contacts.count() or not user_addresses.count():
        request.session["after_setup_uri"] = request.get_full_path()
        return render(request, "domains/domain_create_contact.html")

    error = None

    zone, sld = zone_info.get_domain_info(domain_name)
    if not zone or not zone.transfer_supported:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_unicode = idna.decode(domain_name, uts46=True)
    except idna.IDNAError:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone_price, registry_name = zone.pricing, zone.registry
    try:
        price_decimal = zone_price.transfer(request.country.iso_code, request.user.username, sld)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    if request.method == "POST":
        form = forms.DomainTransferForm(request.POST, zone=zone, user=request.user)

        if form.is_valid():
            registrant = form.cleaned_data['registrant']  # type: models.Contact
            admin_contact = form.cleaned_data['admin']  # type: models.Contact
            tech_contact = form.cleaned_data['tech']  # type: models.Contact
            billing_contact = form.cleaned_data['billing']  # type: models.Contact

            order = models.DomainTransferOrder(
                domain=domain_name,
                auth_code=form.cleaned_data['auth_code'] if zone.auth_code_for_transfer else "N/A",
                registrant_contact=registrant,
                admin_contact=admin_contact,
                billing_contact=billing_contact,
                tech_contact=tech_contact,
                price=price_decimal.amount,
                user=request.user,
                off_session=False,
            )
            order.save()
            tasks.process_domain_transfer.delay(order.id)

            return redirect('domain_transfer_confirm', order.id)
    else:
        form = forms.DomainTransferForm(zone=zone, user=request.user)

    return render(request, "domains/domain_transfer.html", {
        "domain_form": form,
        "domain_name": domain_unicode,
        "price_decimal": price_decimal,
        "zone_info": zone,
        "error": error
    })


@login_required
def domain_transfer_confirm(request, order_id):
    transfer_order = get_object_or_404(models.DomainTransferOrder, id=order_id)

    return confirm_order(
        request, transfer_order, "domains/domain_transfer_pending.html", "domains/domain_passed_off.html"
    )


@require_POST
def internal_check_price(request):
    search_action = request.POST.get("action")
    search_domain = request.POST.get("domain")
    if not search_domain or not search_action:
        return HttpResponseBadRequest()

    domain_info, sld = zone_info.get_domain_info(search_domain)
    if not domain_info:
        return HttpResponseBadRequest()

    if search_action == "register":
        price = domain_info.pricing.registration(
            request.country.iso_code, request.user.username if request.user.is_authenticated else None, sld
        )
        currency = "GBP"
    else:
        return HttpResponseBadRequest()

    return HttpResponse(json.dumps({
        "price": float(price),
        "currency": currency,
        "message": domain_info.notice
    }), content_type="application/json")
