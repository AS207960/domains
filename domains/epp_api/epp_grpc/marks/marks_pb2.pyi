from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

Agent: ContactType
Assignee: Entitlement
DESCRIPTOR: _descriptor.FileDescriptor
Licensee: Entitlement
Owner: Entitlement
OwnerContact: ContactType
ThirdParty: ContactType

class Address(_message.Message):
    __slots__ = ["city", "country_code", "postal_code", "province", "street1", "street2", "street3"]
    CITY_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_CODE_FIELD_NUMBER: _ClassVar[int]
    POSTAL_CODE_FIELD_NUMBER: _ClassVar[int]
    PROVINCE_FIELD_NUMBER: _ClassVar[int]
    STREET1_FIELD_NUMBER: _ClassVar[int]
    STREET2_FIELD_NUMBER: _ClassVar[int]
    STREET3_FIELD_NUMBER: _ClassVar[int]
    city: str
    country_code: str
    postal_code: _wrappers_pb2.StringValue
    province: _wrappers_pb2.StringValue
    street1: _wrappers_pb2.StringValue
    street2: _wrappers_pb2.StringValue
    street3: _wrappers_pb2.StringValue
    def __init__(self, street1: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., street2: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., street3: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., city: _Optional[str] = ..., province: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., postal_code: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., country_code: _Optional[str] = ...) -> None: ...

class Contact(_message.Message):
    __slots__ = ["address", "contact_type", "email", "fax", "name", "organisation", "voice"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CONTACT_TYPE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FAX_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANISATION_FIELD_NUMBER: _ClassVar[int]
    VOICE_FIELD_NUMBER: _ClassVar[int]
    address: Address
    contact_type: ContactType
    email: str
    fax: _common_pb2.Phone
    name: str
    organisation: _wrappers_pb2.StringValue
    voice: _common_pb2.Phone
    def __init__(self, name: _Optional[str] = ..., organisation: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., address: _Optional[_Union[Address, _Mapping]] = ..., voice: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., fax: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., email: _Optional[str] = ..., contact_type: _Optional[_Union[ContactType, str]] = ...) -> None: ...

class Court(_message.Message):
    __slots__ = ["contacts", "country_code", "court_name", "goods_and_services", "holders", "id", "labels", "mark_name", "protection_date", "reference_number", "regions"]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_CODE_FIELD_NUMBER: _ClassVar[int]
    COURT_NAME_FIELD_NUMBER: _ClassVar[int]
    GOODS_AND_SERVICES_FIELD_NUMBER: _ClassVar[int]
    HOLDERS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    MARK_NAME_FIELD_NUMBER: _ClassVar[int]
    PROTECTION_DATE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REGIONS_FIELD_NUMBER: _ClassVar[int]
    contacts: _containers.RepeatedCompositeFieldContainer[Contact]
    country_code: str
    court_name: str
    goods_and_services: str
    holders: _containers.RepeatedCompositeFieldContainer[Holder]
    id: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    mark_name: str
    protection_date: _timestamp_pb2.Timestamp
    reference_number: str
    regions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., mark_name: _Optional[str] = ..., holders: _Optional[_Iterable[_Union[Holder, _Mapping]]] = ..., contacts: _Optional[_Iterable[_Union[Contact, _Mapping]]] = ..., labels: _Optional[_Iterable[str]] = ..., goods_and_services: _Optional[str] = ..., reference_number: _Optional[str] = ..., protection_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., country_code: _Optional[str] = ..., regions: _Optional[_Iterable[str]] = ..., court_name: _Optional[str] = ...) -> None: ...

