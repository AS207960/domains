from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import django_keycloak_auth.clients
import django.db
import urllib.parse
from django.utils import timezone
from django.conf import settings
from .. import models, forms, zone_info


@login_required
def contacts(request):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_contacts = models.Contact.get_object_list(access_token)

    return render(request, "domains/contacts.html", {
        "contacts": user_contacts,
    })


@login_required
def setup_contacts(request):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_addresses = models.ContactAddress.get_object_list(access_token)
    user_contacts = models.Contact.get_object_list(access_token)

    if not user_addresses.count() and not user_contacts.count():
        request.session["next_uri"] = request.get_full_path()
        return redirect('new_contact_and_address')

    if not user_addresses.count():
        request.session["next_uri"] = request.get_full_path()
        return redirect('new_address')

    if not user_contacts.count():
        request.session["next_uri"] = request.get_full_path()
        return redirect('new_contact')

    if "setup_domain" in request.session:
        del request.session["setup_domain"]
    if "new_contact_address" in request.session:
        del request.session["new_contact_address"]
    if "after_setup_uri" in request.session:
        return redirect(request.session.pop("after_setup_uri"))
    return redirect('contacts')


@login_required
def new_contact(request):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('contacts')

    if not models.Contact.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    if request.method == "POST":
        form = forms.ContactForm(request.POST, user=request.user)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.created_date = timezone.now()
            form.save()

            request.session["new_contact"] = str(form.instance.id)

            if "next_uri" in request.session:
                return redirect(request.session.pop("next_uri"))
            return redirect('contacts')
    else:
        form = forms.ContactForm(user=request.user)
        if "new_contact_address" in request.session:
            form.fields['local_address'].initial = request.session["new_contact_address"]

    return render(request, "domains/contact_form.html", {
        "contact_form": form,
        "title": "New contact"
    })


