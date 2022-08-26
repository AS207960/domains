from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from common import common_pb2 as _common_pb2
from rgp import rgp_pb2 as _rgp_pb2
from fee import fee_pb2 as _fee_pb2
from eurid import eurid_pb2 as _eurid_pb2
from launch import launch_pb2 as _launch_pb2
from domain_common import domain_common_pb2 as _domain_common_pb2
from isnic import isnic_pb2 as _isnic_pb2
from personal_registration import personal_registration_pb2 as _personal_registration_pb2
from keysys import keysys_pb2 as _keysys_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

All: DomainHostsType
DESCRIPTOR: _descriptor.FileDescriptor
Delegated: DomainHostsType
None: DomainHostsType
Subordinate: DomainHostsType

class Contact(_message.Message):
    __slots__ = ["id", "type"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class DomainCheckReply(_message.Message):
    __slots__ = ["available", "cmd_resp", "donuts_fee_check", "eurid_data", "eurid_idn", "fee_check", "reason", "registry_name"]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_CHECK_FIELD_NUMBER: _ClassVar[int]
    EURID_DATA_FIELD_NUMBER: _ClassVar[int]
    EURID_IDN_FIELD_NUMBER: _ClassVar[int]
    FEE_CHECK_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    available: bool
    cmd_resp: _common_pb2.CommandResponse
    donuts_fee_check: _fee_pb2.DonutsFeeData
    eurid_data: _eurid_pb2.DomainCheckData
    eurid_idn: _eurid_pb2.IDN
    fee_check: _fee_pb2.FeeCheckData
    reason: _wrappers_pb2.StringValue
    registry_name: str
    def __init__(self, available: bool = ..., reason: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., fee_check: _Optional[_Union[_fee_pb2.FeeCheckData, _Mapping]] = ..., donuts_fee_check: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., registry_name: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ..., eurid_idn: _Optional[_Union[_eurid_pb2.IDN, _Mapping]] = ..., eurid_data: _Optional[_Union[_eurid_pb2.DomainCheckData, _Mapping]] = ...) -> None: ...

class DomainCheckRequest(_message.Message):
    __slots__ = ["fee_check", "keysys", "launch_check", "name", "registry_name"]
    FEE_CHECK_FIELD_NUMBER: _ClassVar[int]
    KEYSYS_FIELD_NUMBER: _ClassVar[int]
    LAUNCH_CHECK_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    fee_check: _fee_pb2.FeeCheck
    keysys: _keysys_pb2.DomainCheck
    launch_check: _launch_pb2.Phase
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., fee_check: _Optional[_Union[_fee_pb2.FeeCheck, _Mapping]] = ..., launch_check: _Optional[_Union[_launch_pb2.Phase, _Mapping]] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., keysys: _Optional[_Union[_keysys_pb2.DomainCheck, _Mapping]] = ...) -> None: ...

