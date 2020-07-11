import dataclasses
import datetime
import decimal
import ipaddress
import typing
import uuid

import grpc
from django.core.exceptions import PermissionDenied
from rest_framework import exceptions, serializers
from rest_framework.settings import api_settings

from .. import apps, models, zone_info
from ..views import billing, gchat_bot


class ObjectExists(exceptions.APIException):
    status_code = 409
    default_detail = 'Object already exists'
    default_code = 'object_exists'


class BillingError(exceptions.APIException):
    status_code = 402
    default_detail = 'Error billing account'
    default_code = 'billing_error'


class Unsupported(exceptions.APIException):
    status_code = 400
    default_detail = 'Unsupported by the registry'
    default_code = 'unsupported'


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

    def validate(self, data):
        errs = {}

        for k in ('local_address', 'int_address'):
            if data.get(k):
                if not data[k].has_scope(self.context['request'].auth.token, 'view'):
                    errs[k] = "you don't have permission to reference this object"

        if errs:
            raise serializers.ValidationError(errs)
        return data


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
        for domain_obj in models.DomainRegistration.get_object_list(
                self.context['request'].auth.token, action='create-ns'
        ):
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
class DomainNameServer:
    host_object: typing.Optional[str]
    host_name: typing.Optional[str]
    addresses: typing.Optional[typing.List[str]]


@dataclasses.dataclass
class Domain:
    id: str
    domain: str
    statuses: [str]
    deleted: bool
    registrant: models.Contact
    admin_contact: typing.Optional[models.Contact]
    billing_contact: typing.Optional[models.Contact]
    tech_contact: typing.Optional[models.Contact]
    name_servers: typing.List[DomainNameServer]
    hosts: typing.List[models.NameServer]
    rgp_state: typing.List[str]
    auth_info: typing.Optional[str]
    sec_dns: typing.Optional[apps.epp_api.SecDNSData]
    created: typing.Optional[datetime.datetime]
    expiry: typing.Optional[datetime.datetime]
    last_updated: typing.Optional[datetime.datetime]
    last_transferred: typing.Optional[datetime.datetime]
    domain_db_obj: models.DomainRegistration
    domain_obj: apps.epp_api.Domain


@dataclasses.dataclass
class DomainCreate:
    id: str
    domain: str
    registrant: models.Contact
    admin_contact: typing.Optional[models.Contact]
    billing_contact: typing.Optional[models.Contact]
    tech_contact: typing.Optional[models.Contact]
    name_servers: typing.List[DomainNameServer]
    auth_info: typing.Optional[str]
    sec_dns: typing.Optional[apps.epp_api.SecDNSData]
    pending: bool
    created: typing.Optional[datetime.datetime]
    expiry: typing.Optional[datetime.datetime]


@dataclasses.dataclass
class DomainCheck:
    domain: str
    available: bool
    reason: typing.Optional[str]
    price: typing.Optional[decimal.Decimal]


class DomainNameServerSerializer(serializers.Serializer):
    host_object = serializers.CharField(max_length=255, allow_null=True)
    host_name = serializers.CharField(max_length=255, allow_null=True)
    addresses = serializers.ListField(
        child=serializers.IPAddressField(),
        allow_null=True
    )


class DomainNameHostSerializer(serializers.Serializer):
    host_object = serializers.PrimaryKeyRelatedField(read_only=True, source='id')
    host_object_url = serializers.HyperlinkedRelatedField(
        view_name='nameserver-detail', source='id', read_only=True
    )


class DomainSecDNSKeyDataSerializer(serializers.Serializer):
    flags = serializers.IntegerField()
    protocol = serializers.IntegerField()
    algorithm = serializers.IntegerField()
    public_key = serializers.CharField(max_length=255)

    def validate(self, data):
        errs = {}
        for k in ('flags', 'protocol', 'algorithm', 'public_key'):
            if k not in data:
                errs[k] = "this field is required"

        if errs:
            raise serializers.ValidationError(errs)
        return data


class DomainSecDNSDSDataSerializer(serializers.Serializer):
    key_tag = serializers.IntegerField()
    algorithm = serializers.IntegerField()
    digest_type = serializers.IntegerField()
    digest = serializers.CharField(max_length=255)
    key_data = DomainSecDNSKeyDataSerializer(allow_null=True)

    def validate(self, data):
        errs = {}
        for k in ('key_tag', 'algorithm', 'digest_type', 'digest'):
            if k not in data:
                errs[k] = "this field is required"

        if errs:
            raise serializers.ValidationError(errs)
        return data


