from rest_framework import serializers, exceptions
from django.core.exceptions import PermissionDenied
import dataclasses
import typing
import datetime
import ipaddress
import uuid

from .. import models, apps


class ObjectExists(exceptions.APIException):
    status_code = 409
    default_detail = 'Object already exists'
    default_code = 'object_exists'


class ContactAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactAddress
        fields = ('url', 'id', 'description', 'name', 'organisation', 'street_1', 'street_2', 'street_3', 'city',
                  'province', 'postal_code', 'country_code', 'birthday', 'identity_number', 'disclose_name',
                  'disclose_organisation', 'disclose_address')


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = ('url', 'id', 'description', 'local_address', 'int_address', 'phone', 'phone_ext', 'fax', 'fax_ext',
                  'email', 'entity_type', 'trading_name', 'company_number', 'disclose_phone', 'disclose_fax',
                  'disclose_email')
        read_only_fields = ('created_date', 'updated_date')


@dataclasses.dataclass
class NameServer:
    id: str
    name_server: str
    statuses: [str]
    addresses: [str]
    created: typing.Optional[datetime.datetime]
    last_updated: typing.Optional[datetime.datetime]
    last_transferred: typing.Optional[datetime.datetime]
    host_obj: apps.epp_api.Host


class NameServerSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(view_name='nameserver-detail', lookup_field='id', lookup_url_kwarg='pk')
    id = serializers.UUIDField(read_only=True)
    name_server = serializers.CharField(max_length=255)
    statuses = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )
    addresses = serializers.ListField(
        child=serializers.IPAddressField()
    )
    created = serializers.DateTimeField(read_only=True, allow_null=True)
    last_updated = serializers.DateTimeField(read_only=True, allow_null=True)
    last_transferred = serializers.DateTimeField(read_only=True, allow_null=True)

    @classmethod
    def get_host(cls, h: models.NameServer):
        host = apps.epp_client.get_host(h.name_server, h.registry_id)
        return NameServer(
            id=h.id,
            name_server=host.name,
            statuses=list(map(lambda s: s.name, host.statuses)),
            addresses=list(map(lambda a: a.address, host.addresses)),
            created=host.creation_date,
            last_updated=host.last_updated_date,
            last_transferred=host.last_transfer_date,
            host_obj=host
        )

    @staticmethod
    def map_addrs(addrs):
        addr_objs = []
        for address in addrs:
            address = ipaddress.ip_address(address)
            ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.UNKNOWN
            if address.version == 4:
                ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.IPv4
            elif address.version == 6:
                ip_type = apps.epp_api.common_pb2.IPAddress.IPVersion.IPv6
            addr_objs.append(apps.epp_api.IPAddress(
                address=address.compressed,
                ip_type=ip_type
            ))
        return addr_objs

    def create(self, validated_data):
        host = validated_data['name_server']

        domain = None  # type: typing.Optional[models.DomainRegistration]
        for domain_obj in models.DomainRegistration.objects.filter(user=self.context['request'].user):
            if host.endswith(domain_obj.domain):
                domain = domain_obj
                break

        if not domain:
            raise PermissionDenied

        domain_data = apps.epp_client.get_domain(domain.domain)
        available, _ = apps.epp_client.check_host(host, domain_data.registry_name)
        if not available:
            raise ObjectExists()

        apps.epp_client.create_host(host, self.map_addrs(validated_data['addresses']), domain_data.registry_name)
        host_obj = models.NameServer(
            name_server=host,
            registry_id=domain_data.registry_name,
            user=self.context['request'].user
        )
        host_obj.save()

        return self.get_host(host_obj)

    def update(self, instance: NameServer, validated_data):
        if 'addresses' in validated_data:
            instance.addresses = validated_data['addresses']
            instance.host_obj.set_addresses(self.map_addrs(validated_data['addresses']))
        return instance


@dataclasses.dataclass
class Domain:
    id: str
    domain: str
    statuses: [str]
    registrant: models.Contact
    admin_contact: typing.Optional[models.Contact]
    billing_contact: typing.Optional[models.Contact]
    tech_contact: typing.Optional[models.Contact]
    created: typing.Optional[datetime.datetime]
    expiry: typing.Optional[datetime.datetime]
    last_updated: typing.Optional[datetime.datetime]
    last_transferred: typing.Optional[datetime.datetime]
    domain_obj: apps.epp_api.Domain


class DomainNameServerSerializer(serializers.Serializer):
    host_object = serializers.CharField(max_length=255)
    addresses = serializers.ListField(
        child=serializers.IPAddressField()
    )

class DomainSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(view_name='domain-detail', lookup_field='id', lookup_url_kwarg='pk')
    id = serializers.UUIDField(read_only=True)
    domain = serializers.CharField(max_length=255)
    statuses = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )
    registrant = serializers.PrimaryKeyRelatedField(queryset=models.Contact.objects.all())
    registrant_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='registrant', read_only=True,
    )
    admin_contact = serializers.PrimaryKeyRelatedField(queryset=models.Contact.objects.all(), allow_null=True)
    admin_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='admin_contact', allow_null=True, read_only=True
    )
    billing_contact = serializers.PrimaryKeyRelatedField(queryset=models.Contact.objects.all(), allow_null=True)
    billing_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='billing_contact', allow_null=True, read_only=True
    )
    tech_contact = serializers.PrimaryKeyRelatedField(queryset=models.Contact.objects.all(), allow_null=True)
    tech_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='tech_contact', allow_null=True, read_only=True
    )
    created = serializers.DateTimeField(read_only=True, allow_null=True)
    expiry = serializers.DateTimeField(read_only=True, allow_null=True)
    last_updated = serializers.DateTimeField(read_only=True, allow_null=True)
    last_transferred = serializers.DateTimeField(read_only=True, allow_null=True)

    @classmethod
    def get_domain(cls, d: models.DomainRegistration, user):
        domain = apps.epp_client.get_domain(d.domain)
        registrant = models.Contact.get_contact(domain.registrant, domain.registry_name, user)
        if domain.admin:
            admin = models.Contact.get_contact(domain.admin.contact_id, domain.registry_name, user)
        elif d.admin_contact:
            admin = d.admin_contact
        else:
            admin = None
        if domain.billing:
            billing = models.Contact.get_contact(domain.billing.contact_id, domain.registry_name, user)
        elif d.billing_contact:
            billing = d.billing_contact
        else:
            billing = None
        if domain.tech:
            tech = models.Contact.get_contact(domain.tech.contact_id, domain.registry_name, user)
        elif d.tech_contact:
            tech = d.tech_contact
        else:
            tech = None

        return Domain(
            id=d.id,
            domain=d.domain,
            statuses=list(map(lambda s: s.name, domain.statuses)),
            registrant=registrant,
            admin_contact=admin,
            billing_contact=billing,
            tech_contact=tech,
            created=domain.creation_date,
            expiry=domain.creation_date,
            last_updated=domain.last_updated_date,
            last_transferred=domain.last_transfer_date,
            domain_obj=domain
        )
