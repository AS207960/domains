from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import ipaddress
import grpc
import decimal
from concurrent.futures import ThreadPoolExecutor
from . import models, apps, hooks, forms, zone_info


def domain_prices(request):
    zones = list(map(lambda z: {
        "zone": z[0],
        "registration": decimal.Decimal(z[1].pricing.registration("")) / decimal.Decimal(100),
        "renewal": decimal.Decimal(z[1].pricing.renewal("")) / decimal.Decimal(100),
        "restore": decimal.Decimal(z[1].pricing.restore("")) / decimal.Decimal(100),
    }, zone_info.ZONES))

    return render(request, "domains/domain_prices.html", {
        "domains": zones
    })


@login_required
def domains(request):
    user_domains = models.DomainRegistration.objects.filter(user=request.user)
    domains_data = []
    error = None
    try:
        with ThreadPoolExecutor() as executor:
            domains_data = list(executor.map(lambda d: (d.id, apps.epp_client.get_domain(d.domain)), user_domains))
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()

    return render(request, "domains/domains.html", {
        "domains": domains_data,
        "error": error,
        "registration_enabled": settings.REGISTRATION_ENABLED
    })


@login_required
def domain(request, domain_id):
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)
    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    if user_domain.user != request.user:
        raise PermissionDenied

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
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
    else:
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
                        return redirect('host_create', domain_data.registry_name, host)

        try:
            registrant = models.Contact.get_contact(domain_data.registrant, domain_data.registry_name, request.user)
        except grpc.RpcError as rpc_error:
            error = rpc_error.details()

        registrant_form.set_cur_id(cur_id=domain_data.registrant, registry_id=domain_data.registry_name)

        if domain_data.admin:
            try:
                admin = models.Contact.get_contact(domain_data.admin.contact_id, domain_data.registry_name, request.user)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
            admin_contact_form.set_cur_id(cur_id=domain_data.admin.contact_id, registry_id=domain_data.registry_name)

        if domain_data.billing:
            try:
                billing = models.Contact.get_contact(domain_data.billing.contact_id, domain_data.registry_name, request.user)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
            billing_contact_form.set_cur_id(cur_id=domain_data.billing.contact_id, registry_id=domain_data.registry_name)

        if domain_data.tech:
            try:
                tech = models.Contact.get_contact(domain_data.tech.contact_id, domain_data.registry_name, request.user)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
            tech_contact_form.set_cur_id(cur_id=domain_data.tech.contact_id, registry_id=domain_data.registry_name)

        if domain_info.registry == domain_info.REGISTRY_AFILIAS:
            admin_contact_form.fields['contact'].required = True
            billing_contact_form.fields['contact'].required = True
            tech_contact_form.fields['contact'].required = True

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
        "dnskey_form": dnskey_form
    })


