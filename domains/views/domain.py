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
import requests
import google.protobuf.wrappers_pb2
from concurrent.futures import ThreadPoolExecutor
from ..proto import billing_pb2
from .. import models, apps, forms, zone_info, tasks
from . import gchat_bot


RENEW_INTERVAL = datetime.timedelta(days=30)


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
    auto_renew_orders = models.DomainAutomaticRenewOrder.get_object_list(access_token).exclude(state=models.AbstractOrder.STATE_COMPLETED)
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
                domain_data = apps.epp_client.get_domain(
                    d.domain, registry_id=d.registry_id
                )
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
        "auto_renew_orders": auto_renew_orders,
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
    sharing_uri = f"{settings.KEYCLOAK_SERVER_URL}/auth/realms/{settings.KEYCLOAK_REALM}/account/?{sharing_data_uri}" \
                  f"#/resources/{user_domain.resource_id}"

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

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
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )

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
        elif user_domain.tech_contact:
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
                for hns in (
                        "ns1.as207960.net",
                        "ns2.as207960.net",
                        "ns3.as207960.net",
                        "ns4.as207960.net",
                )
        ):
            is_hexdns = True

    except grpc.RpcError as rpc_error:
        return render(request, "domains/error.html", {
            "error": rpc_error.details(),
            "back_url": referrer
        })

    now = timezone.now()
    expiry_date = domain_data.expiry_date.replace(tzinfo=datetime.timezone.utc) + domain_info.expiry_offset
    paid_up_until = None
    if expiry_date - RENEW_INTERVAL <= now:
        last_renew_order = models.DomainAutomaticRenewOrder.objects.filter(domain_obj=user_domain) \
            .order_by("-timestamp").first()  # type: models.DomainAutomaticRenewOrder
        if last_renew_order and last_renew_order.state == last_renew_order.STATE_COMPLETED and \
                last_renew_order.timestamp + datetime.timedelta(days=60) >= now:
            if last_renew_order.period_unit == apps.epp_api.common_pb2.Period.Months:
                renew_period = datetime.timedelta(weeks=4 * last_renew_order.period_value)
            else:
                renew_period = datetime.timedelta(weeks=52 * last_renew_order.period_value)

            paid_up_until = expiry_date + renew_period
        else:
            last_restore_order = models.DomainRestoreOrder.objects.filter(domain_obj=user_domain, should_renew=True)\
                        .order_by("-timestamp").first()  # type: models.DomainRestoreOrder
            if last_restore_order and last_restore_order.state == last_restore_order.STATE_COMPLETED and \
                    last_restore_order.timestamp + datetime.timedelta(days=60) >= now:
                if last_restore_order.period_unit == apps.epp_api.common_pb2.Period.Months:
                    renew_period = datetime.timedelta(weeks=4 * last_restore_order.period_value)
                else:
                    renew_period = datetime.timedelta(weeks=52 * last_restore_order.period_value)

                paid_up_until = expiry_date + renew_period

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
        "sharing_uri": sharing_uri,
        "paid_up_until": paid_up_until,
        "expiry_date": expiry_date
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

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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
                            contact_id = contact.get_registry_id(
                                domain_data.registry_name, domain_info,
                                role=apps.epp_api.ContactRole.Admin
                            )
                            domain_data.set_contact(contact_type, contact_id.registry_contact_id)
                        else:
                            domain_data.set_contact(contact_type, None)
                elif contact_type == 'tech':
                    user_domain.tech_contact = contact
                    if domain_info.tech_supported:
                        if contact:
                            if domain_info.is_eurid:
                                if domain_data.eurid:
                                    contact_id = contact.get_registry_id(
                                        domain_data.registry_name, domain_info,
                                        role=apps.epp_api.ContactRole.OnSite
                                    )
                                    if contact_id.registry_contact_id != domain_data.eurid.on_site:
                                        apps.epp_client.stub.DomainUpdate(apps.epp_api.domain_pb2.DomainUpdateRequest(
                                            name=domain_data.name,
                                            registry_name=google.protobuf.wrappers_pb2.StringValue(value=domain_data.registry_name),
                                            eurid_data=apps.epp_api.eurid_pb2.DomainUpdateExtension(
                                                remove_on_site=domain_data.eurid.on_site,
                                                add_on_site=contact_id.registry_contact_id
                                            )
                                        ))
                            else:
                                contact_id = contact.get_registry_id(
                                    domain_data.registry_name, domain_info,
                                    role=apps.epp_api.ContactRole.Tech
                                )
                                domain_data.set_contact(contact_type, contact_id.registry_contact_id)
                        else:
                            domain_data.set_contact(contact_type, None)
                elif contact_type == 'billing':
                    user_domain.billing_contact = contact
                    if domain_info.billing_supported:
                        if contact:
                            contact_id = contact.get_registry_id(
                                domain_data.registry_name, domain_info,
                                role=apps.epp_api.ContactRole.Billing
                            )
                            domain_data.set_contact(contact_type, contact_id.registry_contact_id)
                        else:
                            domain_data.set_contact(contact_type, None)

                user_domain.save()
            elif domain_info.registrant_change_supported:
                if domain_info.registrant_supported:
                    contact_id = domain_info.registrant_proxy(contact)
                    if not contact_id:
                        contact_id = contact.get_registry_id(
                            domain_data.registry_name, domain_info,
                            role=apps.epp_api.ContactRole.Registrant
                        )
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

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    if not domain_info.host_object_supported:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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

                        apps.epp_client.create_host(
                            host_obj, [], domain_data.registry_name,
                            isnic_zone_contact.registry_contact_id if isnic_zone_contact else None
                        )
                except grpc.RpcError as rpc_error:
                    error = rpc_error.details()
                    return render(request, "domains/error.html", {
                        "error": error,
                        "back_url": referrer
                    })

        try:
            domain_data.add_host_objs(hosts, replace=action == "Replace")
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

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    if not domain_info.host_object_supported:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    if domain_info.host_object_supported:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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
        host_v4_addr = form.cleaned_data['v4_address']
        host_v6_addr = form.cleaned_data['v6_address']
        addrs = []
        if host_v4_addr:
            address = ipaddress.IPv4Address(host_v4_addr)
            addrs.append(apps.epp_api.IPAddress(
                address=address.compressed,
                ip_type=apps.epp_api.common_pb2.IPAddress.IPVersion.IPv4
            ))
        if host_v6_addr:
            address = ipaddress.IPv6Address(host_v6_addr)
            addrs.append(apps.epp_api.IPAddress(
                address=address.compressed,
                ip_type=apps.epp_api.common_pb2.IPAddress.IPVersion.IPv6
            ))
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
def delete_domain_host_addr(request, domain_id, host_name):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    if domain_info.host_object_supported:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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
            if ns.host_name:
                host_objs.append(ns.host_name)
    else:
        host_objs = [host_name]

    try:
        domain_data.del_host_name(host_objs)
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
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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

        tasks.notify_dnssec_enabled.delay(user_domain.id)

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
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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

        tasks.notify_dnssec_enabled.delay(user_domain.id)

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
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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

    tasks.notify_dnssec_disabled.delay(user_domain.id)

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


