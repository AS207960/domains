"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import common.common_pb2
import contact.qualified_lawyer.qualified_lawyer_pb2
import eurid.eurid_pb2
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.timestamp_pb2
import google.protobuf.wrappers_pb2
import isnic.isnic_pb2
import keysys.keysys_pb2
import nominet_ext.nominet_ext_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _EntityType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _EntityTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_EntityType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    NotSet: _EntityType.ValueType  # 0
    UnknownEntity: _EntityType.ValueType  # 1
    UkLimitedCompany: _EntityType.ValueType  # 2
    UkPublicLimitedCompany: _EntityType.ValueType  # 3
    UkPartnership: _EntityType.ValueType  # 4
    UkSoleTrader: _EntityType.ValueType  # 5
    UkLimitedLiabilityPartnership: _EntityType.ValueType  # 6
    UkIndustrialProvidentRegisteredCompany: _EntityType.ValueType  # 7
    UkIndividual: _EntityType.ValueType  # 8
    UkSchool: _EntityType.ValueType  # 9
    UkRegisteredCharity: _EntityType.ValueType  # 10
    UkGovernmentBody: _EntityType.ValueType  # 11
    UkCorporationByRoyalCharter: _EntityType.ValueType  # 12
    UkStatutoryBody: _EntityType.ValueType  # 13
    UkPoliticalParty: _EntityType.ValueType  # 31
    OtherUkEntity: _EntityType.ValueType  # 14
    FinnishIndividual: _EntityType.ValueType  # 15
    FinnishCompany: _EntityType.ValueType  # 16
    FinnishAssociation: _EntityType.ValueType  # 17
    FinnishInstitution: _EntityType.ValueType  # 18
    FinnishPoliticalParty: _EntityType.ValueType  # 19
    FinnishMunicipality: _EntityType.ValueType  # 20
    FinnishGovernment: _EntityType.ValueType  # 21
    FinnishPublicCommunity: _EntityType.ValueType  # 22
    OtherIndividual: _EntityType.ValueType  # 23
    OtherCompany: _EntityType.ValueType  # 24
    OtherAssociation: _EntityType.ValueType  # 25
    OtherInstitution: _EntityType.ValueType  # 26
    OtherPoliticalParty: _EntityType.ValueType  # 27
    OtherMunicipality: _EntityType.ValueType  # 28
    OtherGovernment: _EntityType.ValueType  # 29
    OtherPublicCommunity: _EntityType.ValueType  # 30

class EntityType(_EntityType, metaclass=_EntityTypeEnumTypeWrapper): ...

NotSet: EntityType.ValueType  # 0
UnknownEntity: EntityType.ValueType  # 1
UkLimitedCompany: EntityType.ValueType  # 2
UkPublicLimitedCompany: EntityType.ValueType  # 3
UkPartnership: EntityType.ValueType  # 4
UkSoleTrader: EntityType.ValueType  # 5
UkLimitedLiabilityPartnership: EntityType.ValueType  # 6
UkIndustrialProvidentRegisteredCompany: EntityType.ValueType  # 7
UkIndividual: EntityType.ValueType  # 8
UkSchool: EntityType.ValueType  # 9
UkRegisteredCharity: EntityType.ValueType  # 10
UkGovernmentBody: EntityType.ValueType  # 11
UkCorporationByRoyalCharter: EntityType.ValueType  # 12
UkStatutoryBody: EntityType.ValueType  # 13
UkPoliticalParty: EntityType.ValueType  # 31
OtherUkEntity: EntityType.ValueType  # 14
FinnishIndividual: EntityType.ValueType  # 15
FinnishCompany: EntityType.ValueType  # 16
FinnishAssociation: EntityType.ValueType  # 17
FinnishInstitution: EntityType.ValueType  # 18
FinnishPoliticalParty: EntityType.ValueType  # 19
FinnishMunicipality: EntityType.ValueType  # 20
FinnishGovernment: EntityType.ValueType  # 21
FinnishPublicCommunity: EntityType.ValueType  # 22
OtherIndividual: EntityType.ValueType  # 23
OtherCompany: EntityType.ValueType  # 24
OtherAssociation: EntityType.ValueType  # 25
OtherInstitution: EntityType.ValueType  # 26
OtherPoliticalParty: EntityType.ValueType  # 27
OtherMunicipality: EntityType.ValueType  # 28
OtherGovernment: EntityType.ValueType  # 29
OtherPublicCommunity: EntityType.ValueType  # 30
global___EntityType = EntityType