@login_required
@require_POST
def update_domain_contact(request, domain_id):
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)
    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

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
    if domain_info.registry == domain_info.REGISTRY_AFILIAS:
        form.fields['contact'].required = True
    if form.is_valid():
        contact_type = form.cleaned_data['type']
        try:
            if contact_type != "registrant":
                if not (
                        domain_info.registry in (domain_info.REGISTRY_NOMINET, domain_info.REGISTRY_TRAFICOM)
                        or (domain_info.registry in (domain_info.REGISTRY_SWITCH,) and contact_type == "tech")
                ):
                    contact = form.cleaned_data['contact'].get_registry_id(domain_data.registry_name)
                    domain_data.set_contact(contact_type, contact.registry_contact_id)

                old_contact = domain_data.get_contact(contact_type)
                if old_contact:
                    if apps.epp_client.check_contact(old_contact.contact_id, domain_data.registry_name):
                        models.ContactRegistry.objects.filter(
                            registry_contact_id=old_contact.contact_id,
                            registry_id=domain_data.registry_name
                        ).delete()
            elif domain_info.registry not in (domain_info.REGISTRY_TRAFICOM,):
                contact = form.cleaned_data['contact'].get_registry_id(domain_data.registry_name)
                domain_data.set_registrant(contact.registry_contact_id)
                if apps.epp_client.check_contact(domain_data.registrant, domain_data.registry_name):
                    models.ContactRegistry.objects.filter(
                        registry_contact_id=domain_data.registrant,
                        registry_id=domain_data.registry_name
                    ).delete()
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)
    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    if domain_info.registry not in (domain_info.REGISTRY_NOMINET, domain_info.REGISTRY_SWITCH, domain_info.REGISTRY_TRAFICOM):
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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)
    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    if domain_info.registry not in (domain_info.REGISTRY_NOMINET, domain_info.REGISTRY_SWITCH, domain_info.REGISTRY_TRAFICOM):
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
@require_POST
def add_domain_host_obj(request, domain_id):
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

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

            host_model = models.NameServer(
                name_server=host_obj,
                registry_id=domain_data.registry_name,
                user=request.user
            )
            host_model.save()

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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

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
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

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
    if not settings.REGISTRATION_ENABLED:
        raise PermissionDenied

    error = None

    if request.method == "POST":
        form = forms.DomainSearchForm(request.POST)
        if form.is_valid():
            zone, sld = zone_info.get_domain_info(form.cleaned_data['domain'])
            if zone:
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
    if not settings.REGISTRATION_ENABLED:
        raise PermissionDenied

    error = None
    form = None

    zone, sld = zone_info.get_domain_info(domain_name)
    if not zone:
        raise Http404

    price_decimal = decimal.Decimal(zone.registration(sld)) / decimal.Decimal(100)

    try:
        available, _, registry_name = apps.epp_client.check_domain(domain_name)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
    else:
        if not available:
            raise Http404
        if request.method == "POST":
            form = forms.DomainRegisterForm(
                request.POST,
                zone_info=zone,
                registry_name=registry_name,
                user=request.user
            )
            if form.is_valid():
                auth_info = models.make_secret()
                admin_contact = form.cleaned_data['admin']
                billing_contact = form.cleaned_data['billing']
                tech_contact = form.cleaned_data['tech']
                contact_objs = []

                if admin_contact and registry_name not in ("switch", "nominet", "traficom"):
                    contact_objs.append(apps.epp_api.DomainContact(
                        contact_type="admin",
                        contact_id=admin_contact.get_registry_id(registry_name).registry_contact_id
                    ))
                if billing_contact and registry_name not in ("switch", "nominet", "traficom"):
                    contact_objs.append(apps.epp_api.DomainContact(
                        contact_type="billing",
                        contact_id=billing_contact.get_registry_id(registry_name).registry_contact_id
                    ))
                if tech_contact and registry_name not in ("nominet", "traficom"):
                    contact_objs.append(apps.epp_api.DomainContact(
                        contact_type="tech",
                        contact_id=tech_contact.get_registry_id(registry_name).registry_contact_id
                    ))

                try:
                    pending, _, _, _ = apps.epp_client.create_domain(
                        domain=domain_name,
                        period=form.cleaned_data['period'],
                        registrant=form.cleaned_data['registrant'].get_registry_id(registry_name).registry_contact_id,
                        contacts=contact_objs,
                        name_servers=[],
                        auth_info=auth_info,
                    )
                except grpc.RpcError as rpc_error:
                    error = rpc_error.details()
                else:
                    if pending:
                        return render(request, "domains/domain_pending.html", {
                            "domain_name": domain_name
                        })
                    else:
                        domain_obj = models.DomainRegistration(
                            domain=domain_name,
                            user=request.user,
                            auth_info=auth_info
                        )
                        domain_obj.save()
                        return redirect('domain', domain_obj.id)
        else:
            form = forms.DomainRegisterForm(
                zone_info=zone,
                registry_name=registry_name,
                user=request.user
            )

    return render(request, "domains/domain_form.html", {
        "domain_form": form,
        "domain_name": domain_name,
        "price_decimal": price_decimal,
        "zone_info": zone,
        "error": error
    })


@login_required
def delete_domain(request, domain_id):
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)
    domain_info = zone_info.get_domain_info(user_domain.domain)[0]

    if user_domain.user != request.user:
        raise PermissionDenied

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    can_delete = True

    if request.method == "POST":
        if can_delete and request.POST.get("delete") == "true":
            try:
                pending, registry_id = apps.epp_client.delete_domain(user_domain.domain)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
                return render(request, "domains/error.html", {
                    "error": error,
                    "back_url": referrer
                })

            if domain_info.registry in (domain_info.REGISTRY_NOMINET, domain_info.REGISTRY_AFILIAS, domain_info.REGISTRY_DENIC):
                if apps.epp_client.check_contact(domain_data.registrant, registry_id):
                    models.ContactRegistry.objects.filter(
                        registry_contact_id=domain_data.registrant,
                        registry_id=registry_id
                    ).delete()
                user_domain.delete()
            return redirect('domains')

    return render(request, "domains/delete_domain.html", {
        "domain": user_domain,
        "can_delete": can_delete,
        "back_url": referrer
    })