class DomainClaimsCheckReply(_message.Message):
    __slots__ = ["claims_keys", "cmd_resp", "exists", "registry_name"]
    CLAIMS_KEYS_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    EXISTS_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    claims_keys: _containers.RepeatedCompositeFieldContainer[_launch_pb2.ClaimsKey]
    cmd_resp: _common_pb2.CommandResponse
    exists: bool
    registry_name: str
    def __init__(self, exists: bool = ..., claims_keys: _Optional[_Iterable[_Union[_launch_pb2.ClaimsKey, _Mapping]]] = ..., registry_name: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class DomainClaimsCheckRequest(_message.Message):
    __slots__ = ["launch_check", "name", "registry_name"]
    LAUNCH_CHECK_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    launch_check: _launch_pb2.Phase
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., launch_check: _Optional[_Union[_launch_pb2.Phase, _Mapping]] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainCreateReply(_message.Message):
    __slots__ = ["cmd_resp", "creation_date", "donuts_fee_data", "eurid_idn", "expiry_date", "fee_data", "launch_data", "name", "pending", "personal_registration", "registry_name"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    EURID_IDN_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    LAUNCH_DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_REGISTRATION_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    creation_date: _timestamp_pb2.Timestamp
    donuts_fee_data: _fee_pb2.DonutsFeeData
    eurid_idn: _eurid_pb2.IDN
    expiry_date: _timestamp_pb2.Timestamp
    fee_data: _fee_pb2.FeeData
    launch_data: _launch_pb2.LaunchData
    name: str
    pending: bool
    personal_registration: _personal_registration_pb2.PersonalRegistrationCreate
    registry_name: str
    def __init__(self, name: _Optional[str] = ..., pending: bool = ..., creation_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., fee_data: _Optional[_Union[_fee_pb2.FeeData, _Mapping]] = ..., donuts_fee_data: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., launch_data: _Optional[_Union[_launch_pb2.LaunchData, _Mapping]] = ..., registry_name: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ..., eurid_idn: _Optional[_Union[_eurid_pb2.IDN, _Mapping]] = ..., personal_registration: _Optional[_Union[_personal_registration_pb2.PersonalRegistrationCreate, _Mapping]] = ...) -> None: ...

class DomainCreateRequest(_message.Message):
    __slots__ = ["auth_info", "contacts", "donuts_fee_agreement", "eurid_data", "fee_agreement", "isnic_payment", "keysys", "launch_data", "name", "nameservers", "period", "personal_registration", "registrant", "registry_name", "sec_dns"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    EURID_DATA_FIELD_NUMBER: _ClassVar[int]
    FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    ISNIC_PAYMENT_FIELD_NUMBER: _ClassVar[int]
    KEYSYS_FIELD_NUMBER: _ClassVar[int]
    LAUNCH_DATA_FIELD_NUMBER: _ClassVar[int]
    NAMESERVERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_REGISTRATION_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    SEC_DNS_FIELD_NUMBER: _ClassVar[int]
    auth_info: str
    contacts: _containers.RepeatedCompositeFieldContainer[Contact]
    donuts_fee_agreement: _fee_pb2.DonutsFeeData
    eurid_data: _eurid_pb2.DomainCreateExtension
    fee_agreement: _fee_pb2.FeeAgreement
    isnic_payment: _isnic_pb2.PaymentInfo
    keysys: _keysys_pb2.DomainCreate
    launch_data: _launch_pb2.LaunchCreate
    name: str
    nameservers: _containers.RepeatedCompositeFieldContainer[NameServer]
    period: _common_pb2.Period
    personal_registration: _personal_registration_pb2.PersonalRegistrationInfo
    registrant: str
    registry_name: _wrappers_pb2.StringValue
    sec_dns: SecDNSData
    def __init__(self, name: _Optional[str] = ..., period: _Optional[_Union[_common_pb2.Period, _Mapping]] = ..., registrant: _Optional[str] = ..., contacts: _Optional[_Iterable[_Union[Contact, _Mapping]]] = ..., nameservers: _Optional[_Iterable[_Union[NameServer, _Mapping]]] = ..., auth_info: _Optional[str] = ..., sec_dns: _Optional[_Union[SecDNSData, _Mapping]] = ..., launch_data: _Optional[_Union[_launch_pb2.LaunchCreate, _Mapping]] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., donuts_fee_agreement: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., fee_agreement: _Optional[_Union[_fee_pb2.FeeAgreement, _Mapping]] = ..., eurid_data: _Optional[_Union[_eurid_pb2.DomainCreateExtension, _Mapping]] = ..., isnic_payment: _Optional[_Union[_isnic_pb2.PaymentInfo, _Mapping]] = ..., personal_registration: _Optional[_Union[_personal_registration_pb2.PersonalRegistrationInfo, _Mapping]] = ..., keysys: _Optional[_Union[_keysys_pb2.DomainCreate, _Mapping]] = ...) -> None: ...

class DomainDeleteReply(_message.Message):
    __slots__ = ["cmd_resp", "eurid_idn", "fee_data", "pending", "registry_name"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    EURID_IDN_FIELD_NUMBER: _ClassVar[int]
    FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    eurid_idn: _eurid_pb2.IDN
    fee_data: _fee_pb2.FeeData
    pending: bool
    registry_name: str
    def __init__(self, pending: bool = ..., fee_data: _Optional[_Union[_fee_pb2.FeeData, _Mapping]] = ..., registry_name: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ..., eurid_idn: _Optional[_Union[_eurid_pb2.IDN, _Mapping]] = ...) -> None: ...

class DomainDeleteRequest(_message.Message):
    __slots__ = ["donuts_fee_agreement", "eurid_data", "keysys", "launch_data", "name", "registry_name"]
    DONUTS_FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    EURID_DATA_FIELD_NUMBER: _ClassVar[int]
    KEYSYS_FIELD_NUMBER: _ClassVar[int]
    LAUNCH_DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    donuts_fee_agreement: _fee_pb2.DonutsFeeData
    eurid_data: _eurid_pb2.DomainDeleteExtension
    keysys: _keysys_pb2.DomainDelete
    launch_data: _launch_pb2.LaunchData
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., launch_data: _Optional[_Union[_launch_pb2.LaunchData, _Mapping]] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., donuts_fee_agreement: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., eurid_data: _Optional[_Union[_eurid_pb2.DomainDeleteExtension, _Mapping]] = ..., keysys: _Optional[_Union[_keysys_pb2.DomainDelete, _Mapping]] = ...) -> None: ...

class DomainHosts(_message.Message):
    __slots__ = ["hosts"]
    HOSTS_FIELD_NUMBER: _ClassVar[int]
    hosts: DomainHostsType
    def __init__(self, hosts: _Optional[_Union[DomainHostsType, str]] = ...) -> None: ...

class DomainInfoReply(_message.Message):
    __slots__ = ["auth_info", "client_created_id", "client_id", "cmd_resp", "contacts", "creation_date", "donuts_fee_data", "eurid_data", "eurid_idn", "expiry_date", "hosts", "isnic_info", "keysys", "last_transfer_date", "last_updated_client", "last_updated_date", "launch_info", "name", "nameservers", "personal_registration", "registrant", "registry_id", "registry_name", "rgp_state", "sec_dns", "statuses", "verisign_whois_info"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    CLIENT_CREATED_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    EURID_DATA_FIELD_NUMBER: _ClassVar[int]
    EURID_IDN_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    HOSTS_FIELD_NUMBER: _ClassVar[int]
    ISNIC_INFO_FIELD_NUMBER: _ClassVar[int]
    KEYSYS_FIELD_NUMBER: _ClassVar[int]
    LAST_TRANSFER_DATE_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_CLIENT_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_DATE_FIELD_NUMBER: _ClassVar[int]
    LAUNCH_INFO_FIELD_NUMBER: _ClassVar[int]
    NAMESERVERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_REGISTRATION_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    RGP_STATE_FIELD_NUMBER: _ClassVar[int]
    SEC_DNS_FIELD_NUMBER: _ClassVar[int]
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    VERISIGN_WHOIS_INFO_FIELD_NUMBER: _ClassVar[int]
    auth_info: _wrappers_pb2.StringValue
    client_created_id: _wrappers_pb2.StringValue
    client_id: str
    cmd_resp: _common_pb2.CommandResponse
    contacts: _containers.RepeatedCompositeFieldContainer[Contact]
    creation_date: _timestamp_pb2.Timestamp
    donuts_fee_data: _fee_pb2.DonutsFeeData
    eurid_data: _eurid_pb2.DomainInfo
    eurid_idn: _eurid_pb2.IDN
    expiry_date: _timestamp_pb2.Timestamp
    hosts: _containers.RepeatedScalarFieldContainer[str]
    isnic_info: _isnic_pb2.DomainInfo
    keysys: _keysys_pb2.DomainInfo
    last_transfer_date: _timestamp_pb2.Timestamp
    last_updated_client: _wrappers_pb2.StringValue
    last_updated_date: _timestamp_pb2.Timestamp
    launch_info: _launch_pb2.LaunchInfoData
    name: str
    nameservers: _containers.RepeatedCompositeFieldContainer[NameServer]
    personal_registration: _personal_registration_pb2.PersonalRegistrationInfo
    registrant: str
    registry_id: str
    registry_name: str
    rgp_state: _containers.RepeatedScalarFieldContainer[_rgp_pb2.RGPState]
    sec_dns: SecDNSData
    statuses: _containers.RepeatedScalarFieldContainer[_domain_common_pb2.DomainStatus]
    verisign_whois_info: VerisignWhoisInfo
    def __init__(self, name: _Optional[str] = ..., registry_id: _Optional[str] = ..., statuses: _Optional[_Iterable[_Union[_domain_common_pb2.DomainStatus, str]]] = ..., registrant: _Optional[str] = ..., contacts: _Optional[_Iterable[_Union[Contact, _Mapping]]] = ..., nameservers: _Optional[_Iterable[_Union[NameServer, _Mapping]]] = ..., hosts: _Optional[_Iterable[str]] = ..., client_id: _Optional[str] = ..., client_created_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., creation_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_updated_client: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., last_updated_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_transfer_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., registry_name: _Optional[str] = ..., rgp_state: _Optional[_Iterable[_Union[_rgp_pb2.RGPState, str]]] = ..., auth_info: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., sec_dns: _Optional[_Union[SecDNSData, _Mapping]] = ..., launch_info: _Optional[_Union[_launch_pb2.LaunchInfoData, _Mapping]] = ..., donuts_fee_data: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., verisign_whois_info: _Optional[_Union[VerisignWhoisInfo, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ..., eurid_idn: _Optional[_Union[_eurid_pb2.IDN, _Mapping]] = ..., eurid_data: _Optional[_Union[_eurid_pb2.DomainInfo, _Mapping]] = ..., isnic_info: _Optional[_Union[_isnic_pb2.DomainInfo, _Mapping]] = ..., personal_registration: _Optional[_Union[_personal_registration_pb2.PersonalRegistrationInfo, _Mapping]] = ..., keysys: _Optional[_Union[_keysys_pb2.DomainInfo, _Mapping]] = ...) -> None: ...

class DomainInfoRequest(_message.Message):
    __slots__ = ["auth_info", "donuts_fee_agreement", "eurid_data", "hosts", "launch_info", "name", "registry_name"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    EURID_DATA_FIELD_NUMBER: _ClassVar[int]
    HOSTS_FIELD_NUMBER: _ClassVar[int]
    LAUNCH_INFO_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    auth_info: _wrappers_pb2.StringValue
    donuts_fee_agreement: _fee_pb2.DonutsFeeData
    eurid_data: _eurid_pb2.DomainInfoRequest
    hosts: DomainHosts
    launch_info: _launch_pb2.LaunchInfo
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., auth_info: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., hosts: _Optional[_Union[DomainHosts, _Mapping]] = ..., launch_info: _Optional[_Union[_launch_pb2.LaunchInfo, _Mapping]] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., donuts_fee_agreement: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., eurid_data: _Optional[_Union[_eurid_pb2.DomainInfoRequest, _Mapping]] = ...) -> None: ...

class DomainPANReply(_message.Message):
    __slots__ = ["client_transaction_id", "date", "name", "result", "server_transaction_id"]
    CLIENT_TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SERVER_TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    client_transaction_id: _wrappers_pb2.StringValue
    date: _timestamp_pb2.Timestamp
    name: str
    result: bool
    server_transaction_id: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., result: bool = ..., server_transaction_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., client_transaction_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DomainRenewReply(_message.Message):
    __slots__ = ["cmd_resp", "donuts_fee_data", "eurid_data", "eurid_idn", "expiry_date", "fee_data", "name", "pending", "personal_registration", "registry_name"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    EURID_DATA_FIELD_NUMBER: _ClassVar[int]
    EURID_IDN_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_REGISTRATION_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    donuts_fee_data: _fee_pb2.DonutsFeeData
    eurid_data: _eurid_pb2.DomainRenewInfo
    eurid_idn: _eurid_pb2.IDN
    expiry_date: _timestamp_pb2.Timestamp
    fee_data: _fee_pb2.FeeData
    name: str
    pending: bool
    personal_registration: _personal_registration_pb2.PersonalRegistrationCreate
    registry_name: str
    def __init__(self, name: _Optional[str] = ..., pending: bool = ..., expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., fee_data: _Optional[_Union[_fee_pb2.FeeData, _Mapping]] = ..., donuts_fee_data: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., registry_name: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ..., eurid_idn: _Optional[_Union[_eurid_pb2.IDN, _Mapping]] = ..., eurid_data: _Optional[_Union[_eurid_pb2.DomainRenewInfo, _Mapping]] = ..., personal_registration: _Optional[_Union[_personal_registration_pb2.PersonalRegistrationCreate, _Mapping]] = ...) -> None: ...

class DomainRenewRequest(_message.Message):
    __slots__ = ["current_expiry_date", "donuts_fee_agreement", "fee_agreement", "isnic_payment", "keysys", "name", "period", "registry_name"]
    CURRENT_EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    ISNIC_PAYMENT_FIELD_NUMBER: _ClassVar[int]
    KEYSYS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    current_expiry_date: _timestamp_pb2.Timestamp
    donuts_fee_agreement: _fee_pb2.DonutsFeeData
    fee_agreement: _fee_pb2.FeeAgreement
    isnic_payment: _isnic_pb2.PaymentInfo
    keysys: _keysys_pb2.DomainRenew
    name: str
    period: _common_pb2.Period
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., period: _Optional[_Union[_common_pb2.Period, _Mapping]] = ..., current_expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., donuts_fee_agreement: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., fee_agreement: _Optional[_Union[_fee_pb2.FeeAgreement, _Mapping]] = ..., isnic_payment: _Optional[_Union[_isnic_pb2.PaymentInfo, _Mapping]] = ..., keysys: _Optional[_Union[_keysys_pb2.DomainRenew, _Mapping]] = ...) -> None: ...

class DomainSyncRequest(_message.Message):
    __slots__ = ["day", "month", "name", "registry_name"]
    DAY_FIELD_NUMBER: _ClassVar[int]
    MONTH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    day: int
    month: int
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., month: _Optional[int] = ..., day: _Optional[int] = ...) -> None: ...

class DomainTrademarkCheckRequest(_message.Message):
    __slots__ = ["name", "registry_name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainTransferAcceptRejectRequest(_message.Message):
    __slots__ = ["auth_info", "name", "registry_name"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    auth_info: str
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., auth_info: _Optional[str] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainTransferQueryRequest(_message.Message):
    __slots__ = ["auth_info", "name", "registry_name"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    auth_info: _wrappers_pb2.StringValue
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., auth_info: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainTransferReply(_message.Message):
    __slots__ = ["act_client_id", "act_date", "cmd_resp", "donuts_fee_data", "eurid_data", "eurid_idn", "expiry_date", "fee_data", "name", "pending", "personal_registration", "registry_name", "requested_client_id", "requested_date", "status"]
    ACT_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    ACT_DATE_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    EURID_DATA_FIELD_NUMBER: _ClassVar[int]
    EURID_IDN_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_REGISTRATION_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_DATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    act_client_id: str
    act_date: _timestamp_pb2.Timestamp
    cmd_resp: _common_pb2.CommandResponse
    donuts_fee_data: _fee_pb2.DonutsFeeData
    eurid_data: _eurid_pb2.DomainTransferInfo
    eurid_idn: _eurid_pb2.IDN
    expiry_date: _timestamp_pb2.Timestamp
    fee_data: _fee_pb2.FeeData
    name: str
    pending: bool
    personal_registration: _personal_registration_pb2.PersonalRegistrationCreate
    registry_name: str
    requested_client_id: str
    requested_date: _timestamp_pb2.Timestamp
    status: _common_pb2.TransferStatus
    def __init__(self, pending: bool = ..., name: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.TransferStatus, str]] = ..., requested_client_id: _Optional[str] = ..., requested_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., act_client_id: _Optional[str] = ..., act_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., fee_data: _Optional[_Union[_fee_pb2.FeeData, _Mapping]] = ..., donuts_fee_data: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., registry_name: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ..., eurid_idn: _Optional[_Union[_eurid_pb2.IDN, _Mapping]] = ..., eurid_data: _Optional[_Union[_eurid_pb2.DomainTransferInfo, _Mapping]] = ..., personal_registration: _Optional[_Union[_personal_registration_pb2.PersonalRegistrationCreate, _Mapping]] = ...) -> None: ...

class DomainTransferRequestRequest(_message.Message):
    __slots__ = ["auth_info", "donuts_fee_agreement", "eurid_data", "fee_agreement", "keysys", "name", "period", "registry_name"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    EURID_DATA_FIELD_NUMBER: _ClassVar[int]
    FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    KEYSYS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    auth_info: str
    donuts_fee_agreement: _fee_pb2.DonutsFeeData
    eurid_data: _eurid_pb2.DomainTransferExtension
    fee_agreement: _fee_pb2.FeeAgreement
    keysys: _keysys_pb2.DomainTransfer
    name: str
    period: _common_pb2.Period
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., period: _Optional[_Union[_common_pb2.Period, _Mapping]] = ..., auth_info: _Optional[str] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., donuts_fee_agreement: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., fee_agreement: _Optional[_Union[_fee_pb2.FeeAgreement, _Mapping]] = ..., eurid_data: _Optional[_Union[_eurid_pb2.DomainTransferExtension, _Mapping]] = ..., keysys: _Optional[_Union[_keysys_pb2.DomainTransfer, _Mapping]] = ...) -> None: ...

class DomainUpdateReply(_message.Message):
    __slots__ = ["cmd_resp", "donuts_fee_data", "fee_data", "pending", "registry_name"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    donuts_fee_data: _fee_pb2.DonutsFeeData
    fee_data: _fee_pb2.FeeData
    pending: bool
    registry_name: str
    def __init__(self, pending: bool = ..., fee_data: _Optional[_Union[_fee_pb2.FeeData, _Mapping]] = ..., donuts_fee_data: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., registry_name: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class DomainUpdateRequest(_message.Message):
    __slots__ = ["add", "donuts_fee_agreement", "eurid_data", "fee_agreement", "isnic_info", "keysys", "launch_data", "name", "new_auth_info", "new_registrant", "registry_name", "remove", "sec_dns"]
    class Param(_message.Message):
        __slots__ = ["contact", "nameserver", "state"]
        CONTACT_FIELD_NUMBER: _ClassVar[int]
        NAMESERVER_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        contact: Contact
        nameserver: NameServer
        state: _domain_common_pb2.DomainStatus
        def __init__(self, nameserver: _Optional[_Union[NameServer, _Mapping]] = ..., contact: _Optional[_Union[Contact, _Mapping]] = ..., state: _Optional[_Union[_domain_common_pb2.DomainStatus, str]] = ...) -> None: ...
    ADD_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    EURID_DATA_FIELD_NUMBER: _ClassVar[int]
    FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    ISNIC_INFO_FIELD_NUMBER: _ClassVar[int]
    KEYSYS_FIELD_NUMBER: _ClassVar[int]
    LAUNCH_DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NEW_AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    NEW_REGISTRANT_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    REMOVE_FIELD_NUMBER: _ClassVar[int]
    SEC_DNS_FIELD_NUMBER: _ClassVar[int]
    add: _containers.RepeatedCompositeFieldContainer[DomainUpdateRequest.Param]
    donuts_fee_agreement: _fee_pb2.DonutsFeeData
    eurid_data: _eurid_pb2.DomainUpdateExtension
    fee_agreement: _fee_pb2.FeeAgreement
    isnic_info: _isnic_pb2.DomainUpdate
    keysys: _keysys_pb2.DomainUpdate
    launch_data: _launch_pb2.LaunchData
    name: str
    new_auth_info: _wrappers_pb2.StringValue
    new_registrant: _wrappers_pb2.StringValue
    registry_name: _wrappers_pb2.StringValue
    remove: _containers.RepeatedCompositeFieldContainer[DomainUpdateRequest.Param]
    sec_dns: UpdateSecDNSData
    def __init__(self, name: _Optional[str] = ..., add: _Optional[_Iterable[_Union[DomainUpdateRequest.Param, _Mapping]]] = ..., remove: _Optional[_Iterable[_Union[DomainUpdateRequest.Param, _Mapping]]] = ..., new_registrant: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., new_auth_info: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., sec_dns: _Optional[_Union[UpdateSecDNSData, _Mapping]] = ..., launch_data: _Optional[_Union[_launch_pb2.LaunchData, _Mapping]] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., donuts_fee_agreement: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ..., fee_agreement: _Optional[_Union[_fee_pb2.FeeAgreement, _Mapping]] = ..., eurid_data: _Optional[_Union[_eurid_pb2.DomainUpdateExtension, _Mapping]] = ..., isnic_info: _Optional[_Union[_isnic_pb2.DomainUpdate, _Mapping]] = ..., keysys: _Optional[_Union[_keysys_pb2.DomainUpdate, _Mapping]] = ...) -> None: ...

class NameServer(_message.Message):
    __slots__ = ["addresses", "eurid_idn", "host_name", "host_obj"]
    ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    EURID_IDN_FIELD_NUMBER: _ClassVar[int]
    HOST_NAME_FIELD_NUMBER: _ClassVar[int]
    HOST_OBJ_FIELD_NUMBER: _ClassVar[int]
    addresses: _containers.RepeatedCompositeFieldContainer[_common_pb2.IPAddress]
    eurid_idn: _eurid_pb2.IDN
    host_name: str
    host_obj: str
    def __init__(self, host_obj: _Optional[str] = ..., host_name: _Optional[str] = ..., addresses: _Optional[_Iterable[_Union[_common_pb2.IPAddress, _Mapping]]] = ..., eurid_idn: _Optional[_Union[_eurid_pb2.IDN, _Mapping]] = ...) -> None: ...

class SecDNSDSData(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[SecDNSDSDatum]
    def __init__(self, data: _Optional[_Iterable[_Union[SecDNSDSDatum, _Mapping]]] = ...) -> None: ...

class SecDNSDSDatum(_message.Message):
    __slots__ = ["algorithm", "digest", "digest_type", "key_data", "key_tag"]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    DIGEST_FIELD_NUMBER: _ClassVar[int]
    DIGEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    KEY_DATA_FIELD_NUMBER: _ClassVar[int]
    KEY_TAG_FIELD_NUMBER: _ClassVar[int]
    algorithm: int
    digest: str
    digest_type: int
    key_data: SecDNSKeyDatum
    key_tag: int
    def __init__(self, key_tag: _Optional[int] = ..., algorithm: _Optional[int] = ..., digest_type: _Optional[int] = ..., digest: _Optional[str] = ..., key_data: _Optional[_Union[SecDNSKeyDatum, _Mapping]] = ...) -> None: ...

class SecDNSData(_message.Message):
    __slots__ = ["ds_data", "key_data", "max_sig_life"]
    DS_DATA_FIELD_NUMBER: _ClassVar[int]
    KEY_DATA_FIELD_NUMBER: _ClassVar[int]
    MAX_SIG_LIFE_FIELD_NUMBER: _ClassVar[int]
    ds_data: SecDNSDSData
    key_data: SecDNSKeyData
    max_sig_life: _wrappers_pb2.Int64Value
    def __init__(self, max_sig_life: _Optional[_Union[_wrappers_pb2.Int64Value, _Mapping]] = ..., ds_data: _Optional[_Union[SecDNSDSData, _Mapping]] = ..., key_data: _Optional[_Union[SecDNSKeyData, _Mapping]] = ...) -> None: ...

class SecDNSKeyData(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[SecDNSKeyDatum]
    def __init__(self, data: _Optional[_Iterable[_Union[SecDNSKeyDatum, _Mapping]]] = ...) -> None: ...

class SecDNSKeyDatum(_message.Message):
    __slots__ = ["algorithm", "flags", "protocol", "public_key"]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    algorithm: int
    flags: int
    protocol: int
    public_key: str
    def __init__(self, flags: _Optional[int] = ..., protocol: _Optional[int] = ..., algorithm: _Optional[int] = ..., public_key: _Optional[str] = ...) -> None: ...

class UpdateSecDNSData(_message.Message):
    __slots__ = ["add_ds_data", "add_key_data", "all", "new_max_sig_life", "rem_ds_data", "rem_key_data", "urgent"]
    ADD_DS_DATA_FIELD_NUMBER: _ClassVar[int]
    ADD_KEY_DATA_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    NEW_MAX_SIG_LIFE_FIELD_NUMBER: _ClassVar[int]
    REM_DS_DATA_FIELD_NUMBER: _ClassVar[int]
    REM_KEY_DATA_FIELD_NUMBER: _ClassVar[int]
    URGENT_FIELD_NUMBER: _ClassVar[int]
    add_ds_data: SecDNSDSData
    add_key_data: SecDNSKeyData
    all: bool
    new_max_sig_life: _wrappers_pb2.Int64Value
    rem_ds_data: SecDNSDSData
    rem_key_data: SecDNSKeyData
    urgent: _wrappers_pb2.BoolValue
    def __init__(self, urgent: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., new_max_sig_life: _Optional[_Union[_wrappers_pb2.Int64Value, _Mapping]] = ..., add_ds_data: _Optional[_Union[SecDNSDSData, _Mapping]] = ..., add_key_data: _Optional[_Union[SecDNSKeyData, _Mapping]] = ..., all: bool = ..., rem_ds_data: _Optional[_Union[SecDNSDSData, _Mapping]] = ..., rem_key_data: _Optional[_Union[SecDNSKeyData, _Mapping]] = ...) -> None: ...

class VerisignWhoisInfo(_message.Message):
    __slots__ = ["iris_server", "registrar", "url", "whois_server"]
    IRIS_SERVER_FIELD_NUMBER: _ClassVar[int]
    REGISTRAR_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    WHOIS_SERVER_FIELD_NUMBER: _ClassVar[int]
    iris_server: _wrappers_pb2.StringValue
    registrar: str
    url: _wrappers_pb2.StringValue
    whois_server: _wrappers_pb2.StringValue
    def __init__(self, registrar: _Optional[str] = ..., whois_server: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., url: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., iris_server: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainHostsType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
