from django.db import models
from django.core import validators
from django.conf import settings
from django.utils import timezone
import phonenumbers
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from . import apps
import uuid
import secrets
import string
import typing


def make_secret():
    special = "!@#$%^*"
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + special
    secret = "".join(secrets.choice(alphabet) for i in range(12))
    if not any(c in secret for c in special):
        secret += secrets.choice(special)
    else:
        secret += secrets.choice(alphabet)
    if not any(c in secret for c in string.ascii_lowercase):
        secret += secrets.choice(string.ascii_lowercase)
    else:
        secret += secrets.choice(alphabet)
    if not any(c in secret for c in string.digits):
        secret += secrets.choice(string.digits)
    else:
        secret += secrets.choice(alphabet)
    if not any(c in secret for c in string.ascii_uppercase):
        secret += secrets.choice(string.ascii_uppercase)
    else:
        secret += secrets.choice(alphabet)
    return secret


def make_id():
    return secrets.token_urlsafe(12)[:16].upper()


class ContactAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    description = models.CharField(max_length=255)
    name = models.CharField(max_length=255, validators=[validators.MinLengthValidator(4)])
    birthday = models.DateField(blank=True, null=True)
    identity_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="National identity number")
    organisation = models.CharField(max_length=255, blank=True, null=True)
    street_1 = models.CharField(max_length=255, verbose_name="Address line 1")
    street_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Address line 2")
    street_3 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Address line 3")
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255)
    country_code = CountryField(verbose_name="Country")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    disclose_name = models.BooleanField(default=False, blank=True)
    disclose_organisation = models.BooleanField(default=False, blank=True)
    disclose_address = models.BooleanField(default=False, blank=True)

    class Meta:
        ordering = ['description', 'name']
        verbose_name_plural = "Contact addresses"

    def __str__(self):
        return self.description

    def as_api_obj(self):
        streets = [self.street_1]
        if self.street_2:
            streets.append(self.street_2)
        if self.street_3:
            streets.append(self.street_3)

        return apps.epp_api.Address(
            name=self.name,
            organisation=self.organisation,
            streets=streets,
            city=self.city,
            province=self.province,
            postal_code=self.postal_code,
            country_code=self.country_code.code,
            birth_date=self.birthday,
            identity_number=self.identity_number
        )