@login_required
def edit_contact(request, contact_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_contact = get_object_or_404(models.Contact, id=contact_id)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('addresses')

    if not user_contact.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('addresses')

    sharing_data = {
        "referrer": settings.OIDC_CLIENT_ID,
        "referrer_uri": request.build_absolute_uri()
    }
    sharing_data_uri = urllib.parse.urlencode(sharing_data)
    sharing_uri = f"{settings.KEYCLOAK_SERVER_URL}/auth/realms/{settings.KEYCLOAK_REALM}/account/?{sharing_data_uri}" \
                  f"#/resources/{user_contact.resource_id}"

    if request.method == "POST":
        form = forms.ContactForm(request.POST, user=request.user, instance=user_contact)
        if form.is_valid():
            try:
                form.save()
            except django.db.Error as e:
                return render(request, "domains/error.html", {
                    "error": str(e),
                    "back_url": referrer
                })
            return redirect('contacts')
    else:
        form = forms.ContactForm(user=request.user, instance=user_contact)

    return render(request, "domains/contact_form.html", {
        "contact_form": form,
        "title": "Edit contact",
        "sharing_uri": sharing_uri,
        "contact_obj": user_contact,
    })


@login_required
def delete_contact(request, contact_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_contact = get_object_or_404(models.Contact, id=contact_id)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('addresses')

    if not user_contact.has_scope(access_token, 'delete'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    referrer = reverse('contacts')

    try:
        can_delete = user_contact.can_delete()
    except django.db.Error as e:
        return render(request, "domains/error.html", {
            "error": str(e),
            "back_url": referrer
        })

    if request.method == "POST":
        if can_delete and request.POST.get("delete") == "true":
            try:
                user_contact.delete()
            except django.db.Error as e:
                return render(request, "domains/error.html", {
                    "error": str(e),
                    "back_url": referrer
                })
            return redirect('contacts')

    return render(request, "domains/delete_contact.html", {
        "contact": user_contact,
        "can_delete": can_delete
    })


@login_required
def addresses(request):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_addresses = models.ContactAddress.get_object_list(access_token)

    return render(request, "domains/addresses.html", {
        "addresses": user_addresses,
    })


@login_required
def new_address(request):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('addresses')

    if not models.ContactAddress.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    show_fi = True
    if "setup_domain" in request.session:
        zone, sld = zone_info.get_domain_info(request.session["setup_domain"])
        if not zone or not zone.transfer_supported:
            return render(request, "domains/error.html", {
                "error": "You don't have permission to perform this action",
                "back_url": referrer
            })
        show_fi = zone.registry == zone.REGISTRY_TRAFICOM

    if request.method == "POST":
        form = forms.AddressForm(request.POST, show_fi=show_fi)
        if form.is_valid():
            form.instance.user = request.user
            try:
                form.save()
            except django.db.Error as e:
                return render(request, "domains/error.html", {
                    "error": str(e),
                    "back_url": referrer
                })

            request.session["new_contact_address"] = str(form.instance.id)

            if "next_uri" in request.session:
                return redirect(request.session.pop("next_uri"))
            return redirect('addresses')
    else:
        form = forms.AddressForm(show_fi=show_fi)

    return render(request, "domains/address_form.html", {
        "contact_form": form,
        "title": "New address"
    })


@login_required
def edit_address(request, address_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_address = get_object_or_404(models.ContactAddress, id=address_id)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('addresses')

    if not user_address.has_scope(access_token, 'edit'):
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
                  f"#/resources/{user_address.resource_id}"

    if request.method == "POST":
        form = forms.AddressForm(request.POST, instance=user_address)
        if form.is_valid():
            try:
                form.save()
            except django.db.Error as e:
                return render(request, "domains/error.html", {
                    "error": str(e),
                    "back_url": referrer
                })
            return redirect('addresses')
    else:
        form = forms.AddressForm(instance=user_address)

    return render(request, "domains/address_form.html", {
        "contact_form": form,
        "title": "Edit address",
        "sharing_uri": sharing_uri,
        "address_obj": user_address,
    })


@login_required
def delete_address(request, address_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_address = get_object_or_404(models.ContactAddress, id=address_id)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('addresses')

    if not user_address.has_scope(access_token, 'delete'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    can_delete = user_address.can_delete()

    if request.method == "POST":
        if can_delete and request.POST.get("delete") == "true":
            try:
                user_address.delete()
            except django.db.Error as e:
                return render(request, "domains/error.html", {
                    "error": str(e),
                    "back_url": referrer
                })
            return redirect('addresses')

    return render(request, "domains/delete_address.html", {
        "address": user_address,
        "can_delete": can_delete,
        "back_url": referrer
    })


@login_required
def new_contact_and_address(request):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('contacts')

    if not models.Contact.has_class_scope(access_token, 'create') or \
            not models.ContactAddress.has_class_scope(access_token, 'create'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    show_fi = True
    if "setup_domain" in request.session:
        zone, sld = zone_info.get_domain_info(request.session["setup_domain"])
        if not zone or not zone.transfer_supported:
            return render(request, "domains/error.html", {
                "error": "You don't have permission to perform this action",
                "back_url": referrer
            })
        show_fi = zone.registry == zone.REGISTRY_TRAFICOM

    if request.method == "POST":
        form = forms.ContactAndAddressForm(request.POST, show_fi=show_fi)
        if form.is_valid():
            address = models.ContactAddress(
                description=form.cleaned_data['description'],
                name=form.cleaned_data['name'],
                birthday=form.cleaned_data['birthday'],
                identity_number=form.cleaned_data['identity_number'],
                organisation=form.cleaned_data['organisation'],
                street_1=form.cleaned_data['street_1'],
                street_2=form.cleaned_data['street_2'],
                street_3=form.cleaned_data['street_3'],
                city=form.cleaned_data['city'],
                province=form.cleaned_data['province'],
                postal_code=form.cleaned_data['postal_code'],
                country_code=form.cleaned_data['country_code'],
                disclose_name=form.cleaned_data['disclose_name'],
                disclose_address=form.cleaned_data['disclose_address'],
                disclose_organisation=form.cleaned_data['disclose_organisation'],
                user=request.user
            )
            try:
                address.clean()
            except ValidationError as e:
                for f, e in e.error_dict.items():
                    form.add_error(f, e)

            contact = models.Contact(
                description=form.cleaned_data['description'],
                local_address=address,
                phone=form.cleaned_data['phone'],
                phone_ext=form.cleaned_data['phone_ext'],
                fax=form.cleaned_data['fax'],
                fax_ext=form.cleaned_data['fax_ext'],
                email=form.cleaned_data['email'],
                entity_type=form.cleaned_data['entity_type'],
                trading_name=form.cleaned_data['trading_name'],
                company_number=form.cleaned_data['company_number'],
                disclose_phone=form.cleaned_data['disclose_phone'],
                disclose_fax=form.cleaned_data['disclose_fax'],
                disclose_email=form.cleaned_data['disclose_email'],
                user=request.user,
                created_date=timezone.now()
            )
            try:
                contact.clean()
            except ValidationError as e:
                for f, e in e.error_dict.items():
                    form.add_error(f, e)

            try:
                address.save()
                contact.save()
            except django.db.Error as e:
                return render(request, "domains/error.html", {
                    "error": str(e),
                    "back_url": referrer
                })

            request.session["new_contact"] = str(contact.id)

            if "next_uri" in request.session:
                return redirect(request.session.pop("next_uri"))
            return redirect('contacts')
    else:
        form = forms.ContactAndAddressForm(show_fi=show_fi)

    return render(request, "domains/contact_form.html", {
        "contact_form": form,
        "title": "New contact"
    })
