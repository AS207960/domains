import dataclasses
import collections
import datetime
import decimal
import ipaddress
import typing

from django.utils import timezone
from django.core.exceptions import PermissionDenied
from rest_framework import exceptions, serializers
from rest_framework.settings import api_settings

from .. import apps, models, zone_info, tasks


class PermissionPrimaryKeyRelatedFieldValidator:
    requires_context = True

    def __call__(self, value, ctx):
        if not value.has_scope(ctx.auth_token, 'view'):
            raise serializers.ValidationError("you don't have permission to reference this object")


class PermissionPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, model, **kwargs):
        self.model = model
        self.auth_token = None
        super().__init__(queryset=model.objects.all(), **kwargs)

    def get_choices(self, cutoff=None):
        if self.auth_token:
            queryset = self.model.get_object_list(self.auth_token)
        else:
            queryset = self.get_queryset()

        if queryset is None:
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return collections.OrderedDict([
            (
                self.to_representation(item),
                self.display_value(item)
            )
            for item in queryset
        ])

    def get_validators(self):
        validators = super().get_validators()
        validators.append(PermissionPrimaryKeyRelatedFieldValidator())
        return validators


class WriteOnceMixin:
    def get_fields(self):
        fields = super().get_fields()

        if 'update' in getattr(self.context.get('view'), 'action', ''):
            self._set_write_once_fields(fields)
            self._set_write_after_fields(fields)

        return fields

    def _set_write_once_fields(self, fields):
        write_once_fields = getattr(self.Meta, 'write_once_fields', None)
        if not write_once_fields:
            return

        if not isinstance(write_once_fields, (list, tuple)):
            raise TypeError(
                'The `write_once_fields` option must be a list or tuple. '
                'Got {}.'.format(type(write_once_fields).__name__)
            )

        for field_name in write_once_fields:
            fields[field_name].read_only = True

    def _set_write_after_fields(self, fields):
        write_after_fields = getattr(self.Meta, 'write_after_fields', None)
        if not write_after_fields:
            return

        if not isinstance(write_after_fields, (list, tuple)):
            raise TypeError(
                'The `write_after_fields` option must be a list or tuple. '
                'Got {}.'.format(type(write_after_fields).__name__)
            )

        for field_name in write_after_fields:
            fields[field_name].read_only = False


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
    local_address = PermissionPrimaryKeyRelatedField(model=models.Contact)
    local_address_url = serializers.HyperlinkedRelatedField(
        view_name='contactaddress-detail', source='local_address', read_only=True,
    )
    int_address = PermissionPrimaryKeyRelatedField(model=models.Contact)
    int_address_url = serializers.HyperlinkedRelatedField(
        view_name='contactaddress-detail', source='int_address', read_only=True,
    )
    entity_type = serializers.ChoiceField(choices=(
        ("not_set", "Not set"),
        ("unknown_entity", "Unknown entity"),
        ("uk_limited_company", "UK Limited Company"),
        ("uk_public_limited_company", "UK Public Limited Company"),
        ("uk_partnership", "UK Partnership"),
        ("uk_sole_trader", "UK Sole Trader"),
        ("uk_limited_liability_partnership", "UK Limited Liability Partnership"),
        ("uk_industrial_provident_registered_company", "UK Industrial Provident Registered Company"),
        ("uk_individual", "UK Individual"),
        ("uk_school", "UK School"),
        ("uk_registered_charity", "UK Registered Charity"),
        ("uk_government_body", "UK Government Body"),
        ("uk_corporation_by_royal_charter", "UK Corporation by Royal Charter"),
        ("uk_statutory_body", "UK Statutory Body"),
        ("uk_political_party", "UK Political party"),
        ("other_uk_entity", "Other UK Entity"),
        ("finnish_individual", "Finnish Individual"),
        ("finnish_company", "Finnish Company"),
        ("finnish_association", "Finnish Association"),
        ("finnish_institution", "Finnish Institution"),
        ("finnish_political_party", "Finnish Political Party"),
        ("finnish_municipality", "Finnish Municipality"),
        ("finnish_government", "Finnish Government"),
        ("finnish_public_community", "Finnish Public Community"),
        ("other_individual", "Other Individual"),
        ("other_company", "Other Company"),
        ("other_association", "Other Association"),
        ("other_institution", "Other Institution"),
        ("other_political_party", "Other Political Party"),
        ("other_municipality", "Other Municipality"),
        ("other_government", "Other Government"),
        ("other_public_community", "Other Public Community"),
    ), read_only=True)

    class Meta:
        model = models.Contact
        fields = ('url', 'id', 'description', 'local_address', 'local_address_url', 'int_address', 'int_address_url',
                  'phone', 'phone_ext', 'fax', 'fax_ext', 'email', 'entity_type', 'trading_name', 'company_number',
                  'disclose_phone', 'disclose_fax', 'disclose_email')
        read_only_fields = ('created_date', 'updated_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["local_address"].auth_token = self.context['request'].auth.token
        self.fields["int_address"].auth_token = self.context['request'].auth.token

    def to_representation(self, instance: models.Contact):
        ret = super().to_representation(instance)

        if instance.entity_type == 0:
            ret["entity_type"] = "not_set"
        elif instance.entity_type == 1:
            ret["entity_type"] = "unknown_entity"
        elif instance.entity_type == 2:
            ret["entity_type"] = "uk_limited_company"
        elif instance.entity_type == 3:
            ret["entity_type"] = "uk_public_limited_company"
        elif instance.entity_type == 4:
            ret["entity_type"] = "uk_partnership"
        elif instance.entity_type == 5:
            ret["entity_type"] = "uk_sole_trader"
        elif instance.entity_type == 6:
            ret["entity_type"] = "uk_limited_liability_partnership"
        elif instance.entity_type == 7:
            ret["entity_type"] = "uk_industrial_provident_registered_company"
        elif instance.entity_type == 8:
            ret["entity_type"] = "uk_individual"
        elif instance.entity_type == 9:
            ret["entity_type"] = "uk_school"
        elif instance.entity_type == 10:
            ret["entity_type"] = "uk_registered_charity"
        elif instance.entity_type == 11:
            ret["entity_type"] = "uk_government_body"
        elif instance.entity_type == 12:
            ret["entity_type"] = "uk_corporation_by_royal_charter"
        elif instance.entity_type == 13:
            ret["entity_type"] = "uk_statutory_body"
        elif instance.entity_type == 31:
            ret["entity_type"] = "uk_political_party"
        elif instance.entity_type == 14:
            ret["entity_type"] = "other_uk_entity"
        elif instance.entity_type == 15:
            ret["entity_type"] = "finnish_individual"
        elif instance.entity_type == 16:
            ret["entity_type"] = "finnish_company"
        elif instance.entity_type == 17:
            ret["entity_type"] = "finnish_association"
        elif instance.entity_type == 18:
            ret["entity_type"] = "finnish_institution"
        elif instance.entity_type == 19:
            ret["entity_type"] = "finnish_political_party"
        elif instance.entity_type == 20:
            ret["entity_type"] = "finnish_municipality"
        elif instance.entity_type == 21:
            ret["entity_type"] = "finnish_government"
        elif instance.entity_type == 22:
            ret["entity_type"] = "finnish_public_community"
        elif instance.entity_type == 23:
            ret["entity_type"] = "other_individual"
        elif instance.entity_type == 24:
            ret["entity_type"] = "other_company"
        elif instance.entity_type == 25:
            ret["entity_type"] = "other_association"
        elif instance.entity_type == 26:
            ret["entity_type"] = "other_institution"
        elif instance.entity_type == 27:
            ret["entity_type"] = "other_political_party"
        elif instance.entity_type == 28:
            ret["entity_type"] = "other_municipality"
        elif instance.entity_type == 29:
            ret["entity_type"] = "other_government"
        elif instance.entity_type == 30:
            ret["entity_type"] = "other_public_community"
        else:
            ret["entity_typ"] = "unknown"

        return ret

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)

        if "entity_type" in ret:
            if ret["entity_type"] == "not_set":
                ret["entity_type"] = 0
            elif ret["entity_type"] == "unknown_entity":
                ret["entity_type"] = 1
            elif ret["entity_type"] == "uk_limited_company":
                ret["entity_type"] = 2
            elif ret["entity_type"] == "uk_public_limited_company":
                ret["entity_type"] = 3
            elif ret["entity_type"] == "uk_partnership":
                ret["entity_type"] = 4
            elif ret["entity_type"] == "uk_sole_trader":
                ret["entity_type"] = 5
            elif ret["entity_type"] == "uk_limited_liability_partnership":
                ret["entity_type"] = 6
            elif ret["entity_type"] == "uk_industrial_provident_registered_company":
                ret["entity_type"] = 7
            elif ret["entity_type"] == "uk_individual":
                ret["entity_type"] = 8
            elif ret["entity_type"] == "uk_school":
                ret["entity_type"] = 9
            elif ret["entity_type"] == "uk_registered_charity":
                ret["entity_type"] = 10
            elif ret["entity_type"] == "uk_government_body":
                ret["entity_type"] = 11
            elif ret["entity_type"] == "uk_corporation_by_royal_charter":
                ret["entity_type"] = 12
            elif ret["entity_type"] == "uk_statutory_body":
                ret["entity_type"] = 13
            elif ret["entity_type"] == "uk_political_party":
                ret["entity_type"] = 31
            elif ret["entity_type"] == "other_uk_entity":
                ret["entity_type"] = 14
            elif ret["entity_type"] == "finnish_individual":
                ret["entity_type"] = 15
            elif ret["entity_type"] == "finnish_company":
                ret["entity_type"] = 16
            elif ret["entity_type"] == "finnish_association":
                ret["entity_type"] = 17
            elif ret["entity_type"] == "finnish_institution":
                ret["entity_type"] = 18
            elif ret["entity_type"] == "finnish_political_party":
                ret["entity_type"] = 19
            elif ret["entity_type"] == "finnish_municipality":
                ret["entity_type"] = 20
            elif ret["entity_type"] == "finnish_government":
                ret["entity_type"] = 21
            elif ret["entity_type"] == "finnish_public_community":
                ret["entity_type"] = 22
            elif ret["entity_type"] == "other_individual":
                ret["entity_type"] = 23
            elif ret["entity_type"] == "other_company":
                ret["entity_type"] = 24
            elif ret["entity_type"] == "other_association":
                ret["entity_type"] = 25
            elif ret["entity_type"] == "other_institution":
                ret["entity_type"] = 26
            elif ret["entity_type"] == "other_political_party":
                ret["entity_type"] = 27
            elif ret["entity_type"] == "other_municipality":
                ret["entity_type"] = 28
            elif ret["entity_type"] == "other_government":
                ret["entity_type"] = 29
            elif ret["entity_type"] == "other_public_community":
                ret["entity_type"] = 30

        return ret


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
    id = serializers.CharField(read_only=True)
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

        domain_data = apps.epp_client.get_domain(
            domain.domain, registry_id=domain.registry_id
        )
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
    id = serializers.CharField(read_only=True)
    domain = serializers.CharField(max_length=255, read_only=True)
    statuses = serializers.ListField(
        child=serializers.CharField(read_only=True),
        read_only=True
    )
    deleted = serializers.BooleanField(read_only=True)
    registrant = PermissionPrimaryKeyRelatedField(model=models.Contact)
    registrant_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='registrant', read_only=True,
    )
    admin_contact = PermissionPrimaryKeyRelatedField(model=models.Contact, allow_null=True)
    admin_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='admin_contact', allow_null=True, read_only=True
    )
    billing_contact = PermissionPrimaryKeyRelatedField(model=models.Contact, allow_null=True)
    billing_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='billing_contact', allow_null=True, read_only=True
    )
    tech_contact = PermissionPrimaryKeyRelatedField(model=models.Contact, allow_null=True)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["registrant"].auth_token = self.context['request'].auth.token
        self.fields["admin_contact"].auth_token = self.context['request'].auth.token
        self.fields["billing_contact"].auth_token = self.context['request'].auth.token
        self.fields["tech_contact"].auth_token = self.context['request'].auth.token

    @classmethod
    def get_domain(cls, d: models.DomainRegistration, domain: apps.epp_api.Domain, user):
        registrant = d.registrant_contact
        if d.admin_contact:
            admin = d.admin_contact
        else:
            admin = None
        if d.billing_contact:
            billing = d.billing_contact
        else:
            billing = None
        if d.tech_contact:
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

        if apps.epp_api.rgp_pb2.RedemptionPeriod in domain.rgp_state:
            d.deleted = True
            d.deleted_date = timezone.now()
            d.save()

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
        domain_info = zone_info.get_domain_info(instance.domain, registry_id=instance.registry_id)[0]  # type: zone_info.DomainInfo
        update_req = apps.epp_api.domain_pb2.DomainUpdateRequest(
            name=instance.domain,
            remove=[],
            add=[]
        )

        if 'registrant' in validated_data and validated_data['registrant'] != instance.registrant \
                and domain_info.registrant_change_supported:
            instance.registrant = validated_data['registrant']
            if domain_info.registrant_supported:
                proxy_contact = domain_info.registrant_proxy(instance.registrant)
                if proxy_contact:
                    update_req.new_registrant.value = proxy_contact
                else:
                    update_req.new_registrant.value = instance.registrant.get_registry_id(
                        instance.domain_obj.registry_name, domain_info, role=apps.epp_api.ContactRole.Registrant
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
                                instance.domain_obj.registry_name, domain_info,
                                role=apps.epp_api.ContactRole.Admin
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
                                instance.domain_obj.registry_name, domain_info,
                                role=apps.epp_api.ContactRole.Billing
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
                if domain_info.is_eurid:
                    old_contact = instance.domain_obj.eurid.on_site if instance.domain_obj.eurid else None
                    if old_contact:
                        update_req.eurid_data.remove_on_site.value = old_contact

                    update_req.eurid_data.add_on_site.value = instance.tech_contact.get_registry_id(
                        instance.domain_obj.registry_name, domain_info,
                        role=apps.epp_api.ContactRole.OnSite
                    ).registry_contact_id

                else:
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
                                    instance.domain_obj.registry_name, domain_info,
                                    role=apps.epp_api.ContactRole.Tech
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
                    if domain_info.pre_create_host_objects:
                        host_available, _ = apps.epp_client.check_host(ns.host_object, instance.domain_obj.registry_name)
                        if host_available:
                            if domain_info.registry == domain_info.REGISTRY_ISNIC:
                                if instance.domain_db_obj.tech_contact:
                                    zone_contact = instance.domain_db_obj.tech_contact
                                else:
                                    zone_contact = instance.domain_db_obj.registrant_contact

                                isnic_zone_contact = zone_contact.get_registry_id(
                                    instance.domain_obj.registry_name, domain_info, role=apps.epp_api.ContactRole.Tech
                                )
                            else:
                                isnic_zone_contact = None

                            apps.epp_client.create_host(ns.host_object, [], instance.domain_obj.registry_name, isnic_zone_contact.registry_contact_id)
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
                    update_req.sec_dns.rem_ds_data.data.extend(list(map(lambda d: d.to_pb(), rem_ds_data)))
                if add_key_data:
                    update_req.sec_dns.add_key_data.data.extend(list(map(lambda d: d.to_pb(), add_key_data)))
                if rem_key_data:
                    update_req.sec_dns.rem_key_data.data.extend(list(map(lambda d: d.to_pb(), rem_key_data)))

                instance.sec_dns = new_sec_dns

        if 'block_transfer' in validated_data:
            if domain_info.transfer_lock_supported:
                if apps.epp_api.domain_common_pb2.ClientTransferProhibited in instance.domain_obj.statuses \
                        and not validated_data['block_transfer']:
                    update_req.remove.append(
                        apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                            state=apps.epp_api.domain_common_pb2.ClientTransferProhibited
                        )
                    )
                    instance.statuses.remove("client_transfer_prohibited")
                elif apps.epp_api.domain_common_pb2.ClientTransferProhibited not in instance.domain_obj.statuses \
                        and validated_data['block_transfer']:
                    update_req.add.append(
                        apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                            state=apps.epp_api.domain_common_pb2.ClientTransferProhibited
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


class BaseOrderSerializer(WriteOnceMixin, serializers.ModelSerializer):
    state = serializers.ChoiceField(choices=(
        ("pending", "Pending"),
        ("started", "Started"),
        ("processing", "Processing"),
        ("needs_payment", "Needs payment"),
        ("pending_approval", "Pending approval"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ), read_only=True)

    def to_representation(self, instance: models.AbstractOrder):
        ret = {
            "url": self.fields["url"].to_representation(instance),
            "id": self.fields["id"].to_representation(instance),
            "redirect_uri": self.fields["redirect_uri"].to_representation(instance)
            if instance.redirect_uri else None,
            "last_error": self.fields["last_error"].to_representation(instance)
            if instance.last_error else None,
            "off_session": instance.off_session,
            "price": instance.price
        }

        if instance.state == models.AbstractOrder.STATE_STARTED:
            ret["state"] = "started"
        elif instance.state == models.AbstractOrder.STATE_PROCESSING:
            ret["state"] = "processing"
        elif instance.state == models.AbstractOrder.STATE_NEEDS_PAYMENT:
            ret["state"] = "needs_payment"
        elif instance.state == models.AbstractOrder.STATE_PENDING_APPROVAL:
            ret["state"] = "pending_approval"
        elif instance.state == models.AbstractOrder.STATE_COMPLETED:
            ret["state"] = "completed"
        elif instance.state == models.AbstractOrder.STATE_FAILED:
            ret["state"] = "failed"
        else:
            ret["state"] = "unknown"

        return ret

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)

        if "state" in ret:
            if ret["state"] == "started":
                ret["state"] = models.AbstractOrder.STATE_STARTED
            elif ret["state"] == "processing":
                ret["state"] = models.AbstractOrder.STATE_PROCESSING
            elif ret["state"] == "needs_payment":
                ret["state"] = models.AbstractOrder.STATE_NEEDS_PAYMENT
            elif ret["state"] == "pending_approval":
                ret["state"] = models.AbstractOrder.STATE_PENDING_APPROVAL
            elif ret["state"] == "completed":
                ret["state"] = models.AbstractOrder.STATE_COMPLETED
            elif ret["state"] == "failed":
                ret["state"] = models.AbstractOrder.STATE_FAILED

        return ret

    def update(self, instance, validated_data):
        if instance.state != models.DomainRegistrationOrder.STATE_PENDING:
            raise serializers.ValidationError({
                "state": ["invalid state transition"]
            })
        else:
            if validated_data["state"] not in (
                    models.DomainRegistrationOrder.STATE_STARTED, models.DomainRegistrationOrder.STATE_FAILED
            ):
                raise serializers.ValidationError({
                    "state": ["invalid state transition"]
                })

            instance.state = validated_data["state"]
            instance.save()

        return instance


class DomainRegistrationOrderSerializer(BaseOrderSerializer):
    period = DomainPeriodSerializer()
    registrant = PermissionPrimaryKeyRelatedField(model=models.Contact, source='registrant_contact')
    registrant_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='registrant_contact', read_only=True,
    )
    admin_contact = PermissionPrimaryKeyRelatedField(model=models.Contact, allow_null=True)
    admin_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='admin_contact', allow_null=True, read_only=True
    )
    billing_contact = PermissionPrimaryKeyRelatedField(model=models.Contact, allow_null=True)
    billing_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='billing_contact', allow_null=True, read_only=True
    )
    tech_contact = PermissionPrimaryKeyRelatedField(model=models.Contact, allow_null=True)
    tech_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='tech_contact', allow_null=True, read_only=True
    )
    domain_obj = serializers.PrimaryKeyRelatedField(
        allow_null=True, read_only=True
    )
    domain_obj_url = serializers.HyperlinkedRelatedField(
        view_name='domain-detail', source='domain_obj', allow_null=True, read_only=True
    )

    class Meta:
        model = models.DomainRegistrationOrder
        fields = ('url', 'id', 'state', 'domain', 'domain_id', 'registrant', 'registrant_url',
                  'admin_contact', 'admin_contact_url', 'billing_contact', 'billing_contact_url',
                  'tech_contact', 'tech_contact_url', 'domain_obj', 'domain_obj_url', 'redirect_uri',
                  'last_error', 'period', 'price', 'off_session')
        read_only_fields = ('domain_id', 'redirect_uri', 'last_error', 'price', 'domain_obj')
        write_once_fields = ('domain', 'registrant', 'admin_contact', 'billing_contact', 'tech_contact', 'period',
                             'off_session',)
        write_after_fields = ('state',)
        extra_kwargs = {'off_session': {'default': True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["registrant"].auth_token = self.context['request'].auth.token
        self.fields["admin_contact"].auth_token = self.context['request'].auth.token
        self.fields["billing_contact"].auth_token = self.context['request'].auth.token
        self.fields["tech_contact"].auth_token = self.context['request'].auth.token

    def to_representation(self, instance: models.DomainRegistrationOrder):
        ret = super().to_representation(instance)

        ret = dict(**ret, **{
            "domain": self.fields["domain"].to_representation(instance),
            "domain_id": self.fields["domain_id"].to_representation(instance),
            "domain_obj": self.fields["domain_obj"].to_representation(instance)
            if instance.domain_obj else None,
            "domain_obj_url": self.fields["domain_obj_url"].to_representation(instance)
            if instance.domain_obj else None,
            "registrant": self.fields["registrant"].to_representation(instance.registrant_contact),
            "registrant_url": self.fields["registrant_url"].to_representation(instance.registrant_contact),
            "admin_contact": self.fields["admin_contact"].to_representation(instance.admin_contact)
            if instance.admin_contact is not None else None,
            "admin_contact_url": self.fields["admin_contact_url"].to_representation(instance.admin_contact)
            if instance.admin_contact is not None else None,
            "billing_contact": self.fields["billing_contact"].to_representation(instance.billing_contact)
            if instance.billing_contact is not None else None,
            "billing_contact_url": self.fields["billing_contact_url"].to_representation(instance.billing_contact)
            if instance.billing_contact is not None else None,
            "tech_contact": self.fields["tech_contact"].to_representation(instance.tech_contact)
            if instance.tech_contact is not None else None,
            "tech_contact_url": self.fields["tech_contact_url"].to_representation(instance.tech_contact)
            if instance.tech_contact is not None else None,
            "period": {
                "unit": "y" if instance.period_unit == apps.epp_api.common_pb2.Period.Unit.Years
                else "m" if instance.period_unit == apps.epp_api.common_pb2.Period.Unit.Months else "unknown",
                "value": instance.period_value,
            },
        })

        return ret

    def create(self, validated_data):
        zone, sld = zone_info.get_domain_info(validated_data["domain"])

        if zone.admin_required and not validated_data['admin_contact']:
            raise serializers.ValidationError({
                "admin_contact": "Required for this registry"
            })
        if zone.billing_required and not validated_data['billing_contact']:
            raise serializers.ValidationError({
                "billing_contact": "Required for this registry"
            })
        if zone.tech_required and not validated_data['tech_contact']:
            raise serializers.ValidationError({
                "tech_contact": "Required for this registry"
            })

        if not zone:
            raise PermissionDenied

        zone_price, registry_name = zone.pricing, zone.registry
        period = apps.epp_api.Period(
            unit=apps.epp_api.common_pb2.Period.Unit.Years if validated_data['period']['unit'] == "y"
            else apps.epp_api.common_pb2.Period.Unit.Months if validated_data['period']['unit'] == "m" else None,
            value=validated_data['period']['value']
        )

        billing_value = zone_price.registration(
            "GB", self.context['request'].user.username, sld, unit=period.unit, value=period.value
        ).amount
        if billing_value is None:
            raise PermissionDenied

        order = models.DomainRegistrationOrder(
            domain=validated_data["domain"],
            period_unit=period.unit,
            period_value=period.value,
            registrant_contact=validated_data['registrant_contact'],
            admin_contact=validated_data['admin_contact'],
            billing_contact=validated_data['billing_contact'],
            tech_contact=validated_data['tech_contact'],
            user=self.context['request'].user,
            price=billing_value,
            auth_info=models.make_secret(),
            off_session=validated_data["off_session"]
        )
        order.save()
        tasks.process_domain_registration.delay(order.id)
        return order


class DomainTransferOrderSerializer(BaseOrderSerializer):
    registrant = PermissionPrimaryKeyRelatedField(model=models.Contact, source='registrant_contact')
    registrant_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='registrant_contact', read_only=True,
    )
    admin_contact = PermissionPrimaryKeyRelatedField(model=models.Contact, allow_null=True)
    admin_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='admin_contact', allow_null=True, read_only=True
    )
    billing_contact = PermissionPrimaryKeyRelatedField(model=models.Contact, allow_null=True)
    billing_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='billing_contact', allow_null=True, read_only=True
    )
    tech_contact = PermissionPrimaryKeyRelatedField(model=models.Contact, allow_null=True)
    tech_contact_url = serializers.HyperlinkedRelatedField(
        view_name='contact-detail', source='tech_contact', allow_null=True, read_only=True
    )
    domain_obj = serializers.PrimaryKeyRelatedField(
        allow_null=True, read_only=True
    )
    domain_obj_url = serializers.HyperlinkedRelatedField(
        view_name='domain-detail', source='domain_obj', allow_null=True, read_only=True
    )

    class Meta:
        model = models.DomainTransferOrder
        fields = ('url', 'id', 'state', 'domain', 'domain_id', 'registrant', 'registrant_url',
                  'admin_contact', 'admin_contact_url', 'billing_contact', 'billing_contact_url',
                  'tech_contact', 'tech_contact_url', 'domain_obj', 'domain_obj_url', 'redirect_uri',
                  'last_error', 'auth_code', 'price', 'off_session')
        read_only_fields = ('domain_id', 'redirect_uri', 'last_error', 'price', 'domain_obj')
        write_once_fields = ('domain', 'registrant', 'admin_contact', 'billing_contact', 'tech_contact', 'auth_code',
                             'off_session',)
        write_after_fields = ('state',)
        extra_kwargs = {'off_session': {'default': True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["registrant"].auth_token = self.context['request'].auth.token
        self.fields["admin_contact"].auth_token = self.context['request'].auth.token
        self.fields["billing_contact"].auth_token = self.context['request'].auth.token
        self.fields["tech_contact"].auth_token = self.context['request'].auth.token

    def to_representation(self, instance: models.DomainTransferOrder):
        ret = super().to_representation(instance)

        ret = dict(**ret, **{
            "domain": self.fields["domain"].to_representation(instance.domain),
            "domain_id": self.fields["domain_id"].to_representation(instance.domain_id),
            "domain_obj": self.fields["domain_obj"].to_representation(instance.domain_obj)
            if instance.domain_obj else None,
            "domain_obj_url": self.fields["domain_obj_url"].to_representation(instance.domain_obj)
            if instance.domain_obj else None,
            "registrant": self.fields["registrant"].to_representation(instance.registrant_contact),
            "registrant_url": self.fields["registrant_url"].to_representation(instance.registrant_contact),
            "admin_contact": self.fields["admin_contact"].to_representation(instance.admin_contact)
            if instance.admin_contact is not None else None,
            "admin_contact_url": self.fields["admin_contact_url"].to_representation(instance.admin_contact)
            if instance.admin_contact is not None else None,
            "billing_contact": self.fields["billing_contact"].to_representation(instance.billing_contact)
            if instance.billing_contact is not None else None,
            "billing_contact_url": self.fields["billing_contact_url"].to_representation(instance.billing_contact)
            if instance.billing_contact is not None else None,
            "tech_contact": self.fields["tech_contact"].to_representation(instance.tech_contact)
            if instance.tech_contact is not None else None,
            "tech_contact_url": self.fields["tech_contact_url"].to_representation(instance.tech_contact)
            if instance.tech_contact is not None else None,
            "auth_code": self.fields["auth_code"].to_representation(instance.auth_code),
        })

        return ret

    def create(self, validated_data):
        zone, sld = zone_info.get_domain_info(validated_data["domain"])

        if zone.admin_required and not validated_data['admin_contact']:
            raise serializers.ValidationError({
                "admin_contact": "Required for this registry"
            })
        if zone.billing_required and not validated_data['billing_contact']:
            raise serializers.ValidationError({
                "billing_contact": "Required for this registry"
            })
        if zone.tech_required and not validated_data['tech_contact']:
            raise serializers.ValidationError({
                "tech_contact": "Required for this registry"
            })

        if not zone:
            raise PermissionDenied

        zone_price, registry_name = zone.pricing, zone.registry
        billing_value = zone_price.transfer(
            "GB", self.context['request'].user.username, sld
        ).amount
        if billing_value is None:
            raise PermissionDenied

        order = models.DomainTransferOrder(
            domain=validated_data["domain"],
            auth_code=validated_data['auth_code'],
            registrant_contact=validated_data['registrant_contact'],
            admin_contact=validated_data['admin_contact'],
            billing_contact=validated_data['billing_contact'],
            tech_contact=validated_data['tech_contact'],
            user=self.context['request'].user,
            price=billing_value,
            off_session=validated_data["off_session"]
        )
        order.save()
        tasks.process_domain_transfer.delay(order.id)
        return order


class DomainRenewOrderSerializer(BaseOrderSerializer):
    period = DomainPeriodSerializer()
    domain_obj = serializers.PrimaryKeyRelatedField(
        allow_null=True, read_only=True
    )
    domain_obj_url = serializers.HyperlinkedRelatedField(
        view_name='domain-detail', source='domain_obj', allow_null=True, read_only=True
    )

    class Meta:
        model = models.DomainRenewOrder
        fields = ('url', 'id', 'state', 'domain', 'domain_obj', 'domain_obj_url', 'redirect_uri',
                  'last_error', 'period', 'price', 'off_session')
        read_only_fields = ('domain', 'redirect_uri', 'last_error', 'price', 'domain_obj')
        write_once_fields = ('off_session', 'period',)
        write_after_fields = ('state',)
        extra_kwargs = {'off_session': {'default': True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, instance: models.DomainRenewOrder):
        ret = super().to_representation(instance)

        ret = dict(**ret, **{
            "domain": self.fields["domain"].to_representation(instance.domain),
            "domain_obj": self.fields["domain_obj"].to_representation(instance.domain_obj)
            if instance.domain_obj else None,
            "domain_obj_url": self.fields["domain_obj_url"].to_representation(instance.domain_obj)
            if instance.domain_obj else None,
            "period": {
                "unit": "y" if instance.period_unit == apps.epp_api.common_pb2.Period.Unit.Years
                else "m" if instance.period_unit == apps.epp_api.common_pb2.Period.Unit.Months else "unknown",
                "value": instance.period_value,
            },
        })

        return ret

    def create(self, validated_data):
        domain = validated_data["domain_obj"]
        zone, sld = zone_info.get_domain_info(domain.domain)

        if not zone:
            raise PermissionDenied

        zone_price, registry_name = zone.pricing, zone.registry
        period = apps.epp_api.Period(
            unit=apps.epp_api.common_pb2.Period.Unit.Years if validated_data['period']['unit'] == "y"
            else apps.epp_api.common_pb2.Period.Unit.Months if validated_data['period']['unit'] == "m" else None,
            value=validated_data['period']['value']
        )

        billing_value = zone_price.renewal(
            "GB", self.context['request'].user.username, sld, unit=period.unit, value=period.value
        ).amount
        if billing_value is None:
            raise PermissionDenied

        order = models.DomainRenewOrder(
            domain=domain.domain,
            domain_obj=domain,
            period_unit=period.unit,
            period_value=period.value,
            user=self.context['request'].user,
            price=billing_value,
            off_session=validated_data["off_session"]
        )
        order.save()
        tasks.process_domain_renewal.delay(order.id)
        return order


class DomainRestoreOrderSerializer(BaseOrderSerializer):
    domain_obj = serializers.PrimaryKeyRelatedField(
        allow_null=True, read_only=True
    )
    domain_obj_url = serializers.HyperlinkedRelatedField(
        view_name='domain-detail', source='domain_obj', allow_null=True, read_only=True
    )

    class Meta:
        model = models.DomainRestoreOrder
        fields = ('url', 'id', 'state', 'domain', 'domain_obj', 'domain_obj_url', 'redirect_uri',
                  'last_error', 'price', 'off_session')
        read_only_fields = ('domain', 'redirect_uri', 'last_error', 'price', 'domain_obj')
        write_once_fields = ('off_session',)
        write_after_fields = ('state',)
        extra_kwargs = {'off_session': {'default': True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, instance: models.DomainRestoreOrder):
        ret = super().to_representation(instance)

        ret = dict(**ret, **{
            "domain": self.fields["domain"].to_representation(instance.domain),
            "domain_obj": self.fields["domain_obj"].to_representation(instance.domain_obj)
            if instance.domain_obj else None,
            "domain_obj_url": self.fields["domain_obj_url"].to_representation(instance.domain_obj)
            if instance.domain_obj else None,
        })

        return ret

    def create(self, validated_data):
        domain = validated_data["domain_obj"]
        zone, sld = zone_info.get_domain_info(domain.domain)

        if not zone:
            raise PermissionDenied

        zone_price, registry_name = zone.pricing, zone.registry

        billing_value = zone_price.restore(
            "GB", self.context['request'].user.username, sld
        ).amount
        if billing_value is None:
            raise PermissionDenied

        order = models.DomainRestoreOrder(
            domain=domain.domain,
            domain_obj=domain,
            user=self.context['request'].user,
            price=billing_value,
            off_session=validated_data["off_session"]
        )
        order.save()
        tasks.process_domain_restore.delay(order.id)
        return order


class EPPBalanceSerializer(serializers.Serializer):
    balance = serializers.FloatField(read_only=True)
    credit_limit = serializers.FloatField(read_only=True, allow_null=True)
    available_credit = serializers.FloatField(read_only=True, allow_null=True)
    fixed_credit_threshold = serializers.FloatField(read_only=True, allow_null=True)
    percentage_credit_threshold = serializers.FloatField(read_only=True, allow_null=True)
    currency = serializers.CharField(read_only=True)


class UserDomainCheckSerializer(serializers.Serializer):
    domain = serializers.CharField(max_length=255)
    access = serializers.BooleanField(read_only=True)
    token = serializers.CharField(read_only=True)


class UserDomainChecksSerializer(serializers.Serializer):
    domains = serializers.ListField(child=UserDomainCheckSerializer())
