"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.timestamp_pb2
import google.protobuf.wrappers_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _BillType:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _BillTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_BillType.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    Unspecified: _BillType.ValueType  # 0
    BillRegistrar: _BillType.ValueType  # 1
    BillCustomer: _BillType.ValueType  # 2

class BillType(_BillType, metaclass=_BillTypeEnumTypeWrapper): ...

Unspecified: BillType.ValueType  # 0
BillRegistrar: BillType.ValueType  # 1
BillCustomer: BillType.ValueType  # 2
global___BillType = BillType

class _RegistrationStatus:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _RegistrationStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_RegistrationStatus.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    RegisteredUntilExpiry: _RegistrationStatus.ValueType  # 0
    RenewalRequired: _RegistrationStatus.ValueType  # 1
    NoLongerRequired: _RegistrationStatus.ValueType  # 2

class RegistrationStatus(_RegistrationStatus, metaclass=_RegistrationStatusEnumTypeWrapper): ...

RegisteredUntilExpiry: RegistrationStatus.ValueType  # 0
RenewalRequired: RegistrationStatus.ValueType  # 1
NoLongerRequired: RegistrationStatus.ValueType  # 2
global___RegistrationStatus = RegistrationStatus

class _DataQualityStatus:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _DataQualityStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_DataQualityStatus.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    Invalid: _DataQualityStatus.ValueType  # 0
    Valid: _DataQualityStatus.ValueType  # 1

class DataQualityStatus(_DataQualityStatus, metaclass=_DataQualityStatusEnumTypeWrapper): ...

Invalid: DataQualityStatus.ValueType  # 0
Valid: DataQualityStatus.ValueType  # 1
global___DataQualityStatus = DataQualityStatus