class Contact(models.Model):
    ENTITY_TYPES = (
        (0, "Not set"),
        (1, "Unknown entity"),
        (2, "UK Limited Company"),
        (3, "UK Public Limited Company"),
        (4, "UK Partnership"),
        (5, "UK Sole Trader"),
        (6, "UK Limited Liability Partnership"),
        (7, "UK Industrial Provident Registered Company"),
        (8, "UK Individual"),
        (9, "UK School"),
        (10, "UK Registered Charity"),
        (11, "UK Government Body"),
        (12, "UK Corporation by Royal Charter"),
        (13, "UK Statutory Body"),
        (31, "UK Political party"),
        (14, "Other UK Entity"),
        (15, "Finnish Individual"),
        (16, "Finnish Company"),
        (17, "Finnish Association"),
        (18, "Finnish Institution"),
        (19, "Finnish Political Party"),
        (20, "Finnish Municipality"),
        (21, "Finnish Government"),
        (22, "Finnish Public Community"),
        (23, "Other Individual"),
        (24, "Other Company"),
        (25, "Other Association"),
        (26, "Other Institution"),
        (27, "Other Political Party"),
        (28, "Other Municipality"),
        (29, "Other Government"),
        (30, "Other Public Community"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    description = models.CharField(max_length=255)
    local_address = models.ForeignKey(
        ContactAddress,
        on_delete=models.PROTECT,
        related_name='local_contacts',
        verbose_name="Localised address"
    )
    int_address = models.ForeignKey(
        ContactAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='int_contacts',
        verbose_name="Internationalised address"
    )
    phone = PhoneNumberField(blank=False, null=True)
    phone_ext = models.CharField(max_length=64, blank=True, null=True, verbose_name="Phone extension")
    fax = PhoneNumberField(blank=True, null=True)
    fax_ext = models.CharField(max_length=64, blank=True, null=True, verbose_name="Fax extension")
    email = models.EmailField()
    entity_type = models.PositiveSmallIntegerField(choices=ENTITY_TYPES)
    trading_name = models.CharField(max_length=255, blank=True, null=True)
    company_number = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    disclose_phone = models.BooleanField(default=False, blank=True)
    disclose_fax = models.BooleanField(default=False, blank=True)
    disclose_email = models.BooleanField(default=False, blank=True)

    class Meta:
        ordering = ['description']

    def save(self, *args, **kwargs):
        if not kwargs.pop('skip_update_date', False):
            self.updated_date = timezone.now()

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.description

    def get_registry_id(self, registry_id: str):
        contact_registry = ContactRegistry.objects.filter(contact=self, registry_id=registry_id).first()
        if contact_registry:
            return contact_registry

        contact_id = make_id()
        auth_info = make_secret()
        while not apps.epp_client.check_contact(contact_id, registry_id)[0]:
            contact_id = make_id()

        contact_id, _, _ = apps.epp_client.create_contact(
            contact_id,
            local_address=self.get_local_address(),
            int_address=self.get_int_address(),
            phone=apps.epp_api.Phone(
                number=f"+{self.phone.country_code}.{self.phone.national_number}",
                ext=self.phone_ext
            ) if self.phone else None,
            fax=apps.epp_api.Phone(
                number=f"+{self.fax.country_code}.{self.fax.national_number}",
                ext=self.fax_ext
            ) if self.fax else None,
            email=self.email,
            entity_type=self.entity_type,
            trading_name=self.trading_name,
            company_number=self.company_number,
            auth_info=auth_info,
            registry_name=registry_id
        )

        contact_registry = ContactRegistry(
            contact=self,
            registry_id=registry_id,
            registry_contact_id=contact_id,
            auth_info=auth_info
        )
        contact_registry.save()
        return contact_registry

    @classmethod
    def get_contact(cls, registry_contact_id: str, registry_id: str, user):
        contact_registry = ContactRegistry.objects\
            .filter(registry_contact_id=registry_contact_id, registry_id=registry_id).first()
        if contact_registry:
            return contact_registry.contact

        registry_contact = apps.epp_client.get_contact(registry_contact_id, registry_id)

        local_streets = iter(registry_contact.local_address.streets)
        local_address = ContactAddress(
            description=registry_contact.local_address.name,
            name=registry_contact.local_address.name,
            organisation=registry_contact.local_address.organisation,
            street_1=next(local_streets, None),
            street_2=next(local_streets, None),
            street_3=next(local_streets, None),
            city=registry_contact.local_address.city,
            province=registry_contact.local_address.province,
            postal_code=registry_contact.local_address.postal_code,
            country_code=registry_contact.local_address.country_code,
            user=user
        )
        local_address.save()
        if registry_contact.int_address:
            int_streets = iter(registry_contact.int_address.streets)
            int_address = ContactAddress(
                description=registry_contact.int_address.name,
                name=registry_contact.int_address.name,
                organisation=registry_contact.int_address.organisation,
                street_1=next(int_streets, None),
                street_2=next(int_streets, None),
                street_3=next(int_streets, None),
                city=registry_contact.int_address.city,
                province=registry_contact.int_address.province,
                postal_code=registry_contact.int_address.postal_code,
                country_code=registry_contact.int_address.country_code,
                user=user
            )
            int_address.save()
        else:
            int_address = None

        if registry_contact.phone:
            phone = phonenumbers.parse(registry_contact.phone.number, settings.PHONENUMBER_DEFAULT_REGION)
            if not phonenumbers.is_valid_number(phone):
                phone = None
        else:
            phone = None

        if registry_contact.fax:
            fax = phonenumbers.parse(registry_contact.fax.number, settings.PHONENUMBER_DEFAULT_REGION)
            if not phonenumbers.is_valid_number(fax):
                fax = None
        else:
            fax = None

        contact = cls(
            description=registry_contact.local_address.name,
            local_address=local_address,
            int_address=int_address,
            phone=phone,
            phone_ext=registry_contact.phone.ext if registry_contact.phone else None,
            fax=fax,
            fax_ext=registry_contact.fax.ext if registry_contact.fax else None,
            email=registry_contact.email,
            entity_type=registry_contact.entity_type,
            trading_name=registry_contact.trading_name,
            company_number=registry_contact.company_number,
            created_date=registry_contact.creation_date,
            updated_date=registry_contact.last_updated_date,
            user=user
        )
        contact.save(skip_update_date=True)
        ContactRegistry(
            contact=contact,
            registry_contact_id=registry_contact_id,
            registry_id=registry_id,
            auth_info=registry_contact.auth_info
        ).save()
        return contact

    def get_local_address(self) -> apps.epp_api.Address:
        return self.local_address.as_api_obj()

    def get_int_address(self) -> typing.Optional[apps.epp_api.Address]:
        return self.int_address.as_api_obj() if self.int_address else None


class ContactRegistry(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    registry_contact_id = models.CharField(max_length=16, default=make_id)
    registry_id = models.CharField(max_length=255)
    auth_info = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Contact registries"
        ordering = ["registry_contact_id"]

    def __str__(self):
        return f"{self.contact.description} ({self.registry_id})"


class NameServer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name_server = models.CharField(max_length=255)
    registry_id = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['name_server']

    def __str__(self):
        return self.name_server

    @classmethod
    def get_name_server(cls, name_server: str, registry_id: str, user):
        name_server_obj = cls.objects.filter(name_server=name_server, registry_id=registry_id).first()
        if name_server_obj:
            return name_server_obj

        name_server_obj = cls(
            name_server=name_server,
            registry_id=registry_id,
            user=user
        )
        name_server_obj.save()
        return name_server_obj


class DomainRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    domain = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    auth_info = models.CharField(max_length=255, blank=True, null=True)
    pending = models.BooleanField(default=False, blank=True)
    registrant_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.SET_NULL, related_name='domains_registrant')
    admin_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.SET_NULL, related_name='domains_admin')
    billing_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.SET_NULL, related_name='domains_billing')
    tech_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.SET_NULL, related_name='domains_tech')

    class Meta:
        ordering = ['domain']

    def __str__(self):
        return self.domain


class PendingDomainTransfer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    domain = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    auth_info = models.CharField(max_length=255, blank=True, null=True)
    registrant_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.SET_NULL, related_name='pending_domains_registrant')
    admin_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.SET_NULL, related_name='pending_domains_admin')
    billing_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.SET_NULL, related_name='pending_domains_billing')
    tech_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.SET_NULL, related_name='pending_domains_tech')

    class Meta:
        ordering = ['domain']

    def __str__(self):
        return self.domain
