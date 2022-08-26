from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.api import annotations_pb2 as _annotations_pb2
from contact import contact_pb2 as _contact_pb2
from domain import domain_pb2 as _domain_pb2
from host import host_pb2 as _host_pb2
from rgp import rgp_pb2 as _rgp_pb2
from nominet import nominet_pb2 as _nominet_pb2
from traficom import traficom_pb2 as _traficom_pb2
from maintenance import maintenance_pb2 as _maintenance_pb2
from eurid import eurid_pb2 as _eurid_pb2
from tmch import tmch_pb2 as _tmch_pb2
from dac import dac_pb2 as _dac_pb2
from common import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BalanceReply(_message.Message):
    __slots__ = ["available_credit", "balance", "cmd_resp", "credit_limit", "currency", "fixed_credit_threshold", "percentage_credit_threshold"]
    AVAILABLE_CREDIT_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CREDIT_LIMIT_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    FIXED_CREDIT_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_CREDIT_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    available_credit: _wrappers_pb2.StringValue
    balance: str
    cmd_resp: _common_pb2.CommandResponse
    credit_limit: _wrappers_pb2.StringValue
    currency: str
    fixed_credit_threshold: _wrappers_pb2.StringValue
    percentage_credit_threshold: _wrappers_pb2.UInt32Value
    def __init__(self, balance: _Optional[str] = ..., currency: _Optional[str] = ..., credit_limit: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., available_credit: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., fixed_credit_threshold: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., percentage_credit_threshold: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class ChangeData(_message.Message):
    __slots__ = ["case_id", "change_state", "date", "operation", "reason", "server_transaction_id", "who"]
    class ChangeState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class CaseID(_message.Message):
        __slots__ = ["case_id", "case_id_type", "name"]
        class CaseIDType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = []
        CASE_ID_FIELD_NUMBER: _ClassVar[int]
        CASE_ID_TYPE_FIELD_NUMBER: _ClassVar[int]
        Custom: ChangeData.CaseID.CaseIDType
        NAME_FIELD_NUMBER: _ClassVar[int]
        UDRP: ChangeData.CaseID.CaseIDType
        URS: ChangeData.CaseID.CaseIDType
        case_id: str
        case_id_type: ChangeData.CaseID.CaseIDType
        name: _wrappers_pb2.StringValue
        def __init__(self, case_id_type: _Optional[_Union[ChangeData.CaseID.CaseIDType, str]] = ..., name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., case_id: _Optional[str] = ...) -> None: ...
    class ChangeOperation(_message.Message):
        __slots__ = ["operation", "operation_type"]
        class ChangeOperationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = []
        AutoDelete: ChangeData.ChangeOperation.ChangeOperationType
        AutoPurge: ChangeData.ChangeOperation.ChangeOperationType
        AutoRenew: ChangeData.ChangeOperation.ChangeOperationType
        Create: ChangeData.ChangeOperation.ChangeOperationType
        Custom: ChangeData.ChangeOperation.ChangeOperationType
        Delete: ChangeData.ChangeOperation.ChangeOperationType
        OPERATION_FIELD_NUMBER: _ClassVar[int]
        OPERATION_TYPE_FIELD_NUMBER: _ClassVar[int]
        Renew: ChangeData.ChangeOperation.ChangeOperationType
        Restore: ChangeData.ChangeOperation.ChangeOperationType
        Transfer: ChangeData.ChangeOperation.ChangeOperationType
        Update: ChangeData.ChangeOperation.ChangeOperationType
        operation: _wrappers_pb2.StringValue
        operation_type: ChangeData.ChangeOperation.ChangeOperationType
        def __init__(self, operation_type: _Optional[_Union[ChangeData.ChangeOperation.ChangeOperationType, str]] = ..., operation: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...
    AFTER: ChangeData.ChangeState
    BEFORE: ChangeData.ChangeState
    CASE_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGE_STATE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    SERVER_TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    WHO_FIELD_NUMBER: _ClassVar[int]
    case_id: ChangeData.CaseID
    change_state: ChangeData.ChangeState
    date: _timestamp_pb2.Timestamp
    operation: ChangeData.ChangeOperation
    reason: _wrappers_pb2.StringValue
    server_transaction_id: str
    who: str
    def __init__(self, change_state: _Optional[_Union[ChangeData.ChangeState, str]] = ..., operation: _Optional[_Union[ChangeData.ChangeOperation, _Mapping]] = ..., date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., server_transaction_id: _Optional[str] = ..., who: _Optional[str] = ..., case_id: _Optional[_Union[ChangeData.CaseID, _Mapping]] = ..., reason: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class PollAck(_message.Message):
    __slots__ = ["msg_id"]
    MSG_ID_FIELD_NUMBER: _ClassVar[int]
    msg_id: str
    def __init__(self, msg_id: _Optional[str] = ...) -> None: ...

class PollReply(_message.Message):
    __slots__ = ["change_data", "cmd_resp", "contact_info", "contact_pan", "contact_transfer", "domain_create", "domain_info", "domain_pan", "domain_renew", "domain_transfer", "enqueue_date", "eurid_poll", "host_info", "maintenance_info", "message", "msg_id", "nominet_domain_cancel", "nominet_domain_fail", "nominet_domain_registrar_change", "nominet_domain_release", "nominet_host_cancel", "nominet_process", "nominet_registrant_transfer", "nominet_suspend", "traficom_trn", "verisign_low_balance"]
    CHANGE_DATA_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CONTACT_INFO_FIELD_NUMBER: _ClassVar[int]
    CONTACT_PAN_FIELD_NUMBER: _ClassVar[int]
    CONTACT_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_CREATE_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_INFO_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_PAN_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_RENEW_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    ENQUEUE_DATE_FIELD_NUMBER: _ClassVar[int]
    EURID_POLL_FIELD_NUMBER: _ClassVar[int]
    HOST_INFO_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_INFO_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MSG_ID_FIELD_NUMBER: _ClassVar[int]
    NOMINET_DOMAIN_CANCEL_FIELD_NUMBER: _ClassVar[int]
    NOMINET_DOMAIN_FAIL_FIELD_NUMBER: _ClassVar[int]
    NOMINET_DOMAIN_REGISTRAR_CHANGE_FIELD_NUMBER: _ClassVar[int]
    NOMINET_DOMAIN_RELEASE_FIELD_NUMBER: _ClassVar[int]
    NOMINET_HOST_CANCEL_FIELD_NUMBER: _ClassVar[int]
    NOMINET_PROCESS_FIELD_NUMBER: _ClassVar[int]
    NOMINET_REGISTRANT_TRANSFER_FIELD_NUMBER: _ClassVar[int]
    NOMINET_SUSPEND_FIELD_NUMBER: _ClassVar[int]
    TRAFICOM_TRN_FIELD_NUMBER: _ClassVar[int]
    VERISIGN_LOW_BALANCE_FIELD_NUMBER: _ClassVar[int]
    change_data: ChangeData
    cmd_resp: _common_pb2.CommandResponse
    contact_info: _contact_pb2.ContactInfoReply
    contact_pan: _contact_pb2.ContactPANReply
    contact_transfer: _contact_pb2.ContactTransferReply
    domain_create: _domain_pb2.DomainCreateReply
    domain_info: _domain_pb2.DomainInfoReply
    domain_pan: _domain_pb2.DomainPANReply
    domain_renew: _domain_pb2.DomainRenewReply
    domain_transfer: _domain_pb2.DomainTransferReply
    enqueue_date: _timestamp_pb2.Timestamp
    eurid_poll: _eurid_pb2.PollReply
    host_info: _host_pb2.HostInfoReply
    maintenance_info: _maintenance_pb2.MaintenanceInfoReply
    message: str
    msg_id: str
    nominet_domain_cancel: _nominet_pb2.DomainCancel
    nominet_domain_fail: _nominet_pb2.DomainFail
    nominet_domain_registrar_change: _nominet_pb2.DomainRegistrarChange
    nominet_domain_release: _nominet_pb2.DomainRelease
    nominet_host_cancel: _nominet_pb2.HostCancel
    nominet_process: _nominet_pb2.Process
    nominet_registrant_transfer: _nominet_pb2.RegistrantTransfer
    nominet_suspend: _nominet_pb2.Suspend
    traficom_trn: _traficom_pb2.TrnData
    verisign_low_balance: BalanceReply
    def __init__(self, msg_id: _Optional[str] = ..., enqueue_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., message: _Optional[str] = ..., domain_info: _Optional[_Union[_domain_pb2.DomainInfoReply, _Mapping]] = ..., domain_transfer: _Optional[_Union[_domain_pb2.DomainTransferReply, _Mapping]] = ..., domain_create: _Optional[_Union[_domain_pb2.DomainCreateReply, _Mapping]] = ..., domain_renew: _Optional[_Union[_domain_pb2.DomainRenewReply, _Mapping]] = ..., domain_pan: _Optional[_Union[_domain_pb2.DomainPANReply, _Mapping]] = ..., contact_info: _Optional[_Union[_contact_pb2.ContactInfoReply, _Mapping]] = ..., contact_transfer: _Optional[_Union[_contact_pb2.ContactTransferReply, _Mapping]] = ..., contact_pan: _Optional[_Union[_contact_pb2.ContactPANReply, _Mapping]] = ..., nominet_domain_cancel: _Optional[_Union[_nominet_pb2.DomainCancel, _Mapping]] = ..., nominet_domain_release: _Optional[_Union[_nominet_pb2.DomainRelease, _Mapping]] = ..., nominet_domain_registrar_change: _Optional[_Union[_nominet_pb2.DomainRegistrarChange, _Mapping]] = ..., nominet_host_cancel: _Optional[_Union[_nominet_pb2.HostCancel, _Mapping]] = ..., nominet_process: _Optional[_Union[_nominet_pb2.Process, _Mapping]] = ..., nominet_suspend: _Optional[_Union[_nominet_pb2.Suspend, _Mapping]] = ..., nominet_domain_fail: _Optional[_Union[_nominet_pb2.DomainFail, _Mapping]] = ..., nominet_registrant_transfer: _Optional[_Union[_nominet_pb2.RegistrantTransfer, _Mapping]] = ..., traficom_trn: _Optional[_Union[_traficom_pb2.TrnData, _Mapping]] = ..., verisign_low_balance: _Optional[_Union[BalanceReply, _Mapping]] = ..., maintenance_info: _Optional[_Union[_maintenance_pb2.MaintenanceInfoReply, _Mapping]] = ..., eurid_poll: _Optional[_Union[_eurid_pb2.PollReply, _Mapping]] = ..., host_info: _Optional[_Union[_host_pb2.HostInfoReply, _Mapping]] = ..., change_data: _Optional[_Union[ChangeData, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class RegistryInfo(_message.Message):
    __slots__ = ["registry_name"]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    registry_name: str
    def __init__(self, registry_name: _Optional[str] = ...) -> None: ...