class DomainSecDNSSerializer(serializers.Serializer):
    max_sig_life = serializers.DurationField(allow_null=True)
    ds_data = serializers.ListField(
        child=DomainSecDNSDSDataSerializer(),
        allow_null=True
    )
    key_data = serializers.ListField(
        child=DomainSecDNSKeyDataSerializer(),
        allow_null=True
    )

    def validate(self, data):
        errs = {}
        for k in ('max_sig_life', 'ds_data', 'key_data'):
            if k not in data:
                errs[k] = "this field is required"
        if data.get('ds_data') and data.get('key_data'):
            errs[api_settings.NON_FIELD_ERRORS_KEY] = "can't set both ds_data and key_data"
        if not (data.get('ds_data') or data.get('key_data')):
            errs[api_settings.NON_FIELD_ERRORS_KEY] = "must set one of ds_data or key_data"

        if errs:
            raise serializers.ValidationError(errs)
        return data


class DomainPeriodSerializer(serializers.Serializer):
    unit = serializers.ChoiceField(choices=(
        ("y", "Year"),
        ("m", "Month")
    ))
    value = serializers.IntegerField(min_value=1)


class DomainSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(view_name='domain-detail', lookup_field='id', lookup_url_kwarg='pk')
    id = serializers.UUIDField(read_only=True)
    domain = serializers.CharField(max_length=255, read_only=True)
    statuses = serializers.ListField(
        child=serializers.CharField(read_only=True),
        read_only=True
    )
    deleted = serializers.BooleanField(read_only=True)
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
    name_servers = serializers.ListField(
        child=DomainNameServerSerializer()
    )
    hosts = serializers.ListField(
        child=DomainNameHostSerializer(read_only=True),
        read_only=True
    )
    rgp_state = serializers.ListField(
        child=serializers.CharField(max_length=255, read_only=True, allow_null=True),
        read_only=True
    )
    auth_info = serializers.CharField(max_length=255, read_only=True)
    sec_dns = DomainSecDNSSerializer(allow_null=True)
    block_transfer = serializers.BooleanField(write_only=True)
    regen_auth_code = serializers.BooleanField(write_only=True, required=False)
    created = serializers.DateTimeField(read_only=True, allow_null=True)
    expiry = serializers.DateTimeField(read_only=True, allow_null=True)
    last_updated = serializers.DateTimeField(read_only=True, allow_null=True)
    last_transferred = serializers.DateTimeField(read_only=True, allow_null=True)

    def validate(self, data):
        errs = {}

        for k in ('registrant', 'admin_contact', 'billing_contact', 'tech_contact'):
            if data.get(k):
                if not data[k].has_scope(self.context['request'].auth.token, 'view'):
                    errs[k] = "you don't have permission to reference this object"

        if errs:
            raise serializers.ValidationError(errs)
        return data

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

        name_servers = []
        for ns in domain.name_servers:
            if ns.host_obj:
                name_servers.append(DomainNameServer(
                    host_object=ns.host_obj,
                    host_name=None,
                    addresses=None
                ))
            else:
                name_servers.append(DomainNameServer(
                    host_object=None,
                    host_name=ns.host_name,
                    addresses=list(map(lambda a: a.address, ns.address))
                ))

        hosts = []
        for ns in domain.hosts:
            ns_obj = models.NameServer.get_name_server(
                ns,
                domain.registry_name,
                user
            )
            hosts.append(ns_obj)

        return Domain(
            id=d.id,
            domain=d.domain,
            statuses=list(map(lambda s: s.name, domain.statuses)),
            deleted=d.deleted,
            registrant=registrant,
            admin_contact=admin,
            billing_contact=billing,
            tech_contact=tech,
            name_servers=name_servers,
            hosts=hosts,
            rgp_state=list(map(lambda s: s.name, domain.rgp_state)),
            auth_info=d.auth_info,
            sec_dns=domain.sec_dns,
            created=domain.creation_date,
            expiry=domain.expiry_date,
            last_updated=domain.last_updated_date,
            last_transferred=domain.last_transfer_date,
            domain_obj=domain,
            domain_db_obj=d
        )

    def update(self, instance: Domain, validated_data):
        domain_info = zone_info.get_domain_info(instance.domain)[0]  # type: zone_info.DomainInfo
        update_req = apps.epp_api.domain_pb2.DomainUpdateRequest(
            name=instance.domain,
            remove=[],
            add=[]
        )

        if 'registrant' in validated_data and validated_data['registrant'] != instance.registrant \
                and domain_info.registrant_change_supported:
            instance.registrant = validated_data['registrant']
            if domain_info.registrant_supported:
                update_req.new_registrant.value = instance.registrant.get_registry_id(
                    instance.domain_obj.registry_name
                ).registry_contact_id
            instance.domain_db_obj.registrant_contact = instance.registrant

        if 'admin_contact' in validated_data and validated_data['admin_contact'] != instance.admin_contact:
            if not validated_data['admin_contact'] and domain_info.admin_required:
                raise serializers.ValidationError('Admin contact required')
            instance.admin_contact = validated_data['admin_contact']
            if instance.admin_contact != instance.domain_db_obj.user:
                raise PermissionDenied
            if domain_info.admin_supported:
                old_contact = instance.domain_obj.get_contact('admin')
                if old_contact:
                    update_req.remove.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                        contact=apps.epp_api.domain_pb2.Contact(
                            type='admin',
                            id=old_contact.contact_id
                        )
                    ))
                if instance.admin_contact:
                    update_req.add.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                        contact=apps.epp_api.domain_pb2.Contact(
                            type='admin',
                            id=instance.admin_contact.get_registry_id(
                                instance.domain_obj.registry_name
                            ).registry_contact_id
                        )
                    ))
            instance.domain_db_obj.admin_contact = instance.admin_contact

        if 'billing_contact' in validated_data and validated_data['billing_contact'] != instance.billing_contact:
            if not validated_data['billing_contact'] and domain_info.billing_required:
                raise serializers.ValidationError('Billing contact required')
            instance.billing_contact = validated_data['billing_contact']
            if instance.billing_contact != instance.domain_db_obj.user:
                raise PermissionDenied
            if domain_info.billing_supported:
                old_contact = instance.domain_obj.get_contact('billing')
                if old_contact:
                    update_req.remove.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                        contact=apps.epp_api.domain_pb2.Contact(
                            type='billing',
                            id=old_contact.contact_id
                        )
                    ))
                if instance.billing_contact:
                    update_req.add.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                        contact=apps.epp_api.domain_pb2.Contact(
                            type='billing',
                            id=instance.billing_contact.get_registry_id(
                                instance.domain_obj.registry_name
                            ).registry_contact_id
                        )
                    ))
            instance.domain_db_obj.billing_contact = instance.billing_contact

        if 'tech_contact' in validated_data and validated_data['tech_contact'] != instance.tech_contact:
            if not validated_data['tech_contact'] and domain_info.tech_required:
                raise serializers.ValidationError('Tech contact required')
            instance.tech_contact = validated_data['tech_contact']
            if instance.tech_contact != instance.domain_db_obj.user:
                raise PermissionDenied
            if domain_info.tech_supported:
                old_contact = instance.domain_obj.get_contact('tech')
                if old_contact:
                    update_req.remove.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                        contact=apps.epp_api.domain_pb2.Contact(
                            type='tech',
                            id=old_contact.contact_id
                        )
                    ))
                if instance.tech_contact:
                    update_req.add.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                        contact=apps.epp_api.domain_pb2.Contact(
                            type='tech',
                            id=instance.tech_contact.get_registry_id(
                                instance.domain_obj.registry_name
                            ).registry_contact_id
                        )
                    ))
            instance.domain_db_obj.tech_contact = instance.tech_contact

        if 'name_servers' in validated_data:
            new_name_servers = list(map(
                lambda n: DomainNameServer(**{"host_object": None, "host_name": None, "addresses": None, **n}),
                validated_data['name_servers']
            ))
            rem_name_servers = list(filter(lambda n: n not in new_name_servers, instance.name_servers))
            add_name_servers = list(filter(lambda n: n not in instance.name_servers, new_name_servers))

            for ns in add_name_servers:
                if ns.host_object:
                    host_available, _ = apps.epp_client.check_host(ns.host_object, instance.domain_obj.registry_name)
                    if host_available:
                        apps.epp_client.create_host(ns.host_object, [], instance.domain_obj.registry_name)
                    update_req.add.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                        nameserver=apps.epp_api.domain_pb2.NameServer(
                            host_obj=ns.host_object
                        )
                    ))
                elif ns.host_name:
                    update_req.add.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                        nameserver=apps.epp_api.domain_pb2.NameServer(
                            host_name=ns.host_name,
                            addresses=NameServerSerializer.map_addrs(ns.addresses)
                        )
                    ))

            for ns in rem_name_servers:
                if ns.host_object:
                    update_req.remove.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                        nameserver=apps.epp_api.domain_pb2.NameServer(
                            host_obj=ns.host_object
                        )
                    ))
                elif ns.host_name:
                    update_req.remove.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                        nameserver=apps.epp_api.domain_pb2.NameServer(
                            host_name=ns.host_name,
                            addresses=NameServerSerializer.map_addrs(ns.addresses)
                        )
                    ))

            instance.name_servers = new_name_servers

        if 'sec_dns' in validated_data:
            sec_dns = validated_data['sec_dns']

            if sec_dns is None:
                update_req.sec_dns.remove_all = True
                instance.sec_dns = None
            else:
                new_sec_dns = apps.epp_api.SecDNSData(
                    max_sig_life=sec_dns['max_sig_life'],
                    ds_data=list(map(lambda k: apps.epp_api.SecDNSDSData(
                        key_tag=k['key_tag'],
                        algorithm=k['algorithm'],
                        digest_type=k['digest_type'],
                        digest=k['digest'],
                        key_data=apps.epp_api.SecDNSKeyData(
                            **k['key_data']
                        ) if 'key_data' in k and k['key_data'] else None
                    ), sec_dns['ds_data'])) if sec_dns['ds_data'] is not None else None,
                    key_data=list(map(
                        lambda k: apps.epp_api.SecDNSKeyData(**k),
                        sec_dns['key_data']
                    )) if sec_dns['key_data'] is not None else None,
                )

                new_ds_data = new_sec_dns.ds_data if new_sec_dns.ds_data else []
                old_ds_data = (
                    instance.sec_dns.ds_data if instance.sec_dns.ds_data else []
                ) if instance.sec_dns else []
                new_key_data = new_sec_dns.key_data if new_sec_dns.key_data else []
                old_key_data = (
                    instance.sec_dns.key_data if instance.sec_dns.key_data else []
                ) if instance.sec_dns else []

                rem_ds_data = list(filter(lambda n: n not in new_ds_data, old_ds_data))
                add_ds_data = list(filter(lambda n: n not in old_ds_data, new_ds_data))
                rem_key_data = list(filter(lambda n: n not in new_key_data, old_key_data))
                add_key_data = list(filter(lambda n: n not in old_key_data, new_key_data))

                if new_sec_dns.max_sig_life and (
                        instance.sec_dns is None or new_sec_dns.max_sig_life != instance.sec_dns.max_sig_life
                ):
                    update_req.sec_dns.new_max_sig_life.value = new_sec_dns.max_sig_life.total_seconds()

                if add_ds_data:
                    update_req.sec_dns.add_ds_data.data.extend(list(map(lambda d: d.to_pb(), add_ds_data)))
                if rem_ds_data:
                    update_req.sec_dns.remove_ds_data.data.extend(list(map(lambda d: d.to_pb(), rem_ds_data)))
                if add_key_data:
                    update_req.sec_dns.add_key_data.data.extend(list(map(lambda d: d.to_pb(), add_key_data)))
                if rem_key_data:
                    update_req.sec_dns.remove_key_data.data.extend(list(map(lambda d: d.to_pb(), rem_key_data)))

                instance.sec_dns = new_sec_dns

        if 'block_transfer' in validated_data:
            if domain_info.transfer_lock_supported:
                if apps.epp_api.domain_pb2.ClientTransferProhibited in instance.domain_obj.statuses \
                        and not validated_data['block_transfer']:
                    update_req.remove.append(
                        apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                            state=apps.epp_api.domain_pb2.ClientTransferProhibited
                        )
                    )
                    instance.statuses.remove("client_transfer_prohibited")
                elif apps.epp_api.domain_pb2.ClientTransferProhibited not in instance.domain_obj.statuses \
                        and validated_data['block_transfer']:
                    update_req.add.append(
                        apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                            state=apps.epp_api.domain_pb2.ClientTransferProhibited
                        )
                    )
                    instance.statuses.append("client_transfer_prohibited")

        if 'regen_auth_code' in validated_data:
            if validated_data['regen_auth_code']:
                new_auth_info = models.make_secret()
                update_req.new_auth_info.value = new_auth_info
                instance.auth_info = new_auth_info
                instance.domain_db_obj.auth_info = new_auth_info

        if update_req.add or update_req.remove or update_req.HasField('new_registrant') \
                or update_req.HasField('new_auth_info') or update_req.HasField("sec_dns"):
            apps.epp_client.stub.DomainUpdate(update_req)

        instance.domain_db_obj.save()
        return instance


class DomainCreateSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(view_name='domain-detail', lookup_field='id', lookup_url_kwarg='pk')
    id = serializers.UUIDField(read_only=True)
    domain = serializers.CharField(max_length=255)
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
    name_servers = serializers.ListField(
        child=DomainNameServerSerializer()
    )
    auth_info = serializers.CharField(max_length=255, read_only=True)
    sec_dns = DomainSecDNSSerializer(allow_null=True)
    period = DomainPeriodSerializer(write_only=True)
    pending = serializers.BooleanField(read_only=True)
    created = serializers.DateTimeField(read_only=True, allow_null=True)
    expiry = serializers.DateTimeField(read_only=True, allow_null=True)

    def validate(self, data):
        errs = {}

        for k in ('registrant', 'admin_contact', 'billing_contact', 'tech_contact'):
            if data.get(k):
                if not data[k].has_scope(self.context['request'].auth.token, 'view'):
                    errs[k] = "you don't have permission to reference this object"

        if errs:
            raise serializers.ValidationError(errs)
        return data

    def create(self, validated_data):
        domain = validated_data['domain']
        domain_info, sld = zone_info.get_domain_info(domain)

        if not domain_info:
            raise PermissionDenied

        available, _, registry_id = apps.epp_client.check_domain(domain)

        if not available:
            raise ObjectExists()

        zone_price, registry_name = domain_info.pricing, domain_info.registry

        auth_info = models.make_secret()
        registrant = validated_data['registrant']
        admin_contact = validated_data['admin_contact']
        billing_contact = validated_data['billing_contact']
        tech_contact = validated_data['tech_contact']
        period = validated_data['period']
        name_servers = list(map(
            lambda n: DomainNameServer(**{"host_object": None, "host_name": None, "addresses": None, **n}),
            validated_data['name_servers']
        ))
        sec_dns = validated_data['sec_dns']
        domain_id = uuid.uuid4()

        if not name_servers:
            name_servers = [
                DomainNameServer(host_object='ns1.as207960.net', host_name=None, addresses=None),
                DomainNameServer(host_object='ns2.as207960.net', host_name=None, addresses=None),
            ]

        period_obj = apps.epp_api.Period(
            unit=apps.epp_api.common_pb2.Period.Unit.Years if period['unit'] == "y"
            else apps.epp_api.common_pb2.Period.Unit.Months if period['unit'] == "m" else None,
            value=period['value']
        )

        domain_db_obj = models.DomainRegistration(
            id=domain_id,
            domain=domain,
            registrant_contact=registrant,
            admin_contact=admin_contact,
            tech_contact=tech_contact,
            billing_contact=billing_contact,
            auth_info=auth_info,
            user=self.context['request'].user
        )

        create_req = apps.epp_api.domain_pb2.DomainCreateRequest(
            name=domain,
            period=period_obj.to_pb(),
        )

        for ns in name_servers:
            if ns.host_object:
                host_available, _ = apps.epp_client.check_host(ns.host_object, registry_id)
                if host_available:
                    apps.epp_client.create_host(ns.host_object, [], registry_id)
                create_req.nameservers.append(apps.epp_api.domain_pb2.NameServer(
                    host_obj=ns.host_object
                ))
            elif ns.host_name:
                create_req.nameservers.append(apps.epp_api.domain_pb2.NameServer(
                    host_name=ns.host_name,
                    addresses=NameServerSerializer.map_addrs(ns.addresses)
                ))

        if sec_dns:
            if sec_dns['max_sig_life']:
                create_req.sec_dns.max_sig_life.value = sec_dns['max_sig_life'].total_seconds()
            if sec_dns['ds_data']:
                create_req.sec_dns.ds_data.data.extend(list(map(
                    lambda k: apps.epp_api.SecDNSDSData(
                        key_tag=k['key_tag'],
                        algorithm=k['algorithm'],
                        digest_type=k['digest_type'],
                        digest=k['digest'],
                        key_data=apps.epp_api.SecDNSKeyData(
                            **k['key_data']
                        ) if 'key_data' in k and k['key_data'] else None
                    ).to_pb(),
                    sec_dns['ds_data']
                )))
            if sec_dns['key_data']:
                create_req.sec_dns.key_data.data.extend(list(map(
                    lambda k: apps.epp_api.SecDNSKeyData(**k).to_pb(),
                    sec_dns['key_data']
                )))

        billing_value = zone_price.registration(sld, unit=period_obj.unit, value=period_obj.value)
        if billing_value is None:
            raise PermissionDenied
        charge_state = billing.charge_account(
            self.context['request'].user.username,
            billing_value,
            f"{domain} domain registration",
            f"dm_{domain_id}"
        )
        if not charge_state.success:
            raise BillingError(detail=charge_state.error)

        if domain_info.direct_registration_supported:
            try:
                if domain_info.registrant_supported:
                    create_req.registrant = registrant.get_registry_id(registry_id).registry_contact_id
                if domain_info.admin_supported and admin_contact:
                    create_req.contacts.append(apps.epp_api.domain_pb2.Contact(
                        type="admin",
                        id=admin_contact.get_registry_id(registry_id).registry_contact_id
                    ))
                if domain_info.billing_supported and billing_contact:
                    create_req.contacts.append(apps.epp_api.domain_pb2.Contact(
                        type="billing",
                        id=billing_contact.get_registry_id(registry_id).registry_contact_id
                    ))
                if domain_info.tech_supported and tech_contact:
                    create_req.contacts.append(apps.epp_api.domain_pb2.Contact(
                        type="tech",
                        id=tech_contact.get_registry_id(registry_id).registry_contact_id
                    ))

                resp = apps.epp_client.stub.DomainCreate(create_req)
            except grpc.RpcError as rpc_error:
                billing.reverse_charge(f"dm_{domain_id}")
                raise rpc_error
            domain_db_obj.pending = resp.pending
            domain_db_obj.save()
            gchat_bot.notify_registration(domain_db_obj, registry_id, period)
        else:
            resp = None
            domain_db_obj.pending = True
            domain_db_obj.save()
            gchat_bot.request_registration(domain_db_obj, registry_id, period)

        return DomainCreate(
            id=str(domain_id),
            domain=domain,
            registrant=domain_db_obj.registrant_contact,
            admin_contact=domain_db_obj.admin_contact,
            billing_contact=domain_db_obj.billing_contact,
            tech_contact=domain_db_obj.tech_contact,
            name_servers=name_servers,
            auth_info=auth_info,
            sec_dns=sec_dns,
            pending=domain_db_obj.pending,
            created=resp.creation_date.ToDatetime() if resp and resp.HasField("creation_date") else None,
            expiry=resp.expiry_date.ToDatetime() if resp and resp.HasField("expiry_date") else None,
        )


class DomainRenewSerializer(serializers.Serializer):
    period = DomainPeriodSerializer(write_only=True)


class DomainCheckSerializer(serializers.Serializer):
    domain = serializers.CharField(max_length=255)
    period = DomainPeriodSerializer(write_only=True)
    available = serializers.BooleanField(read_only=True)
    reason = serializers.CharField(read_only=True, allow_null=True)
    price = serializers.DecimalField(max_digits=9, decimal_places=2, read_only=True, allow_null=True)


class DomainCheckRenewSerializer(serializers.Serializer):
    domain = serializers.CharField(max_length=255, read_only=True)
    period = DomainPeriodSerializer(write_only=True)
    available = serializers.BooleanField(read_only=True)
    reason = serializers.CharField(read_only=True, allow_null=True)
    price = serializers.DecimalField(max_digits=9, decimal_places=2, read_only=True, allow_null=True)


class DomainCheckRestoreSerializer(serializers.Serializer):
    domain = serializers.CharField(max_length=255, read_only=True)
    available = serializers.BooleanField(read_only=True)
    reason = serializers.CharField(read_only=True, allow_null=True)
    price = serializers.DecimalField(max_digits=9, decimal_places=2, read_only=True, allow_null=True)