class _DisclosureType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _DisclosureTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_DisclosureType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    LocalName: _DisclosureType.ValueType  # 0
    InternationalisedName: _DisclosureType.ValueType  # 1
    LocalOrganisation: _DisclosureType.ValueType  # 2
    InternationalisedOrganisation: _DisclosureType.ValueType  # 3
    LocalAddress: _DisclosureType.ValueType  # 4
    InternationalisedAddress: _DisclosureType.ValueType  # 5
    Voice: _DisclosureType.ValueType  # 6
    Fax: _DisclosureType.ValueType  # 7
    Email: _DisclosureType.ValueType  # 8

class DisclosureType(_DisclosureType, metaclass=_DisclosureTypeEnumTypeWrapper): ...

LocalName: DisclosureType.ValueType  # 0
InternationalisedName: DisclosureType.ValueType  # 1
LocalOrganisation: DisclosureType.ValueType  # 2
InternationalisedOrganisation: DisclosureType.ValueType  # 3
LocalAddress: DisclosureType.ValueType  # 4
InternationalisedAddress: DisclosureType.ValueType  # 5
Voice: DisclosureType.ValueType  # 6
Fax: DisclosureType.ValueType  # 7
Email: DisclosureType.ValueType  # 8
global___DisclosureType = DisclosureType

class _ContactStatus:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _ContactStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_ContactStatus.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    ClientDeleteProhibited: _ContactStatus.ValueType  # 0
    ClientTransferProhibited: _ContactStatus.ValueType  # 1
    ClientUpdateProhibited: _ContactStatus.ValueType  # 2
    Linked: _ContactStatus.ValueType  # 3
    Ok: _ContactStatus.ValueType  # 4
    PendingCreate: _ContactStatus.ValueType  # 5
    PendingDelete: _ContactStatus.ValueType  # 6
    PendingTransfer: _ContactStatus.ValueType  # 7
    PendingUpdate: _ContactStatus.ValueType  # 8
    ServerDeleteProhibited: _ContactStatus.ValueType  # 9
    ServerTransferProhibited: _ContactStatus.ValueType  # 10
    ServerUpdateProhibited: _ContactStatus.ValueType  # 11

class ContactStatus(_ContactStatus, metaclass=_ContactStatusEnumTypeWrapper): ...

ClientDeleteProhibited: ContactStatus.ValueType  # 0
ClientTransferProhibited: ContactStatus.ValueType  # 1
ClientUpdateProhibited: ContactStatus.ValueType  # 2
Linked: ContactStatus.ValueType  # 3
Ok: ContactStatus.ValueType  # 4
PendingCreate: ContactStatus.ValueType  # 5
PendingDelete: ContactStatus.ValueType  # 6
PendingTransfer: ContactStatus.ValueType  # 7
PendingUpdate: ContactStatus.ValueType  # 8
ServerDeleteProhibited: ContactStatus.ValueType  # 9
ServerTransferProhibited: ContactStatus.ValueType  # 10
ServerUpdateProhibited: ContactStatus.ValueType  # 11
global___ContactStatus = ContactStatus

