from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

BillCustomer: BillType
BillRegistrar: BillType
DESCRIPTOR: _descriptor.FileDescriptor
Invalid: DataQualityStatus
NoLongerRequired: RegistrationStatus
RegisteredUntilExpiry: RegistrationStatus
RenewalRequired: RegistrationStatus
Unspecified: BillType
Valid: DataQualityStatus

class DataQuality(_message.Message):
    __slots__ = ["date_commenced", "date_to_suspend", "domains", "lock_applied", "reason", "status"]
    DATE_COMMENCED_FIELD_NUMBER: _ClassVar[int]
    DATE_TO_SUSPEND_FIELD_NUMBER: _ClassVar[int]
    DOMAINS_FIELD_NUMBER: _ClassVar[int]
    LOCK_APPLIED_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    date_commenced: _timestamp_pb2.Timestamp
    date_to_suspend: _timestamp_pb2.Timestamp
    domains: _containers.RepeatedScalarFieldContainer[str]
    lock_applied: _wrappers_pb2.BoolValue
    reason: _wrappers_pb2.StringValue
    status: DataQualityStatus
    def __init__(self, status: _Optional[_Union[DataQualityStatus, str]] = ..., reason: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., date_commenced: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., date_to_suspend: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., lock_applied: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., domains: _Optional[_Iterable[str]] = ...) -> None: ...

class DomainCheckInfo(_message.Message):
    __slots__ = ["abuse_limit"]
    ABUSE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    abuse_limit: int
    def __init__(self, abuse_limit: _Optional[int] = ...) -> None: ...

class DomainCreate(_message.Message):
    __slots__ = ["auto_bill", "auto_period", "first_bill", "next_bill", "next_period", "notes", "recur_bill", "reseller"]
    AUTO_BILL_FIELD_NUMBER: _ClassVar[int]
    AUTO_PERIOD_FIELD_NUMBER: _ClassVar[int]
    FIRST_BILL_FIELD_NUMBER: _ClassVar[int]
    NEXT_BILL_FIELD_NUMBER: _ClassVar[int]
    NEXT_PERIOD_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    RECUR_BILL_FIELD_NUMBER: _ClassVar[int]
    RESELLER_FIELD_NUMBER: _ClassVar[int]
    auto_bill: _wrappers_pb2.UInt32Value
    auto_period: _wrappers_pb2.UInt32Value
    first_bill: BillType
    next_bill: _wrappers_pb2.UInt32Value
    next_period: _wrappers_pb2.UInt32Value
    notes: _containers.RepeatedScalarFieldContainer[str]
    recur_bill: BillType
    reseller: _wrappers_pb2.StringValue
    def __init__(self, first_bill: _Optional[_Union[BillType, str]] = ..., recur_bill: _Optional[_Union[BillType, str]] = ..., auto_bill: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., next_bill: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., auto_period: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., next_period: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., notes: _Optional[_Iterable[str]] = ..., reseller: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainInfo(_message.Message):
    __slots__ = ["auto_bill", "auto_period", "first_bill", "next_bill", "next_period", "notes", "recur_bill", "registration_status", "renewal_not_required", "reseller"]
    AUTO_BILL_FIELD_NUMBER: _ClassVar[int]
    AUTO_PERIOD_FIELD_NUMBER: _ClassVar[int]
    FIRST_BILL_FIELD_NUMBER: _ClassVar[int]
    NEXT_BILL_FIELD_NUMBER: _ClassVar[int]
    NEXT_PERIOD_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    RECUR_BILL_FIELD_NUMBER: _ClassVar[int]
    REGISTRATION_STATUS_FIELD_NUMBER: _ClassVar[int]
    RENEWAL_NOT_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    RESELLER_FIELD_NUMBER: _ClassVar[int]
    auto_bill: _wrappers_pb2.UInt32Value
    auto_period: _wrappers_pb2.UInt32Value
    first_bill: BillType
    next_bill: _wrappers_pb2.UInt32Value
    next_period: _wrappers_pb2.UInt32Value
    notes: _containers.RepeatedScalarFieldContainer[str]
    recur_bill: BillType
    registration_status: RegistrationStatus
    renewal_not_required: bool
    reseller: _wrappers_pb2.StringValue
    def __init__(self, registration_status: _Optional[_Union[RegistrationStatus, str]] = ..., first_bill: _Optional[_Union[BillType, str]] = ..., recur_bill: _Optional[_Union[BillType, str]] = ..., auto_bill: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., next_bill: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., auto_period: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., next_period: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., renewal_not_required: bool = ..., notes: _Optional[_Iterable[str]] = ..., reseller: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainUpdate(_message.Message):
    __slots__ = ["auto_bill", "auto_period", "first_bill", "next_bill", "next_period", "notes", "recur_bill", "renewal_not_required", "reseller"]
    AUTO_BILL_FIELD_NUMBER: _ClassVar[int]
    AUTO_PERIOD_FIELD_NUMBER: _ClassVar[int]
    FIRST_BILL_FIELD_NUMBER: _ClassVar[int]
    NEXT_BILL_FIELD_NUMBER: _ClassVar[int]
    NEXT_PERIOD_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    RECUR_BILL_FIELD_NUMBER: _ClassVar[int]
    RENEWAL_NOT_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    RESELLER_FIELD_NUMBER: _ClassVar[int]
    auto_bill: _wrappers_pb2.UInt32Value
    auto_period: _wrappers_pb2.UInt32Value
    first_bill: BillType
    next_bill: _wrappers_pb2.UInt32Value
    next_period: _wrappers_pb2.UInt32Value
    notes: _containers.RepeatedScalarFieldContainer[str]
    recur_bill: BillType
    renewal_not_required: bool
    reseller: _wrappers_pb2.StringValue
    def __init__(self, first_bill: _Optional[_Union[BillType, str]] = ..., recur_bill: _Optional[_Union[BillType, str]] = ..., auto_bill: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., next_bill: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., auto_period: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., next_period: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., renewal_not_required: bool = ..., notes: _Optional[_Iterable[str]] = ..., reseller: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class BillType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class RegistrationStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DataQualityStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
