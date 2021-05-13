from django.db import models, InternalError
from django.core import validators
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import phonenumbers
import django_keycloak_auth.clients
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from . import apps
import uuid
import grpc
import secrets
import typing
import threading
import as207960_utils.models

CONTACT_SEARCH = threading.Lock()
NAME_SERVER_SEARCH = threading.Lock()


def make_secret():
    special = "!@#$%^*"
    ascii_uppercase = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    ascii_lowercase = "abcdefghijkmnpqrstuvwxyz"
    digits = "23456789"
    alphabet = ascii_uppercase + ascii_lowercase + digits + special
    secret = "".join(secrets.choice(alphabet) for _ in range(12))

    for sa in (special, ascii_lowercase, digits, ascii_uppercase):
        if not any(c in secret for c in sa):
            secret += secrets.choice(sa)
        else:
            secret += secrets.choice(alphabet)

    return secret


def make_id():
    return secrets.token_urlsafe(12)[:16].upper()


class ContactAddress(models.Model):
    user: settings.AUTH_USER_MODEL
    id = as207960_utils.models.TypedUUIDField('domains_contactaddress', primary_key=True)
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
    postal_code = models.CharField(max_length=255, null=True)
    country_code = CountryField(verbose_name="Country")
    disclose_name = models.BooleanField(default=False, blank=True)
    disclose_organisation = models.BooleanField(default=False, blank=True)
    disclose_address = models.BooleanField(default=False, blank=True)
    resource_id = models.UUIDField(null=True, db_index=True)

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    class Meta:
        ordering = ['description', 'name']
        verbose_name_plural = "Contact addresses"

    def __str__(self):
        return self.description

    @classmethod
    def get_object_list(cls, access_token: str, action='view'):
        return cls.objects.filter(resource_id__in=as207960_utils.models.get_object_ids(access_token, 'contact-address', action))

    @classmethod
    def has_class_scope(cls, access_token: str, action='view'):
        scope_name = f"{action}-contact-address"
        return django_keycloak_auth.clients.get_authz_client()\
            .eval_permission(access_token, f"contact-address", scope_name)

    def has_scope(self, access_token: str, action='view'):
        scope_name = f"{action}-contact-address"
        return as207960_utils.models.eval_permission(access_token, self.resource_id, scope_name)

    def save(self, *args, **kwargs):
        as207960_utils.models.sync_resource_to_keycloak(
            self,
            display_name="Contact address", scopes=[
                'view-contact-address',
                'edit-contact-address',
                'delete-contact-address',
            ],
            urn="urn:as207960:domains:contact_address", super_save=super().save, view_name='edit_address',
            args=args, kwargs=kwargs
        )

    def delete(self, *args, **kwargs):
        super().delete(*args, *kwargs)
        as207960_utils.models.delete_resource(self.resource_id)

    def can_delete(self):
        return self.local_contacts.count() + self.int_contacts.count() == 0

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

    id = as207960_utils.models.TypedUUIDField('domains_contact', primary_key=True)
    description = models.CharField(max_length=255)
    local_address = models.ForeignKey(
        ContactAddress,
        on_delete=models.PROTECT,
        related_name='local_contacts',
        verbose_name="Localised address"
    )
    int_address = models.ForeignKey(
        ContactAddress,
        on_delete=models.PROTECT,
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
    disclose_phone = models.BooleanField(default=False, blank=True)
    disclose_fax = models.BooleanField(default=False, blank=True)
    disclose_email = models.BooleanField(default=False, blank=True)
    privacy_email = models.UUIDField(default=uuid.uuid4)
    resource_id = models.UUIDField(null=True, db_index=True)

    class Meta:
        ordering = ['description']

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    @classmethod
    def get_object_list(cls, access_token: str, action='view'):
        return cls.objects.filter(resource_id__in=as207960_utils.models.get_object_ids(access_token, 'contact', action))

    @classmethod
    def has_class_scope(cls, access_token: str, action='view'):
        scope_name = f"{action}-contact"
        return django_keycloak_auth.clients.get_authz_client() \
            .eval_permission(access_token, f"contact", scope_name)

    def has_scope(self, access_token: str, action='view'):
        scope_name = f"{action}-contact"
        return as207960_utils.models.eval_permission(access_token, self.resource_id, scope_name)

    def save(self, *args, **kwargs):
        if not kwargs.pop('skip_update_date', False):
            self.updated_date = timezone.now()

        as207960_utils.models.sync_resource_to_keycloak(
            self,
            display_name="Contact", scopes=[
                'view-contact',
                'edit-contact',
                'delete-contact',
            ],
            urn="urn:as207960:domains:contact", super_save=super().save, view_name='edit_contact',
            args=args, kwargs=kwargs
        )
    
    def __str__(self):
        return self.description

    def can_delete(self):
        if self.domains_registrant.count() or self.domains_admin.count() or \
                self.domains_tech.count() or self.domains_billing.count() or \
                self.domain_registration_orders_registrant.count() or self.domain_registration_orders_admin.count() or \
                self.domain_registration_orders_tech.count() or self.domain_registration_orders_billing.count() or \
                self.domain_transfer_orders_registrant.count() or self.domain_transfer_orders_admin.count() or \
                self.domain_transfer_orders_tech.count() or self.domain_transfer_orders_billing.count():
            return False

        for i in self.contactregistry_set.all():
            try:
                contact_data = apps.epp_client.get_contact(i.registry_contact_id, i.registry_id)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
                raise InternalError(error)

            if apps.epp_api.contact_pb2.Linked in contact_data.statuses:
                return False

        return True

    def delete(self, *args, **kwargs):
        for i in self.contactregistry_set.all():
            try:
                apps.epp_client.delete_contact(i.registry_contact_id, i.registry_id)
            except grpc.RpcError as rpc_error:
                error = rpc_error.details()
                raise InternalError(error)
            i.delete()

        as207960_utils.models.delete_resource(self.resource_id)
        super().delete(*args, **kwargs)

    def get_registry_id(self, registry_id: str):
        with CONTACT_SEARCH:
            contact_registry = ContactRegistry.objects.filter(contact=self, registry_id=registry_id)\
                .first()   # type: ContactRegistry
            if contact_registry:
                if not apps.epp_client.check_contact(contact_registry.registry_contact_id, registry_id)[0]:
                    return contact_registry
                else:
                    contact_registry.delete()

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
                email=self.get_public_email(),
                entity_type=self.entity_type,
                trading_name=self.trading_name,
                company_number=self.company_number,
                auth_info=auth_info,
                disclosure=self.get_disclosure(),
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
        with CONTACT_SEARCH:
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

    def get_disclosure(self) -> apps.epp_api.Disclosure:
        disclosure = apps.epp_api.Disclosure(items=[
            apps.epp_api.DisclosureItem(item=apps.epp_api.contact_pb2.DisclosureType.Email)
        ])
        if self.local_address.disclose_name:
            disclosure.items.append(
                apps.epp_api.DisclosureItem(item=apps.epp_api.contact_pb2.DisclosureType.LocalName))
        if self.local_address.disclose_organisation:
            disclosure.items.append(
                apps.epp_api.DisclosureItem(item=apps.epp_api.contact_pb2.DisclosureType.LocalOrganisation))
        if self.local_address.disclose_address:
            disclosure.items.append(
                apps.epp_api.DisclosureItem(item=apps.epp_api.contact_pb2.DisclosureType.LocalAddress))
        if self.int_address:
            if self.int_address.disclose_name:
                disclosure.items.append(
                    apps.epp_api.DisclosureItem(item=apps.epp_api.contact_pb2.DisclosureType.InternationalisedName))
            if self.int_address.disclose_organisation:
                disclosure.items.append(apps.epp_api.DisclosureItem(
                    item=apps.epp_api.contact_pb2.DisclosureType.InternationalisedOrganisation))
            if self.int_address.disclose_address:
                disclosure.items.append(
                    apps.epp_api.DisclosureItem(item=apps.epp_api.contact_pb2.DisclosureType.InternationalisedAddress))
        if self.disclose_phone:
            disclosure.items.append(apps.epp_api.DisclosureItem(item=apps.epp_api.contact_pb2.DisclosureType.Voice))
        if self.disclose_fax:
            disclosure.items.append(apps.epp_api.DisclosureItem(item=apps.epp_api.contact_pb2.DisclosureType.Fax))

        return disclosure

    def get_public_email(self):
        if self.disclose_email:
            return self.email
        else:
            return f"{self.privacy_email.hex}@owowhosth.is"


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
    id = as207960_utils.models.TypedUUIDField('domains_nameserver', primary_key=True)
    name_server = models.CharField(max_length=255)
    registry_id = models.CharField(max_length=255)
    resource_id = models.UUIDField(null=True, db_index=True)

    class Meta:
        ordering = ['name_server']

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    @property
    def unicode_name_server(self):
        try:
            return self.name_server.encode().decode('idna')
        except UnicodeError:
            return self.name_server

    @classmethod
    def get_object_list(cls, access_token: str, action='view'):
        return cls.objects.filter(resource_id__in=as207960_utils.models.get_object_ids(access_token, 'name-server', action))

    @classmethod
    def has_class_scope(cls, access_token: str, action='view'):
        scope_name = f"{action}-name-server"
        return django_keycloak_auth.clients.get_authz_client() \
            .eval_permission(access_token, f"name-server", scope_name)

    def has_scope(self, access_token: str, action='view'):
        scope_name = f"{action}-name-server"
        return as207960_utils.models.eval_permission(access_token, self.resource_id, scope_name)

    def save(self, *args, **kwargs):
        as207960_utils.models.sync_resource_to_keycloak(
            self,
            display_name="Name server", scopes=[
                'view-name-server',
                'edit-name-server',
                'delete-name-server',
            ],
            urn="urn:as207960:domains:name_server", super_save=super().save, view_name='host',
            args=args, kwargs=kwargs
        )

    def delete(self, *args, **kwargs):
        super().delete(*args, *kwargs)
        as207960_utils.models.delete_resource(self.resource_id)

    def __str__(self):
        return self.name_server

    @classmethod
    def get_name_server(cls, name_server: str, registry_id: str, user):
        name_server = name_server.lower()
        with NAME_SERVER_SEARCH:
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
    id = as207960_utils.models.TypedUUIDField('domains_domainregistration', primary_key=True)
    domain = models.CharField(max_length=255)
    auth_info = models.CharField(max_length=255, blank=True, null=True)
    deleted = models.BooleanField(default=False, blank=True)
    former_domain = models.BooleanField(default=False, blank=True)
    transfer_out_pending = models.BooleanField(default=False, blank=True)
    registrant_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domains_registrant')
    admin_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domains_admin')
    billing_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domains_billing')
    tech_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domains_tech')
    resource_id = models.UUIDField(null=True, db_index=True)
    last_billed = models.DateTimeField(default=timezone.datetime.min)
    last_renew_notify = models.DateTimeField(default=timezone.datetime.min)
    deleted_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['domain']

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    @property
    def unicode_domain(self):
        try:
            return self.domain.encode().decode('idna')
        except UnicodeError:
            return self.domain

    @classmethod
    def get_object_list(cls, access_token: str, action='view'):
        return cls.objects.filter(resource_id__in=as207960_utils.models.get_object_ids(access_token, 'domain', action))

    @classmethod
    def has_class_scope(cls, access_token: str, action='view'):
        scope_name = f"{action}-domain"
        return django_keycloak_auth.clients.get_authz_client() \
            .eval_permission(access_token, f"domain", scope_name)

    def has_scope(self, access_token: str, action='view'):
        scope_name = f"{action}-domain"
        return as207960_utils.models.eval_permission(access_token, self.resource_id, scope_name)

    def save(self, *args, **kwargs):
        as207960_utils.models.sync_resource_to_keycloak(
            self,
            display_name="Domain", scopes=[
                'view-domain',
                'edit-domain',
                'delete-domain',
                'create-ns-domain'
            ],
            urn="urn:as207960:domains:domain", super_save=super().save, view_name='domain',
            args=args, kwargs=kwargs
        )

    def delete(self, *args, **kwargs):
        super().delete(*args, *kwargs)
        as207960_utils.models.delete_resource(self.resource_id)

    def get_user(self):
        return as207960_utils.models.get_resource_owner(self.resource_id)

    @property
    def pending_restore(self):
        return self.domainrestoreorder_set.exclude(state__in=("C", "F")).count() != 0

    def __str__(self):
        return self.domain


class SimpleAbstractOrder(models.Model):
    STATE_PENDING = "P"
    STATE_STARTED = "T"
    STATE_NEEDS_PAYMENT = "N"
    STATE_PROCESSING = "S"
    STATE_PENDING_APPROVAL = "A"
    STATE_COMPLETED = "C"
    STATE_FAILED = "F"

    STATES = (
        (STATE_STARTED, "Started"),
        (STATE_NEEDS_PAYMENT, "Needs payment"),
        (STATE_PROCESSING, "Processing"),
        (STATE_PENDING_APPROVAL, "Pending approval"),
        (STATE_COMPLETED, "Completed"),
        (STATE_FAILED, "Failed")
    )

    state = models.CharField(max_length=1, default=STATE_STARTED, choices=STATES)
    charge_state_id = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=9)
    redirect_uri = models.TextField(blank=True, null=True)
    last_error = models.TextField(blank=True, null=True)
    off_session = models.BooleanField(blank=True, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AbstractOrder(SimpleAbstractOrder):
    resource_id = models.UUIDField(null=True, db_index=True)

    resource_type: str
    resource_urn: str
    resource_display_name: str

    class Meta:
        abstract = True

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    @classmethod
    def get_object_list(cls, access_token: str, action='view'):
        return cls.objects.filter(resource_id__in=as207960_utils.models.get_object_ids(access_token, cls.resource_type, action))

    @classmethod
    def has_class_scope(cls, access_token: str, action='view'):
        scope_name = f"{action}-{cls.resource_type}"
        return django_keycloak_auth.clients.get_authz_client() \
            .eval_permission(access_token, cls.resource_type, scope_name)

    def has_scope(self, access_token: str, action='view'):
        scope_name = f"{action}-{self.resource_type}"
        return as207960_utils.models.eval_permission(access_token, self.resource_id, scope_name)

    def save(self, *args, **kwargs):
        as207960_utils.models.sync_resource_to_keycloak(
            self,
            display_name=self.resource_display_name, scopes=[
                f'view-{self.resource_type}',
                f'edit-{self.resource_type}',
                f'delete-{self.resource_type}',
            ],
            urn=self.resource_urn, super_save=super().save, view_name=None,
            args=args, kwargs=kwargs
        )

    def delete(self, *args, **kwargs):
        super().delete(*args, *kwargs)
        as207960_utils.models.delete_resource(self.resource_id)

    def get_user(self):
        if self.user:
            return self.user
        return as207960_utils.models.get_resource_owner(self.resource_id)


class DomainRegistrationOrder(AbstractOrder):
    resource_type = "registration-order"
    resource_urn = "urn:as207960:domains:registration_order"
    resource_display_name = "Registration order"

    id = as207960_utils.models.TypedUUIDField(f'domains_domainregistrationorder', primary_key=True)
    domain = models.CharField(max_length=255)
    domain_id = as207960_utils.models.TypedUUIDField('domains_domainregistration')
    auth_info = models.CharField(max_length=255)
    registrant_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domain_registration_orders_registrant')
    admin_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domain_registration_orders_admin')
    billing_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domain_registration_orders_billing')
    tech_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domain_registration_orders_tech')
    period_unit = models.PositiveSmallIntegerField()
    period_value = models.PositiveSmallIntegerField()
    domain_obj = models.ForeignKey(DomainRegistration, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['domain']

    @property
    def unicode_domain(self):
        try:
            return self.domain.encode().decode('idna')
        except UnicodeError:
            return self.domain

    def __str__(self):
        return self.domain


class DomainTransferOrder(AbstractOrder):
    resource_type = "transfer-order"
    resource_urn = "urn:as207960:domains:transfer_order"
    resource_display_name = "Transfer order"

    id = as207960_utils.models.TypedUUIDField(f'domains_domaintransferorder', primary_key=True)
    domain = models.CharField(max_length=255)
    domain_id = as207960_utils.models.TypedUUIDField('domains_domainregistration')
    auth_code = models.CharField(max_length=255)
    registrant_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domain_transfer_orders_registrant')
    admin_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domain_transfer_orders_admin')
    billing_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domain_transfer_orders_billing')
    tech_contact = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.PROTECT, related_name='domain_transfer_orders_tech')
    domain_obj = models.ForeignKey(DomainRegistration, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['domain']

    @property
    def unicode_domain(self):
        try:
            return self.domain.encode().decode('idna')
        except UnicodeError:
            return self.domain

    def __str__(self):
        return self.domain


class DomainRenewOrder(AbstractOrder):
    resource_type = "renew-order"
    resource_urn = "urn:as207960:domains:renew_order"
    resource_display_name = "Renew order"

    id = as207960_utils.models.TypedUUIDField(f'domains_domainreneworder', primary_key=True)
    domain = models.CharField(max_length=255)
    period_unit = models.PositiveSmallIntegerField()
    period_value = models.PositiveSmallIntegerField()
    domain_obj = models.ForeignKey(DomainRegistration, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['domain']

    @property
    def unicode_domain(self):
        try:
            return self.domain.encode().decode('idna')
        except UnicodeError:
            return self.domain

    def __str__(self):
        return self.domain


class DomainAutomaticRenewOrder(SimpleAbstractOrder):
    id = as207960_utils.models.TypedUUIDField(f'domains_domainautoreneworder', primary_key=True)
    domain = models.CharField(max_length=255)
    period_unit = models.PositiveSmallIntegerField()
    period_value = models.PositiveSmallIntegerField()
    domain_obj = models.ForeignKey(DomainRegistration, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['domain']

    @property
    def unicode_domain(self):
        try:
            return self.domain.encode().decode('idna')
        except UnicodeError:
            return self.domain

    def __str__(self):
        return self.domain


class DomainRestoreOrder(AbstractOrder):
    resource_type = "restore-order"
    resource_urn = "urn:as207960:domains:restore_order"
    resource_display_name = "Restore order"

    id = as207960_utils.models.TypedUUIDField(f'domains_domainrestoreorder', primary_key=True)
    domain = models.CharField(max_length=255)
    domain_obj = models.ForeignKey(DomainRegistration, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['domain']

    @property
    def unicode_domain(self):
        try:
            return self.domain.encode().decode('idna')
        except UnicodeError:
            return self.domain

    def __str__(self):
        return self.domain


class HangoutsSpaces(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space_id = models.CharField(max_length=255)


class HangoutsUsers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user = models.CharField(max_length=255)


class HangoutsUserLinkState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    return_url = models.URLField(max_length=1000)
    message_name = models.CharField(max_length=255)
    linked = models.BooleanField(default=False, blank=True)
    user = models.CharField(max_length=255)