@typing_extensions.final
class PostalAddress(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    NAME_FIELD_NUMBER: builtins.int
    ORGANISATION_FIELD_NUMBER: builtins.int
    STREETS_FIELD_NUMBER: builtins.int
    CITY_FIELD_NUMBER: builtins.int
    PROVINCE_FIELD_NUMBER: builtins.int
    POSTAL_CODE_FIELD_NUMBER: builtins.int
    COUNTRY_CODE_FIELD_NUMBER: builtins.int
    IDENTITY_NUMBER_FIELD_NUMBER: builtins.int
    BIRTH_DATE_FIELD_NUMBER: builtins.int
    name: builtins.str
    @property
    def organisation(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def streets(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    city: builtins.str
    @property
    def province(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def postal_code(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    country_code: builtins.str
    @property
    def identity_number(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def birth_date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    def __init__(
        self,
        *,
        name: builtins.str = ...,
        organisation: google.protobuf.wrappers_pb2.StringValue | None = ...,
        streets: collections.abc.Iterable[builtins.str] | None = ...,
        city: builtins.str = ...,
        province: google.protobuf.wrappers_pb2.StringValue | None = ...,
        postal_code: google.protobuf.wrappers_pb2.StringValue | None = ...,
        country_code: builtins.str = ...,
        identity_number: google.protobuf.wrappers_pb2.StringValue | None = ...,
        birth_date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["birth_date", b"birth_date", "identity_number", b"identity_number", "organisation", b"organisation", "postal_code", b"postal_code", "province", b"province"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["birth_date", b"birth_date", "city", b"city", "country_code", b"country_code", "identity_number", b"identity_number", "name", b"name", "organisation", b"organisation", "postal_code", b"postal_code", "province", b"province", "streets", b"streets"]) -> None: ...

global___PostalAddress = PostalAddress

@typing_extensions.final
class ContactCheckRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    id: builtins.str
    registry_name: builtins.str
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        registry_name: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["id", b"id", "registry_name", b"registry_name"]) -> None: ...

global___ContactCheckRequest = ContactCheckRequest

@typing_extensions.final
class ContactCheckReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    AVAILABLE_FIELD_NUMBER: builtins.int
    REASON_FIELD_NUMBER: builtins.int
    CMD_RESP_FIELD_NUMBER: builtins.int
    available: builtins.bool
    @property
    def reason(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    def __init__(
        self,
        *,
        available: builtins.bool = ...,
        reason: google.protobuf.wrappers_pb2.StringValue | None = ...,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp", "reason", b"reason"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["available", b"available", "cmd_resp", b"cmd_resp", "reason", b"reason"]) -> None: ...

global___ContactCheckReply = ContactCheckReply

@typing_extensions.final
class ContactInfoRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    id: builtins.str
    registry_name: builtins.str
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        registry_name: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["id", b"id", "registry_name", b"registry_name"]) -> None: ...

global___ContactInfoRequest = ContactInfoRequest

@typing_extensions.final
class Disclosure(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DISCLOSURE_FIELD_NUMBER: builtins.int
    @property
    def disclosure(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[global___DisclosureType.ValueType]: ...
    def __init__(
        self,
        *,
        disclosure: collections.abc.Iterable[global___DisclosureType.ValueType] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["disclosure", b"disclosure"]) -> None: ...

global___Disclosure = Disclosure

@typing_extensions.final
class ContactInfoReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    REGISTRY_ID_FIELD_NUMBER: builtins.int
    STATUSES_FIELD_NUMBER: builtins.int
    LOCAL_ADDRESS_FIELD_NUMBER: builtins.int
    INTERNATIONALISED_ADDRESS_FIELD_NUMBER: builtins.int
    PHONE_FIELD_NUMBER: builtins.int
    FAX_FIELD_NUMBER: builtins.int
    EMAIL_FIELD_NUMBER: builtins.int
    CLIENT_ID_FIELD_NUMBER: builtins.int
    CLIENT_CREATED_ID_FIELD_NUMBER: builtins.int
    CREATION_DATE_FIELD_NUMBER: builtins.int
    LAST_UPDATED_CLIENT_FIELD_NUMBER: builtins.int
    LAST_UPDATED_DATE_FIELD_NUMBER: builtins.int
    LAST_TRANSFER_DATE_FIELD_NUMBER: builtins.int
    ENTITY_TYPE_FIELD_NUMBER: builtins.int
    TRADING_NAME_FIELD_NUMBER: builtins.int
    COMPANY_NUMBER_FIELD_NUMBER: builtins.int
    DISCLOSURE_FIELD_NUMBER: builtins.int
    AUTH_INFO_FIELD_NUMBER: builtins.int
    NOMINET_DATA_QUALITY_FIELD_NUMBER: builtins.int
    EURID_INFO_FIELD_NUMBER: builtins.int
    CMD_RESP_FIELD_NUMBER: builtins.int
    QUALIFIED_LAWYER_FIELD_NUMBER: builtins.int
    ISNIC_INFO_FIELD_NUMBER: builtins.int
    KEYSYS_FIELD_NUMBER: builtins.int
    id: builtins.str
    registry_id: builtins.str
    @property
    def statuses(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[global___ContactStatus.ValueType]: ...
    @property
    def local_address(self) -> global___PostalAddress: ...
    @property
    def internationalised_address(self) -> global___PostalAddress: ...
    @property
    def phone(self) -> common.common_pb2.Phone: ...
    @property
    def fax(self) -> common.common_pb2.Phone: ...
    email: builtins.str
    client_id: builtins.str
    @property
    def client_created_id(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def creation_date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    @property
    def last_updated_client(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def last_updated_date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    @property
    def last_transfer_date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    entity_type: global___EntityType.ValueType
    @property
    def trading_name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def company_number(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def disclosure(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[global___DisclosureType.ValueType]: ...
    @property
    def auth_info(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def nominet_data_quality(self) -> nominet_ext.nominet_ext_pb2.DataQuality: ...
    @property
    def eurid_info(self) -> eurid.eurid_pb2.ContactExtension: ...
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    @property
    def qualified_lawyer(self) -> contact.qualified_lawyer.qualified_lawyer_pb2.QualifiedLawyer: ...
    @property
    def isnic_info(self) -> isnic.isnic_pb2.ContactInfo: ...
    @property
    def keysys(self) -> keysys.keysys_pb2.ContactInfo: ...
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        registry_id: builtins.str = ...,
        statuses: collections.abc.Iterable[global___ContactStatus.ValueType] | None = ...,
        local_address: global___PostalAddress | None = ...,
        internationalised_address: global___PostalAddress | None = ...,
        phone: common.common_pb2.Phone | None = ...,
        fax: common.common_pb2.Phone | None = ...,
        email: builtins.str = ...,
        client_id: builtins.str = ...,
        client_created_id: google.protobuf.wrappers_pb2.StringValue | None = ...,
        creation_date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        last_updated_client: google.protobuf.wrappers_pb2.StringValue | None = ...,
        last_updated_date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        last_transfer_date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        entity_type: global___EntityType.ValueType = ...,
        trading_name: google.protobuf.wrappers_pb2.StringValue | None = ...,
        company_number: google.protobuf.wrappers_pb2.StringValue | None = ...,
        disclosure: collections.abc.Iterable[global___DisclosureType.ValueType] | None = ...,
        auth_info: google.protobuf.wrappers_pb2.StringValue | None = ...,
        nominet_data_quality: nominet_ext.nominet_ext_pb2.DataQuality | None = ...,
        eurid_info: eurid.eurid_pb2.ContactExtension | None = ...,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
        qualified_lawyer: contact.qualified_lawyer.qualified_lawyer_pb2.QualifiedLawyer | None = ...,
        isnic_info: isnic.isnic_pb2.ContactInfo | None = ...,
        keysys: keysys.keysys_pb2.ContactInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["auth_info", b"auth_info", "client_created_id", b"client_created_id", "cmd_resp", b"cmd_resp", "company_number", b"company_number", "creation_date", b"creation_date", "eurid_info", b"eurid_info", "fax", b"fax", "internationalised_address", b"internationalised_address", "isnic_info", b"isnic_info", "keysys", b"keysys", "last_transfer_date", b"last_transfer_date", "last_updated_client", b"last_updated_client", "last_updated_date", b"last_updated_date", "local_address", b"local_address", "nominet_data_quality", b"nominet_data_quality", "phone", b"phone", "qualified_lawyer", b"qualified_lawyer", "trading_name", b"trading_name"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["auth_info", b"auth_info", "client_created_id", b"client_created_id", "client_id", b"client_id", "cmd_resp", b"cmd_resp", "company_number", b"company_number", "creation_date", b"creation_date", "disclosure", b"disclosure", "email", b"email", "entity_type", b"entity_type", "eurid_info", b"eurid_info", "fax", b"fax", "id", b"id", "internationalised_address", b"internationalised_address", "isnic_info", b"isnic_info", "keysys", b"keysys", "last_transfer_date", b"last_transfer_date", "last_updated_client", b"last_updated_client", "last_updated_date", b"last_updated_date", "local_address", b"local_address", "nominet_data_quality", b"nominet_data_quality", "phone", b"phone", "qualified_lawyer", b"qualified_lawyer", "registry_id", b"registry_id", "statuses", b"statuses", "trading_name", b"trading_name"]) -> None: ...

global___ContactInfoReply = ContactInfoReply

@typing_extensions.final
class ContactCreateRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    LOCAL_ADDRESS_FIELD_NUMBER: builtins.int
    INTERNATIONALISED_ADDRESS_FIELD_NUMBER: builtins.int
    PHONE_FIELD_NUMBER: builtins.int
    FAX_FIELD_NUMBER: builtins.int
    EMAIL_FIELD_NUMBER: builtins.int
    ENTITY_TYPE_FIELD_NUMBER: builtins.int
    TRADING_NAME_FIELD_NUMBER: builtins.int
    COMPANY_NUMBER_FIELD_NUMBER: builtins.int
    DISCLOSURE_FIELD_NUMBER: builtins.int
    EURID_INFO_FIELD_NUMBER: builtins.int
    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    AUTH_INFO_FIELD_NUMBER: builtins.int
    QUALIFIED_LAWYER_FIELD_NUMBER: builtins.int
    ISNIC_INFO_FIELD_NUMBER: builtins.int
    KEYSYS_FIELD_NUMBER: builtins.int
    id: builtins.str
    @property
    def local_address(self) -> global___PostalAddress: ...
    @property
    def internationalised_address(self) -> global___PostalAddress: ...
    @property
    def phone(self) -> common.common_pb2.Phone: ...
    @property
    def fax(self) -> common.common_pb2.Phone: ...
    email: builtins.str
    entity_type: global___EntityType.ValueType
    @property
    def trading_name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def company_number(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def disclosure(self) -> global___Disclosure: ...
    @property
    def eurid_info(self) -> eurid.eurid_pb2.ContactExtension: ...
    registry_name: builtins.str
    auth_info: builtins.str
    @property
    def qualified_lawyer(self) -> contact.qualified_lawyer.qualified_lawyer_pb2.QualifiedLawyer: ...
    @property
    def isnic_info(self) -> isnic.isnic_pb2.ContactCreate: ...
    @property
    def keysys(self) -> keysys.keysys_pb2.ContactCreate: ...
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        local_address: global___PostalAddress | None = ...,
        internationalised_address: global___PostalAddress | None = ...,
        phone: common.common_pb2.Phone | None = ...,
        fax: common.common_pb2.Phone | None = ...,
        email: builtins.str = ...,
        entity_type: global___EntityType.ValueType = ...,
        trading_name: google.protobuf.wrappers_pb2.StringValue | None = ...,
        company_number: google.protobuf.wrappers_pb2.StringValue | None = ...,
        disclosure: global___Disclosure | None = ...,
        eurid_info: eurid.eurid_pb2.ContactExtension | None = ...,
        registry_name: builtins.str = ...,
        auth_info: builtins.str = ...,
        qualified_lawyer: contact.qualified_lawyer.qualified_lawyer_pb2.QualifiedLawyer | None = ...,
        isnic_info: isnic.isnic_pb2.ContactCreate | None = ...,
        keysys: keysys.keysys_pb2.ContactCreate | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["company_number", b"company_number", "disclosure", b"disclosure", "eurid_info", b"eurid_info", "fax", b"fax", "internationalised_address", b"internationalised_address", "isnic_info", b"isnic_info", "keysys", b"keysys", "local_address", b"local_address", "phone", b"phone", "qualified_lawyer", b"qualified_lawyer", "trading_name", b"trading_name"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["auth_info", b"auth_info", "company_number", b"company_number", "disclosure", b"disclosure", "email", b"email", "entity_type", b"entity_type", "eurid_info", b"eurid_info", "fax", b"fax", "id", b"id", "internationalised_address", b"internationalised_address", "isnic_info", b"isnic_info", "keysys", b"keysys", "local_address", b"local_address", "phone", b"phone", "qualified_lawyer", b"qualified_lawyer", "registry_name", b"registry_name", "trading_name", b"trading_name"]) -> None: ...

global___ContactCreateRequest = ContactCreateRequest

@typing_extensions.final
class ContactCreateReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    PENDING_FIELD_NUMBER: builtins.int
    CREATION_DATE_FIELD_NUMBER: builtins.int
    CMD_RESP_FIELD_NUMBER: builtins.int
    id: builtins.str
    pending: builtins.bool
    @property
    def creation_date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        pending: builtins.bool = ...,
        creation_date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp", "creation_date", b"creation_date"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp", "creation_date", b"creation_date", "id", b"id", "pending", b"pending"]) -> None: ...

global___ContactCreateReply = ContactCreateReply

@typing_extensions.final
class ContactDeleteRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    id: builtins.str
    registry_name: builtins.str
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        registry_name: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["id", b"id", "registry_name", b"registry_name"]) -> None: ...

global___ContactDeleteRequest = ContactDeleteRequest

@typing_extensions.final
class ContactDeleteReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PENDING_FIELD_NUMBER: builtins.int
    CMD_RESP_FIELD_NUMBER: builtins.int
    pending: builtins.bool
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    def __init__(
        self,
        *,
        pending: builtins.bool = ...,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp", "pending", b"pending"]) -> None: ...

global___ContactDeleteReply = ContactDeleteReply

@typing_extensions.final
class ContactUpdateRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    ADD_STATUSES_FIELD_NUMBER: builtins.int
    REMOVE_STATUSES_FIELD_NUMBER: builtins.int
    NEW_LOCAL_ADDRESS_FIELD_NUMBER: builtins.int
    NEW_INTERNATIONALISED_ADDRESS_FIELD_NUMBER: builtins.int
    NEW_PHONE_FIELD_NUMBER: builtins.int
    NEW_FAX_FIELD_NUMBER: builtins.int
    NEW_EMAIL_FIELD_NUMBER: builtins.int
    NEW_ENTITY_TYPE_FIELD_NUMBER: builtins.int
    NEW_TRADING_NAME_FIELD_NUMBER: builtins.int
    NEW_COMPANY_NUMBER_FIELD_NUMBER: builtins.int
    DISCLOSURE_FIELD_NUMBER: builtins.int
    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    NEW_AUTH_INFO_FIELD_NUMBER: builtins.int
    NEW_EURID_INFO_FIELD_NUMBER: builtins.int
    QUALIFIED_LAWYER_FIELD_NUMBER: builtins.int
    ISNIC_INFO_FIELD_NUMBER: builtins.int
    KEYSYS_FIELD_NUMBER: builtins.int
    id: builtins.str
    @property
    def add_statuses(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[global___ContactStatus.ValueType]: ...
    @property
    def remove_statuses(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[global___ContactStatus.ValueType]: ...
    @property
    def new_local_address(self) -> global___PostalAddress: ...
    @property
    def new_internationalised_address(self) -> global___PostalAddress: ...
    @property
    def new_phone(self) -> common.common_pb2.Phone: ...
    @property
    def new_fax(self) -> common.common_pb2.Phone: ...
    @property
    def new_email(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    new_entity_type: global___EntityType.ValueType
    @property
    def new_trading_name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def new_company_number(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def disclosure(self) -> global___Disclosure: ...
    registry_name: builtins.str
    @property
    def new_auth_info(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def new_eurid_info(self) -> eurid.eurid_pb2.ContactUpdateExtension: ...
    @property
    def qualified_lawyer(self) -> contact.qualified_lawyer.qualified_lawyer_pb2.QualifiedLawyer: ...
    @property
    def isnic_info(self) -> isnic.isnic_pb2.ContactUpdate: ...
    @property
    def keysys(self) -> keysys.keysys_pb2.ContactUpdate: ...
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        add_statuses: collections.abc.Iterable[global___ContactStatus.ValueType] | None = ...,
        remove_statuses: collections.abc.Iterable[global___ContactStatus.ValueType] | None = ...,
        new_local_address: global___PostalAddress | None = ...,
        new_internationalised_address: global___PostalAddress | None = ...,
        new_phone: common.common_pb2.Phone | None = ...,
        new_fax: common.common_pb2.Phone | None = ...,
        new_email: google.protobuf.wrappers_pb2.StringValue | None = ...,
        new_entity_type: global___EntityType.ValueType = ...,
        new_trading_name: google.protobuf.wrappers_pb2.StringValue | None = ...,
        new_company_number: google.protobuf.wrappers_pb2.StringValue | None = ...,
        disclosure: global___Disclosure | None = ...,
        registry_name: builtins.str = ...,
        new_auth_info: google.protobuf.wrappers_pb2.StringValue | None = ...,
        new_eurid_info: eurid.eurid_pb2.ContactUpdateExtension | None = ...,
        qualified_lawyer: contact.qualified_lawyer.qualified_lawyer_pb2.QualifiedLawyer | None = ...,
        isnic_info: isnic.isnic_pb2.ContactUpdate | None = ...,
        keysys: keysys.keysys_pb2.ContactUpdate | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["disclosure", b"disclosure", "isnic_info", b"isnic_info", "keysys", b"keysys", "new_auth_info", b"new_auth_info", "new_company_number", b"new_company_number", "new_email", b"new_email", "new_eurid_info", b"new_eurid_info", "new_fax", b"new_fax", "new_internationalised_address", b"new_internationalised_address", "new_local_address", b"new_local_address", "new_phone", b"new_phone", "new_trading_name", b"new_trading_name", "qualified_lawyer", b"qualified_lawyer"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["add_statuses", b"add_statuses", "disclosure", b"disclosure", "id", b"id", "isnic_info", b"isnic_info", "keysys", b"keysys", "new_auth_info", b"new_auth_info", "new_company_number", b"new_company_number", "new_email", b"new_email", "new_entity_type", b"new_entity_type", "new_eurid_info", b"new_eurid_info", "new_fax", b"new_fax", "new_internationalised_address", b"new_internationalised_address", "new_local_address", b"new_local_address", "new_phone", b"new_phone", "new_trading_name", b"new_trading_name", "qualified_lawyer", b"qualified_lawyer", "registry_name", b"registry_name", "remove_statuses", b"remove_statuses"]) -> None: ...

global___ContactUpdateRequest = ContactUpdateRequest

@typing_extensions.final
class ContactUpdateReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PENDING_FIELD_NUMBER: builtins.int
    CMD_RESP_FIELD_NUMBER: builtins.int
    pending: builtins.bool
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    def __init__(
        self,
        *,
        pending: builtins.bool = ...,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp", "pending", b"pending"]) -> None: ...

global___ContactUpdateReply = ContactUpdateReply

@typing_extensions.final
class ContactTransferQueryRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    AUTH_INFO_FIELD_NUMBER: builtins.int
    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    id: builtins.str
    @property
    def auth_info(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    registry_name: builtins.str
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        auth_info: google.protobuf.wrappers_pb2.StringValue | None = ...,
        registry_name: builtins.str = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["auth_info", b"auth_info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["auth_info", b"auth_info", "id", b"id", "registry_name", b"registry_name"]) -> None: ...

global___ContactTransferQueryRequest = ContactTransferQueryRequest

@typing_extensions.final
class ContactTransferRequestRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    AUTH_INFO_FIELD_NUMBER: builtins.int
    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    id: builtins.str
    auth_info: builtins.str
    registry_name: builtins.str
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        auth_info: builtins.str = ...,
        registry_name: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["auth_info", b"auth_info", "id", b"id", "registry_name", b"registry_name"]) -> None: ...

global___ContactTransferRequestRequest = ContactTransferRequestRequest

@typing_extensions.final
class ContactTransferReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PENDING_FIELD_NUMBER: builtins.int
    STATUS_FIELD_NUMBER: builtins.int
    REQUESTED_CLIENT_ID_FIELD_NUMBER: builtins.int
    REQUESTED_DATE_FIELD_NUMBER: builtins.int
    ACT_CLIENT_ID_FIELD_NUMBER: builtins.int
    ACT_DATE_FIELD_NUMBER: builtins.int
    CMD_RESP_FIELD_NUMBER: builtins.int
    pending: builtins.bool
    status: common.common_pb2.TransferStatus.ValueType
    requested_client_id: builtins.str
    @property
    def requested_date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    act_client_id: builtins.str
    @property
    def act_date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    def __init__(
        self,
        *,
        pending: builtins.bool = ...,
        status: common.common_pb2.TransferStatus.ValueType = ...,
        requested_client_id: builtins.str = ...,
        requested_date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        act_client_id: builtins.str = ...,
        act_date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["act_date", b"act_date", "cmd_resp", b"cmd_resp", "requested_date", b"requested_date"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["act_client_id", b"act_client_id", "act_date", b"act_date", "cmd_resp", b"cmd_resp", "pending", b"pending", "requested_client_id", b"requested_client_id", "requested_date", b"requested_date", "status", b"status"]) -> None: ...

global___ContactTransferReply = ContactTransferReply

@typing_extensions.final
class ContactPANReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    RESULT_FIELD_NUMBER: builtins.int
    SERVER_TRANSACTION_ID_FIELD_NUMBER: builtins.int
    CLIENT_TRANSACTION_ID_FIELD_NUMBER: builtins.int
    DATE_FIELD_NUMBER: builtins.int
    id: builtins.str
    result: builtins.bool
    @property
    def server_transaction_id(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def client_transaction_id(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    def __init__(
        self,
        *,
        id: builtins.str = ...,
        result: builtins.bool = ...,
        server_transaction_id: google.protobuf.wrappers_pb2.StringValue | None = ...,
        client_transaction_id: google.protobuf.wrappers_pb2.StringValue | None = ...,
        date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["client_transaction_id", b"client_transaction_id", "date", b"date", "server_transaction_id", b"server_transaction_id"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["client_transaction_id", b"client_transaction_id", "date", b"date", "id", b"id", "result", b"result", "server_transaction_id", b"server_transaction_id"]) -> None: ...

global___ContactPANReply = ContactPANReply
