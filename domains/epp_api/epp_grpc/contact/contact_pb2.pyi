from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from common import common_pb2 as _common_pb2
from eurid import eurid_pb2 as _eurid_pb2
from contact.qualified_lawyer import qualified_lawyer_pb2 as _qualified_lawyer_pb2
from nominet_ext import nominet_ext_pb2 as _nominet_ext_pb2
from isnic import isnic_pb2 as _isnic_pb2
from keysys import keysys_pb2 as _keysys_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

ClientDeleteProhibited: ContactStatus
ClientTransferProhibited: ContactStatus
ClientUpdateProhibited: ContactStatus
DESCRIPTOR: _descriptor.FileDescriptor
Email: DisclosureType
Fax: DisclosureType
FinnishAssociation: EntityType
FinnishCompany: EntityType
FinnishGovernment: EntityType
FinnishIndividual: EntityType
FinnishInstitution: EntityType
FinnishMunicipality: EntityType
FinnishPoliticalParty: EntityType
FinnishPublicCommunity: EntityType
InternationalisedAddress: DisclosureType
InternationalisedName: DisclosureType
InternationalisedOrganisation: DisclosureType
Linked: ContactStatus
LocalAddress: DisclosureType
LocalName: DisclosureType
LocalOrganisation: DisclosureType
NotSet: EntityType
Ok: ContactStatus
OtherAssociation: EntityType
OtherCompany: EntityType
OtherGovernment: EntityType
OtherIndividual: EntityType
OtherInstitution: EntityType
OtherMunicipality: EntityType
OtherPoliticalParty: EntityType
OtherPublicCommunity: EntityType
OtherUkEntity: EntityType
PendingCreate: ContactStatus
PendingDelete: ContactStatus
PendingTransfer: ContactStatus
PendingUpdate: ContactStatus
ServerDeleteProhibited: ContactStatus
ServerTransferProhibited: ContactStatus
ServerUpdateProhibited: ContactStatus
UkCorporationByRoyalCharter: EntityType
UkGovernmentBody: EntityType
UkIndividual: EntityType
UkIndustrialProvidentRegisteredCompany: EntityType
UkLimitedCompany: EntityType
UkLimitedLiabilityPartnership: EntityType
UkPartnership: EntityType
UkPoliticalParty: EntityType
UkPublicLimitedCompany: EntityType
UkRegisteredCharity: EntityType
UkSchool: EntityType
UkSoleTrader: EntityType
UkStatutoryBody: EntityType
UnknownEntity: EntityType
Voice: DisclosureType