@typing_extensions.final
class DomainCreate(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    FIRST_BILL_FIELD_NUMBER: builtins.int
    RECUR_BILL_FIELD_NUMBER: builtins.int
    AUTO_BILL_FIELD_NUMBER: builtins.int
    NEXT_BILL_FIELD_NUMBER: builtins.int
    AUTO_PERIOD_FIELD_NUMBER: builtins.int
    NEXT_PERIOD_FIELD_NUMBER: builtins.int
    NOTES_FIELD_NUMBER: builtins.int
    RESELLER_FIELD_NUMBER: builtins.int
    first_bill: global___BillType.ValueType
    recur_bill: global___BillType.ValueType
    @property
    def auto_bill(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def next_bill(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def auto_period(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def next_period(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def notes(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    @property
    def reseller(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        first_bill: global___BillType.ValueType = ...,
        recur_bill: global___BillType.ValueType = ...,
        auto_bill: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        next_bill: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        auto_period: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        next_period: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        notes: collections.abc.Iterable[builtins.str] | None = ...,
        reseller: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["auto_bill", b"auto_bill", "auto_period", b"auto_period", "next_bill", b"next_bill", "next_period", b"next_period", "reseller", b"reseller"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["auto_bill", b"auto_bill", "auto_period", b"auto_period", "first_bill", b"first_bill", "next_bill", b"next_bill", "next_period", b"next_period", "notes", b"notes", "recur_bill", b"recur_bill", "reseller", b"reseller"]) -> None: ...

global___DomainCreate = DomainCreate

@typing_extensions.final
class DomainUpdate(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    FIRST_BILL_FIELD_NUMBER: builtins.int
    RECUR_BILL_FIELD_NUMBER: builtins.int
    AUTO_BILL_FIELD_NUMBER: builtins.int
    NEXT_BILL_FIELD_NUMBER: builtins.int
    AUTO_PERIOD_FIELD_NUMBER: builtins.int
    NEXT_PERIOD_FIELD_NUMBER: builtins.int
    RENEWAL_NOT_REQUIRED_FIELD_NUMBER: builtins.int
    NOTES_FIELD_NUMBER: builtins.int
    RESELLER_FIELD_NUMBER: builtins.int
    first_bill: global___BillType.ValueType
    recur_bill: global___BillType.ValueType
    @property
    def auto_bill(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def next_bill(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def auto_period(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def next_period(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def renewal_not_required(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
    @property
    def notes(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    @property
    def reseller(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        first_bill: global___BillType.ValueType = ...,
        recur_bill: global___BillType.ValueType = ...,
        auto_bill: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        next_bill: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        auto_period: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        next_period: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        renewal_not_required: google.protobuf.wrappers_pb2.BoolValue | None = ...,
        notes: collections.abc.Iterable[builtins.str] | None = ...,
        reseller: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["auto_bill", b"auto_bill", "auto_period", b"auto_period", "next_bill", b"next_bill", "next_period", b"next_period", "renewal_not_required", b"renewal_not_required", "reseller", b"reseller"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["auto_bill", b"auto_bill", "auto_period", b"auto_period", "first_bill", b"first_bill", "next_bill", b"next_bill", "next_period", b"next_period", "notes", b"notes", "recur_bill", b"recur_bill", "renewal_not_required", b"renewal_not_required", "reseller", b"reseller"]) -> None: ...

global___DomainUpdate = DomainUpdate

@typing_extensions.final
class DomainCheckInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ABUSE_LIMIT_FIELD_NUMBER: builtins.int
    abuse_limit: builtins.int
    def __init__(
        self,
        *,
        abuse_limit: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["abuse_limit", b"abuse_limit"]) -> None: ...

global___DomainCheckInfo = DomainCheckInfo

@typing_extensions.final
class DomainInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    REGISTRATION_STATUS_FIELD_NUMBER: builtins.int
    FIRST_BILL_FIELD_NUMBER: builtins.int
    RECUR_BILL_FIELD_NUMBER: builtins.int
    AUTO_BILL_FIELD_NUMBER: builtins.int
    NEXT_BILL_FIELD_NUMBER: builtins.int
    AUTO_PERIOD_FIELD_NUMBER: builtins.int
    NEXT_PERIOD_FIELD_NUMBER: builtins.int
    RENEWAL_NOT_REQUIRED_FIELD_NUMBER: builtins.int
    NOTES_FIELD_NUMBER: builtins.int
    RESELLER_FIELD_NUMBER: builtins.int
    registration_status: global___RegistrationStatus.ValueType
    first_bill: global___BillType.ValueType
    recur_bill: global___BillType.ValueType
    @property
    def auto_bill(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def next_bill(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def auto_period(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    @property
    def next_period(self) -> google.protobuf.wrappers_pb2.UInt32Value: ...
    renewal_not_required: builtins.bool
    @property
    def notes(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    @property
    def reseller(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        registration_status: global___RegistrationStatus.ValueType = ...,
        first_bill: global___BillType.ValueType = ...,
        recur_bill: global___BillType.ValueType = ...,
        auto_bill: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        next_bill: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        auto_period: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        next_period: google.protobuf.wrappers_pb2.UInt32Value | None = ...,
        renewal_not_required: builtins.bool = ...,
        notes: collections.abc.Iterable[builtins.str] | None = ...,
        reseller: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["auto_bill", b"auto_bill", "auto_period", b"auto_period", "next_bill", b"next_bill", "next_period", b"next_period", "reseller", b"reseller"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["auto_bill", b"auto_bill", "auto_period", b"auto_period", "first_bill", b"first_bill", "next_bill", b"next_bill", "next_period", b"next_period", "notes", b"notes", "recur_bill", b"recur_bill", "registration_status", b"registration_status", "renewal_not_required", b"renewal_not_required", "reseller", b"reseller"]) -> None: ...

global___DomainInfo = DomainInfo

@typing_extensions.final
class DataQuality(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    STATUS_FIELD_NUMBER: builtins.int
    REASON_FIELD_NUMBER: builtins.int
    DATE_COMMENCED_FIELD_NUMBER: builtins.int
    DATE_TO_SUSPEND_FIELD_NUMBER: builtins.int
    LOCK_APPLIED_FIELD_NUMBER: builtins.int
    DOMAINS_FIELD_NUMBER: builtins.int
    status: global___DataQualityStatus.ValueType
    @property
    def reason(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def date_commenced(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    @property
    def date_to_suspend(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    @property
    def lock_applied(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
    @property
    def domains(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    def __init__(
        self,
        *,
        status: global___DataQualityStatus.ValueType = ...,
        reason: google.protobuf.wrappers_pb2.StringValue | None = ...,
        date_commenced: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        date_to_suspend: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        lock_applied: google.protobuf.wrappers_pb2.BoolValue | None = ...,
        domains: collections.abc.Iterable[builtins.str] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["date_commenced", b"date_commenced", "date_to_suspend", b"date_to_suspend", "lock_applied", b"lock_applied", "reason", b"reason"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["date_commenced", b"date_commenced", "date_to_suspend", b"date_to_suspend", "domains", b"domains", "lock_applied", b"lock_applied", "reason", b"reason", "status", b"status"]) -> None: ...

global___DataQuality = DataQuality