@login_required
def renew_domain(request, domain_id):
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.user != request.user:
        raise PermissionDenied

    zone, sld = zone_info.get_domain_info(user_domain.domain)
    if not zone:
        raise Http404

    price_decimal = decimal.Decimal(zone.price.renewal(sld)) / decimal.Decimal(100)

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    try:
        domain_data = apps.epp_client.get_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": referrer
        })

    if request.method == "POST":
        form = forms.DomainRenewForm(
            request.POST,
            zone_info=zone
        )

        if form.is_valid():
            try:
                apps.epp_client.renew_domain(user_domain.domain, form.cleaned_data['period'], domain_data.expiry_date)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
                return render(request, "domains/error.html", {
                    "error": error,
                    "back_url": referrer
                })
    else:
        form = forms.DomainRenewForm(zone_info=zone)

    return render(request, "domains/renew_domain.html", {
        "domain": user_domain,
        "domain_name": user_domain.domain,
        "zone_info": zone,
        "domain_form": form,
        "price_decimal": price_decimal
    })


@login_required
def restore_domain(request, domain_id):
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id)

    if user_domain.user != request.user:
        raise PermissionDenied

    try:
        pending = apps.epp_client.restore_domain(user_domain.domain)
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        return render(request, "domains/error.html", {
            "error": error,
            "back_url": reverse('domain', args=(domain_id,))
        })

    if not pending:
        user_domain.delete()
    return redirect('domain', domain_id)


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
def host_create(request, registry_name, host):
    error = None
    form = None

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


@login_required
def contacts(request):
    user_contacts = models.Contact.objects.filter(user=request.user)

    return render(request, "domains/contacts.html", {
        "contacts": user_contacts,
    })


@login_required
def new_contact(request):
    if request.method == "POST":
        form = forms.ContactForm(request.POST, user=request.user)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect('contacts')
    else:
        form = forms.ContactForm(user=request.user)

    return render(request, "domains/contact_form.html", {
        "contact_form": form,
        "title": "New contact"
    })


@login_required
def edit_contact(request, contact_id):
    user_contact = get_object_or_404(models.Contact, id=contact_id)

    if user_contact.user != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = forms.ContactForm(request.POST, user=request.user, instance=user_contact)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect('contacts')
    else:
        form = forms.ContactForm(user=request.user, instance=user_contact)

    return render(request, "domains/contact_form.html", {
        "contact_form": form,
        "title": "Edit contact"
    })


@login_required
def delete_contact(request, contact_id):
    user_contact = get_object_or_404(models.Contact, id=contact_id)

    if user_contact.user != request.user:
        raise PermissionDenied

    can_delete = True

    referrer = reverse('contacts')

    for i in user_contact.contactregistry_set.all():
        try:
            contact_data = apps.epp_client.get_contact(i.registry_contact_id, i.registry_id)
        except grpc.RpcError as rpc_error:
            error = rpc_error.details()
            return render(request, "domains/error.html", {
                "error": error,
                "back_url": referrer
            })

        if apps.epp_api.contact_pb2.Linked in contact_data.statuses:
            can_delete = False
            break

    if request.method == "POST":
        if can_delete and request.POST.get("delete") == "true":
            for i in user_contact.contactregistry_set.all():
                try:
                    apps.epp_client.delete_contact(i.registry_contact_id, i.registry_id)
                except grpc.RpcError as rpc_error:
                    error = rpc_error.details()
                    return render(request, "domains/error.html", {
                        "error": error,
                        "back_url": referrer
                    })
                i.delete()
            user_contact.delete()
            return redirect('contacts')

    return render(request, "domains/delete_contact.html", {
        "contact": user_contact,
        "can_delete": can_delete
    })


@login_required
def addresses(request):
    user_addresses = models.ContactAddress.objects.filter(user=request.user)

    return render(request, "domains/addresses.html", {
        "addresses": user_addresses,
    })


@login_required
def new_address(request):
    if request.method == "POST":
        form = forms.AddressForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect('addresses')
    else:
        form = forms.AddressForm()

    return render(request, "domains/address_form.html", {
        "contact_form": form,
        "title": "New address"
    })


@login_required
def edit_address(request, address_id):
    user_address = get_object_or_404(models.ContactAddress, id=address_id)

    if user_address.user != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = forms.AddressForm(request.POST, instance=user_address)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect('addresses')
    else:
        form = forms.AddressForm(instance=user_address)

    return render(request, "domains/address_form.html", {
        "contact_form": form,
        "title": "Edit address"
    })


@login_required
def delete_address(request, address_id):
    user_address = get_object_or_404(models.ContactAddress, id=address_id)

    if user_address.user != request.user:
        raise PermissionDenied

    can_delete = user_address.local_contacts.count() + user_address.int_contacts.count() == 0
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('hosts')

    if request.method == "POST":
        if can_delete and request.POST.get("delete") == "true":
            user_address.delete()
            return redirect('addresses')

    return render(request, "domains/delete_address.html", {
        "address": user_address,
        "can_delete": can_delete,
        "back_url": referrer
    })