class Holder(_message.Message):
    __slots__ = ["address", "email", "entitlement", "fax", "name", "organisation", "voice"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ENTITLEMENT_FIELD_NUMBER: _ClassVar[int]
    FAX_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANISATION_FIELD_NUMBER: _ClassVar[int]
    VOICE_FIELD_NUMBER: _ClassVar[int]
    address: Address
    email: _wrappers_pb2.StringValue
    entitlement: Entitlement
    fax: _common_pb2.Phone
    name: _wrappers_pb2.StringValue
    organisation: _wrappers_pb2.StringValue
    voice: _common_pb2.Phone
    def __init__(self, name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., organisation: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., address: _Optional[_Union[Address, _Mapping]] = ..., voice: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., fax: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., email: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., entitlement: _Optional[_Union[Entitlement, str]] = ...) -> None: ...

class Mark(_message.Message):
    __slots__ = ["court", "trademark", "treaty_or_statute"]
    COURT_FIELD_NUMBER: _ClassVar[int]
    TRADEMARK_FIELD_NUMBER: _ClassVar[int]
    TREATY_OR_STATUTE_FIELD_NUMBER: _ClassVar[int]
    court: Court
    trademark: TradeMark
    treaty_or_statute: TreatyOrStatute
    def __init__(self, trademark: _Optional[_Union[TradeMark, _Mapping]] = ..., treaty_or_statute: _Optional[_Union[TreatyOrStatute, _Mapping]] = ..., court: _Optional[_Union[Court, _Mapping]] = ...) -> None: ...

class Protection(_message.Message):
    __slots__ = ["country_code", "region", "ruling"]
    COUNTRY_CODE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    RULING_FIELD_NUMBER: _ClassVar[int]
    country_code: str
    region: _wrappers_pb2.StringValue
    ruling: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, country_code: _Optional[str] = ..., region: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., ruling: _Optional[_Iterable[str]] = ...) -> None: ...

class TradeMark(_message.Message):
    __slots__ = ["application_date", "application_id", "classes", "contacts", "expiry_date", "goods_and_services", "holders", "id", "jurisdiction", "labels", "mark_name", "registration_date", "registration_id"]
    APPLICATION_DATE_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    CLASSES_FIELD_NUMBER: _ClassVar[int]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    GOODS_AND_SERVICES_FIELD_NUMBER: _ClassVar[int]
    HOLDERS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    JURISDICTION_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    MARK_NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    REGISTRATION_ID_FIELD_NUMBER: _ClassVar[int]
    application_date: _timestamp_pb2.Timestamp
    application_id: _wrappers_pb2.StringValue
    classes: _containers.RepeatedScalarFieldContainer[int]
    contacts: _containers.RepeatedCompositeFieldContainer[Contact]
    expiry_date: _timestamp_pb2.Timestamp
    goods_and_services: str
    holders: _containers.RepeatedCompositeFieldContainer[Holder]
    id: str
    jurisdiction: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    mark_name: str
    registration_date: _timestamp_pb2.Timestamp
    registration_id: str
    def __init__(self, id: _Optional[str] = ..., mark_name: _Optional[str] = ..., holders: _Optional[_Iterable[_Union[Holder, _Mapping]]] = ..., contacts: _Optional[_Iterable[_Union[Contact, _Mapping]]] = ..., jurisdiction: _Optional[str] = ..., classes: _Optional[_Iterable[int]] = ..., labels: _Optional[_Iterable[str]] = ..., goods_and_services: _Optional[str] = ..., application_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., application_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., registration_id: _Optional[str] = ..., registration_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TreatyOrStatute(_message.Message):
    __slots__ = ["contacts", "execution_date", "goods_and_services", "holders", "id", "labels", "mark_name", "protection_date", "protections", "reference_number", "title"]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_DATE_FIELD_NUMBER: _ClassVar[int]
    GOODS_AND_SERVICES_FIELD_NUMBER: _ClassVar[int]
    HOLDERS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    MARK_NAME_FIELD_NUMBER: _ClassVar[int]
    PROTECTIONS_FIELD_NUMBER: _ClassVar[int]
    PROTECTION_DATE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    contacts: _containers.RepeatedCompositeFieldContainer[Contact]
    execution_date: _timestamp_pb2.Timestamp
    goods_and_services: str
    holders: _containers.RepeatedCompositeFieldContainer[Holder]
    id: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    mark_name: str
    protection_date: _timestamp_pb2.Timestamp
    protections: _containers.RepeatedCompositeFieldContainer[Protection]
    reference_number: str
    title: str
    def __init__(self, id: _Optional[str] = ..., mark_name: _Optional[str] = ..., holders: _Optional[_Iterable[_Union[Holder, _Mapping]]] = ..., contacts: _Optional[_Iterable[_Union[Contact, _Mapping]]] = ..., protections: _Optional[_Iterable[_Union[Protection, _Mapping]]] = ..., labels: _Optional[_Iterable[str]] = ..., goods_and_services: _Optional[str] = ..., reference_number: _Optional[str] = ..., protection_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., title: _Optional[str] = ..., execution_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Entitlement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ContactType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