@login_required
def domain_cf(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    msg = billing_pb2.BillingRequest(
        cloudflare_account=billing_pb2.CloudflareAccountRequest(
            id=request.user.username
        )
    )
    msg_response = billing_pb2.CloudflareAccountResponse()
    msg_response.ParseFromString(apps.rpc_client.call('billing_rpc', msg.SerializeToString(), timeout=0))

    if msg_response.result == msg_response.NEEDS_SETUP:
        return redirect(reverse('https://billing.as207970.net'))
    elif msg_response.result == msg_response.FAIL:
        return render(request, "domains/error.html", {
            "error": msg_response.message if msg_response.message.strip() != "" else "An error occurred",
            "back_url": referrer
        })

    if not user_domain.cf_zone_id:
        r = requests.post("https://api.cloudflare.com/client/v4/zones", headers={
            "X-Auth-Email": settings.CLOUDFLARE_API_EMAIL,
            "X-Auth-Key": settings.CLOUDFLARE_API_KEY,
        }, json={
            "name": user_domain.domain,
            "account": {
                "id": msg_response.account_id
            }
        })
        r.raise_for_status()
        zone_data = r.json()["result"]

        user_domain.cf_zone_id = zone_data["id"]
        user_domain.save()
    else:
        r = requests.get(f"https://api.cloudflare.com/client/v4/zones/{user_domain.cf_zone_id}", headers={
            "X-Auth-Email": settings.CLOUDFLARE_API_EMAIL,
            "X-Auth-Key": settings.CLOUDFLARE_API_KEY,
        })
        r.raise_for_status()
        zone_data = r.json()["result"]

    r = requests.post(f"https://api.cloudflare.com/client/v4/zones/{user_domain.cf_zone_id}/subscription", headers={
        "X-Auth-Email": settings.CLOUDFLARE_API_EMAIL,
        "X-Auth-Key": settings.CLOUDFLARE_API_KEY,
    }, json={
        "rate_plan": {
            "id": "CF_FREE"
        },
    })
    r.raise_for_status()

    tasks.set_dns(user_domain, zone_data["name_servers"])

    return redirect('domain', user_domain.id)

@login_required
def domain_cf_remove(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    if user_domain.cf_zone_id:
        r = requests.delete(f"https://api.cloudflare.com/client/v4/zones/{user_domain.cf_zone_id}", headers={
            "X-Auth-Email": settings.CLOUDFLARE_API_EMAIL,
            "X-Auth-Key": settings.CLOUDFLARE_API_KEY,
        })
        r.raise_for_status()

    tasks.set_dns(user_domain, [])

    return redirect('domain', user_domain.id)


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
        request.country.iso_code, request.user.username if request.user.is_authenticated else None, sld,
        local_currency=True
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
        request.session["setup_domain"] = domain_name
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
        if "new_contact" in request.session:
            del request.session["new_contact"]

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


            registration_order = models.DomainRegistrationOrder.get_object_list(access_token) \
                                   .exclude(state=models.AbstractOrder.STATE_COMPLETED) \
                                   .exclude(state=models.AbstractOrder.STATE_FAILED) \
                                   .filter(domain=domain_name).first()

            if registration_order:
                registration_order.period_unit = period.unit
                registration_order.period_value = period.value
                registration_order.registrant_contact = registrant
                registration_order.admin_contact = admin_contact
                registration_order.billing_contact = billing_contact
                registration_order.tech_contact = tech_contact
                registration_order.price = billing_value
                registration_order.off_session = False
                registration_order.save()
            else:
                registration_order = models.DomainRegistrationOrder(
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
                registration_order.save()

            tasks.process_domain_registration.delay(registration_order.id)
            return redirect('domain_register_confirm', registration_order.id)
    else:
        form = forms.DomainRegisterForm(
            zone=zone,
            user=request.user
        )
        if "new_contact" in request.session:
            form.fields['registrant'].initial = request.session["new_contact"]
            form.fields['admin'].initial = request.session["new_contact"]
            form.fields['tech'].initial = request.session["new_contact"]
            form.fields['billing'].initial = request.session["new_contact"]

    price_decimal = zone_price.registration(request.country.iso_code, request.user.username, sld, local_currency=True)

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

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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
                pending, registry_name, _transaction_id, _fee_data = apps.epp_client.delete_domain(
                    user_domain.domain, registry_id=user_domain.registry_id
                )
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
def mark_domain_not_required(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'delete'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    if not domain_info.nominet_mark_not_required:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        apps.epp_client.stub.DomainUpdate(apps.epp_api.domain_pb2.DomainUpdateRequest(
            name=user_domain.domain,
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=user_domain.registry_id),
            nominet_ext=apps.epp_api.nominet_ext_pb2.DomainUpdate(
                renewal_not_required=google.protobuf.wrappers_pb2.BoolValue(value=True)
            )
        ))
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    user_domain.not_required = True
    user_domain.save()

    return redirect(referrer)


@login_required
def mark_domain_required(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'delete'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    if not domain_info.nominet_mark_not_required:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        apps.epp_client.stub.DomainUpdate(apps.epp_api.domain_pb2.DomainUpdateRequest(
            name=user_domain.domain,
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=user_domain.registry_id),
            nominet_ext=apps.epp_api.nominet_ext_pb2.DomainUpdate(
                renewal_not_required=google.protobuf.wrappers_pb2.BoolValue(value=False)
            )
        ))
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    user_domain.not_required = False
    user_domain.save()

    return redirect(referrer)


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

    domain_info = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    if request.method == "POST" and request.POST.get("confirm") == "true":
        if transfer_action == "approve":
            if domain_info.direct_transfer_supported:
                try:
                    _ = apps.epp_client.transfer_accept_domain(
                        user_domain.domain, "",
                        registry_id=user_domain.registry_id
                    )
                except grpc.RpcError as rpc_error:
                    error = rpc_error.details()
                    return render(request, "domains/error.html", {
                        "error": error,
                        "back_url": referrer
                    })

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
            if domain_info.direct_transfer_supported:
                try:
                    _ = apps.epp_client.transfer_reject_domain(
                        user_domain.domain, "",
                        registry_id=user_domain.registry_id
                    )
                except grpc.RpcError as rpc_error:
                    error = rpc_error.details()
                    return render(request, "domains/error.html", {
                        "error": error,
                        "back_url": referrer
                    })

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

    zone, sld = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)
    if not zone:
        raise Http404

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
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

    price_decimal = zone_price.renewal(request.country.iso_code, request.user.username, sld, local_currency=True)

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
def auto_renew_domain_confirm(request, order_id):
    renew_order = get_object_or_404(models.DomainAutomaticRenewOrder, id=order_id)

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

    zone, sld = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)
    if not zone:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        domain_data = apps.epp_client.get_domain(
            user_domain.domain, registry_id=user_domain.registry_id
        )
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    expiry_date = domain_data.expiry_date.replace(tzinfo=datetime.timezone.utc) + zone.expiry_offset
    zone_price, _ = zone.pricing, zone.registry
    renewal_period = zone_price.periods[0]
    billing_value = zone_price.restore(request.country.iso_code, request.user.username, sld).amount
    should_renew = False
    if (expiry_date - RENEW_INTERVAL) <= timezone.now():
        should_renew = True
        billing_value += zone_price.renewal(
            request.country.iso_code, request.user.username, sld, unit=renewal_period.unit, value=renewal_period.value
        ).amount

    order = models.DomainRestoreOrder(
        domain=user_domain.domain,
        domain_obj=user_domain,
        price=billing_value,
        user=request.user,
        off_session=False,
        period_unit=renewal_period.unit,
        period_value=renewal_period.value,
        should_renew=should_renew
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

    zone, sld = zone_info.get_domain_info(domain_name)
    if not zone or not zone.transfer_supported:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    user_addresses = models.Contact.get_object_list(access_token)
    user_contacts = models.ContactAddress.get_object_list(access_token)
    if not user_contacts.count() or not user_addresses.count():
        request.session["after_setup_uri"] = request.get_full_path()
        request.session["setup_domain"] = domain_name
        return render(request, "domains/domain_create_contact.html")

    error = None

    try:
        domain_unicode = idna.decode(domain_name, uts46=True)
    except idna.IDNAError:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    zone_price, registry_name = zone.pricing, zone.registry
    try:
        price_decimal = zone_price.transfer(request.country.iso_code, request.user.username, sld, local_currency=True)
        billing_value = zone_price.transfer(request.country.iso_code, request.user.username, sld)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    if request.method == "POST":
        if "new_contact" in request.session:
            del request.session["new_contact"]

        form = forms.DomainTransferForm(request.POST, zone=zone, user=request.user)

        if form.is_valid():
            registrant = form.cleaned_data['registrant']  # type: models.Contact
            admin_contact = form.cleaned_data['admin']  # type: models.Contact
            tech_contact = form.cleaned_data['tech']  # type: models.Contact
            billing_contact = form.cleaned_data['billing']  # type: models.Contact

            transfer_order = models.DomainTransferOrder.get_object_list(access_token) \
                                .exclude(state=models.AbstractOrder.STATE_COMPLETED) \
                                .exclude(state=models.AbstractOrder.STATE_FAILED) \
                                .filter(domain=domain_name).first()

            if transfer_order:
                transfer_order.auth_code = form.cleaned_data['auth_code'] if zone.auth_code_for_transfer else "N/A"
                transfer_order.registrant_contact = registrant
                transfer_order.admin_contact = admin_contact
                transfer_order.billing_contact = billing_contact
                transfer_order.tech_contact = tech_contact
                transfer_order.price = billing_value.amount
                transfer_order.off_session = False
                transfer_order.save()
            else:
                transfer_order = models.DomainTransferOrder(
                    domain=domain_name,
                    auth_code=form.cleaned_data['auth_code'] if zone.auth_code_for_transfer else "N/A",
                    registrant_contact=registrant,
                    admin_contact=admin_contact,
                    billing_contact=billing_contact,
                    tech_contact=tech_contact,
                    price=billing_value.amount,
                    user=request.user,
                    off_session=False,
                )
                transfer_order.save()

            tasks.process_domain_transfer.delay(transfer_order.id)

            return redirect('domain_transfer_confirm', transfer_order.id)
    else:
        form = forms.DomainTransferForm(zone=zone, user=request.user)
        if "new_contact" in request.session:
            form.fields['registrant'].initial = request.session["new_contact"]
            form.fields['admin'].initial = request.session["new_contact"]
            form.fields['tech'].initial = request.session["new_contact"]
            form.fields['billing'].initial = request.session["new_contact"]

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
            request.country.iso_code, request.user.username if request.user.is_authenticated else None, sld,
            local_currency=True
        )
    else:
        return HttpResponseBadRequest()

    return HttpResponse(json.dumps({
        "price": float(price.amount_inc_vat),
        "currency": price.currency,
        "message": domain_info.notice
    }), content_type="application/json")
