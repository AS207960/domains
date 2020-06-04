from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
import django.db
from django.utils import timezone
from .. import models, forms


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
            form.instance.created_date = timezone.now()
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
    user_addresses = models.ContactAddress.objects.filter(user=request.user)

    return render(request, "domains/addresses.html", {
        "addresses": user_addresses,
    })


@login_required
def new_address(request):
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('addresses')

    if request.method == "POST":
        form = forms.AddressForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            try:
                form.save()
            except django.db.Error as e:
                return render(request, "domains/error.html", {
                    "error": str(e),
                    "back_url": referrer
                })
            return redirect(referrer)
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

    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('addresses')

    if request.method == "POST":
        form = forms.AddressForm(request.POST, instance=user_address)
        if form.is_valid():
            form.instance.user = request.user
            try:
                form.save()
            except django.db.Error as e:
                return render(request, "domains/error.html", {
                    "error": str(e),
                    "back_url": referrer
                })
            return redirect(referrer)
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

    can_delete = user_address.can_delete()
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('addresses')

    if request.method == "POST":
        if can_delete and request.POST.get("delete") == "true":
            try:
                user_address.delete()
            except django.db.Error as e:
                return render(request, "domains/error.html", {
                    "error": str(e),
                    "back_url": referrer
                })
            return redirect(referrer)

    return render(request, "domains/delete_address.html", {
        "address": user_address,
        "can_delete": can_delete,
        "back_url": referrer
    })