class ContactCheckReply(_message.Message):
    __slots__ = ["available", "cmd_resp", "reason"]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    available: bool
    cmd_resp: _common_pb2.CommandResponse
    reason: _wrappers_pb2.StringValue
    def __init__(self, available: bool = ..., reason: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class ContactCheckRequest(_message.Message):
    __slots__ = ["id", "registry_name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class ContactCreateReply(_message.Message):
    __slots__ = ["cmd_resp", "creation_date", "id", "pending"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    creation_date: _timestamp_pb2.Timestamp
    id: str
    pending: bool
    def __init__(self, id: _Optional[str] = ..., pending: bool = ..., creation_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class ContactCreateRequest(_message.Message):
    __slots__ = ["auth_info", "company_number", "disclosure", "email", "entity_type", "eurid_info", "fax", "id", "internationalised_address", "isnic_info", "keysys", "local_address", "phone", "qualified_lawyer", "registry_name", "trading_name"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    COMPANY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    DISCLOSURE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ENTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    EURID_INFO_FIELD_NUMBER: _ClassVar[int]
    FAX_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNATIONALISED_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ISNIC_INFO_FIELD_NUMBER: _ClassVar[int]
    KEYSYS_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    QUALIFIED_LAWYER_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    TRADING_NAME_FIELD_NUMBER: _ClassVar[int]
    auth_info: str
    company_number: _wrappers_pb2.StringValue
    disclosure: Disclosure
    email: str
    entity_type: EntityType
    eurid_info: _eurid_pb2.ContactExtension
    fax: _common_pb2.Phone
    id: str
    internationalised_address: PostalAddress
    isnic_info: _isnic_pb2.ContactCreate
    keysys: _keysys_pb2.ContactCreate
    local_address: PostalAddress
    phone: _common_pb2.Phone
    qualified_lawyer: _qualified_lawyer_pb2.QualifiedLawyer
    registry_name: str
    trading_name: _wrappers_pb2.StringValue
    def __init__(self, id: _Optional[str] = ..., local_address: _Optional[_Union[PostalAddress, _Mapping]] = ..., internationalised_address: _Optional[_Union[PostalAddress, _Mapping]] = ..., phone: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., fax: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., email: _Optional[str] = ..., entity_type: _Optional[_Union[EntityType, str]] = ..., trading_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., company_number: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., disclosure: _Optional[_Union[Disclosure, _Mapping]] = ..., eurid_info: _Optional[_Union[_eurid_pb2.ContactExtension, _Mapping]] = ..., registry_name: _Optional[str] = ..., auth_info: _Optional[str] = ..., qualified_lawyer: _Optional[_Union[_qualified_lawyer_pb2.QualifiedLawyer, _Mapping]] = ..., isnic_info: _Optional[_Union[_isnic_pb2.ContactCreate, _Mapping]] = ..., keysys: _Optional[_Union[_keysys_pb2.ContactCreate, _Mapping]] = ...) -> None: ...

class ContactDeleteReply(_message.Message):
    __slots__ = ["cmd_resp", "pending"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    pending: bool
    def __init__(self, pending: bool = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class ContactDeleteRequest(_message.Message):
    __slots__ = ["id", "registry_name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class ContactInfoReply(_message.Message):
    __slots__ = ["auth_info", "client_created_id", "client_id", "cmd_resp", "company_number", "creation_date", "disclosure", "email", "entity_type", "eurid_info", "fax", "id", "internationalised_address", "isnic_info", "keysys", "last_transfer_date", "last_updated_client", "last_updated_date", "local_address", "nominet_data_quality", "phone", "qualified_lawyer", "registry_id", "statuses", "trading_name"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    CLIENT_CREATED_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    COMPANY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    DISCLOSURE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ENTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    EURID_INFO_FIELD_NUMBER: _ClassVar[int]
    FAX_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNATIONALISED_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ISNIC_INFO_FIELD_NUMBER: _ClassVar[int]
    KEYSYS_FIELD_NUMBER: _ClassVar[int]
    LAST_TRANSFER_DATE_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_CLIENT_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_DATE_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NOMINET_DATA_QUALITY_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    QUALIFIED_LAWYER_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_ID_FIELD_NUMBER: _ClassVar[int]
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    TRADING_NAME_FIELD_NUMBER: _ClassVar[int]
    auth_info: _wrappers_pb2.StringValue
    client_created_id: _wrappers_pb2.StringValue
    client_id: str
    cmd_resp: _common_pb2.CommandResponse
    company_number: _wrappers_pb2.StringValue
    creation_date: _timestamp_pb2.Timestamp
    disclosure: _containers.RepeatedScalarFieldContainer[DisclosureType]
    email: str
    entity_type: EntityType
    eurid_info: _eurid_pb2.ContactExtension
    fax: _common_pb2.Phone
    id: str
    internationalised_address: PostalAddress
    isnic_info: _isnic_pb2.ContactInfo
    keysys: _keysys_pb2.ContactInfo
    last_transfer_date: _timestamp_pb2.Timestamp
    last_updated_client: _wrappers_pb2.StringValue
    last_updated_date: _timestamp_pb2.Timestamp
    local_address: PostalAddress
    nominet_data_quality: _nominet_ext_pb2.DataQuality
    phone: _common_pb2.Phone
    qualified_lawyer: _qualified_lawyer_pb2.QualifiedLawyer
    registry_id: str
    statuses: _containers.RepeatedScalarFieldContainer[ContactStatus]
    trading_name: _wrappers_pb2.StringValue
    def __init__(self, id: _Optional[str] = ..., registry_id: _Optional[str] = ..., statuses: _Optional[_Iterable[_Union[ContactStatus, str]]] = ..., local_address: _Optional[_Union[PostalAddress, _Mapping]] = ..., internationalised_address: _Optional[_Union[PostalAddress, _Mapping]] = ..., phone: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., fax: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., email: _Optional[str] = ..., client_id: _Optional[str] = ..., client_created_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., creation_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_updated_client: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., last_updated_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_transfer_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., entity_type: _Optional[_Union[EntityType, str]] = ..., trading_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., company_number: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., disclosure: _Optional[_Iterable[_Union[DisclosureType, str]]] = ..., auth_info: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., nominet_data_quality: _Optional[_Union[_nominet_ext_pb2.DataQuality, _Mapping]] = ..., eurid_info: _Optional[_Union[_eurid_pb2.ContactExtension, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ..., qualified_lawyer: _Optional[_Union[_qualified_lawyer_pb2.QualifiedLawyer, _Mapping]] = ..., isnic_info: _Optional[_Union[_isnic_pb2.ContactInfo, _Mapping]] = ..., keysys: _Optional[_Union[_keysys_pb2.ContactInfo, _Mapping]] = ...) -> None: ...

class ContactInfoRequest(_message.Message):
    __slots__ = ["id", "registry_name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class ContactPANReply(_message.Message):
    __slots__ = ["client_transaction_id", "date", "id", "result", "server_transaction_id"]
    CLIENT_TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SERVER_TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    client_transaction_id: _wrappers_pb2.StringValue
    date: _timestamp_pb2.Timestamp
    id: str
    result: bool
    server_transaction_id: _wrappers_pb2.StringValue
    def __init__(self, id: _Optional[str] = ..., result: bool = ..., server_transaction_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., client_transaction_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ContactTransferQueryRequest(_message.Message):
    __slots__ = ["auth_info", "id", "registry_name"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    auth_info: _wrappers_pb2.StringValue
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., auth_info: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., registry_name: _Optional[str] = ...) -> None: ...

class ContactTransferReply(_message.Message):
    __slots__ = ["act_client_id", "act_date", "cmd_resp", "pending", "requested_client_id", "requested_date", "status"]
    ACT_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    ACT_DATE_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_DATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    act_client_id: str
    act_date: _timestamp_pb2.Timestamp
    cmd_resp: _common_pb2.CommandResponse
    pending: bool
    requested_client_id: str
    requested_date: _timestamp_pb2.Timestamp
    status: _common_pb2.TransferStatus
    def __init__(self, pending: bool = ..., status: _Optional[_Union[_common_pb2.TransferStatus, str]] = ..., requested_client_id: _Optional[str] = ..., requested_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., act_client_id: _Optional[str] = ..., act_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class ContactTransferRequestRequest(_message.Message):
    __slots__ = ["auth_info", "id", "registry_name"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    auth_info: str
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., auth_info: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class ContactUpdateReply(_message.Message):
    __slots__ = ["cmd_resp", "pending"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    pending: bool
    def __init__(self, pending: bool = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class ContactUpdateRequest(_message.Message):
    __slots__ = ["add_statuses", "disclosure", "id", "isnic_info", "keysys", "new_auth_info", "new_company_number", "new_email", "new_entity_type", "new_eurid_info", "new_fax", "new_internationalised_address", "new_local_address", "new_phone", "new_trading_name", "qualified_lawyer", "registry_name", "remove_statuses"]
    ADD_STATUSES_FIELD_NUMBER: _ClassVar[int]
    DISCLOSURE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ISNIC_INFO_FIELD_NUMBER: _ClassVar[int]
    KEYSYS_FIELD_NUMBER: _ClassVar[int]
    NEW_AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    NEW_COMPANY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    NEW_EMAIL_FIELD_NUMBER: _ClassVar[int]
    NEW_ENTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    NEW_EURID_INFO_FIELD_NUMBER: _ClassVar[int]
    NEW_FAX_FIELD_NUMBER: _ClassVar[int]
    NEW_INTERNATIONALISED_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NEW_LOCAL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NEW_PHONE_FIELD_NUMBER: _ClassVar[int]
    NEW_TRADING_NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFIED_LAWYER_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    REMOVE_STATUSES_FIELD_NUMBER: _ClassVar[int]
    add_statuses: _containers.RepeatedScalarFieldContainer[ContactStatus]
    disclosure: Disclosure
    id: str
    isnic_info: _isnic_pb2.ContactUpdate
    keysys: _keysys_pb2.ContactUpdate
    new_auth_info: _wrappers_pb2.StringValue
    new_company_number: _wrappers_pb2.StringValue
    new_email: _wrappers_pb2.StringValue
    new_entity_type: EntityType
    new_eurid_info: _eurid_pb2.ContactUpdateExtension
    new_fax: _common_pb2.Phone
    new_internationalised_address: PostalAddress
    new_local_address: PostalAddress
    new_phone: _common_pb2.Phone
    new_trading_name: _wrappers_pb2.StringValue
    qualified_lawyer: _qualified_lawyer_pb2.QualifiedLawyer
    registry_name: str
    remove_statuses: _containers.RepeatedScalarFieldContainer[ContactStatus]
    def __init__(self, id: _Optional[str] = ..., add_statuses: _Optional[_Iterable[_Union[ContactStatus, str]]] = ..., remove_statuses: _Optional[_Iterable[_Union[ContactStatus, str]]] = ..., new_local_address: _Optional[_Union[PostalAddress, _Mapping]] = ..., new_internationalised_address: _Optional[_Union[PostalAddress, _Mapping]] = ..., new_phone: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., new_fax: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., new_email: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., new_entity_type: _Optional[_Union[EntityType, str]] = ..., new_trading_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., new_company_number: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., disclosure: _Optional[_Union[Disclosure, _Mapping]] = ..., registry_name: _Optional[str] = ..., new_auth_info: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., new_eurid_info: _Optional[_Union[_eurid_pb2.ContactUpdateExtension, _Mapping]] = ..., qualified_lawyer: _Optional[_Union[_qualified_lawyer_pb2.QualifiedLawyer, _Mapping]] = ..., isnic_info: _Optional[_Union[_isnic_pb2.ContactUpdate, _Mapping]] = ..., keysys: _Optional[_Union[_keysys_pb2.ContactUpdate, _Mapping]] = ...) -> None: ...

class Disclosure(_message.Message):
    __slots__ = ["disclosure"]
    DISCLOSURE_FIELD_NUMBER: _ClassVar[int]
    disclosure: _containers.RepeatedScalarFieldContainer[DisclosureType]
    def __init__(self, disclosure: _Optional[_Iterable[_Union[DisclosureType, str]]] = ...) -> None: ...

class PostalAddress(_message.Message):
    __slots__ = ["birth_date", "city", "country_code", "identity_number", "name", "organisation", "postal_code", "province", "streets"]
    BIRTH_DATE_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_CODE_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANISATION_FIELD_NUMBER: _ClassVar[int]
    POSTAL_CODE_FIELD_NUMBER: _ClassVar[int]
    PROVINCE_FIELD_NUMBER: _ClassVar[int]
    STREETS_FIELD_NUMBER: _ClassVar[int]
    birth_date: _timestamp_pb2.Timestamp
    city: str
    country_code: str
    identity_number: _wrappers_pb2.StringValue
    name: str
    organisation: _wrappers_pb2.StringValue
    postal_code: _wrappers_pb2.StringValue
    province: _wrappers_pb2.StringValue
    streets: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., organisation: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., streets: _Optional[_Iterable[str]] = ..., city: _Optional[str] = ..., province: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., postal_code: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., country_code: _Optional[str] = ..., identity_number: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., birth_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class EntityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DisclosureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ContactStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
