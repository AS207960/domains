from google.protobuf import wrappers_pb2 as _wrappers_pb2
from common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

Check: Command
Create: Command
Custom: Command
DESCRIPTOR: _descriptor.FileDescriptor
Delayed: Applied
Delete: Command
Immediate: Applied
Info: Command
Renew: Command
Restore: Command
Transfer: Command
Unspecified: Applied
Update: Command

class Credit(_message.Message):
    __slots__ = ["description", "value"]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    description: _wrappers_pb2.StringValue
    value: str
    def __init__(self, value: _Optional[str] = ..., description: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DonutsAmount(_message.Message):
    __slots__ = ["command", "name", "value"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    command: Command
    name: _wrappers_pb2.StringValue
    value: str
    def __init__(self, value: _Optional[str] = ..., name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., command: _Optional[_Union[Command, str]] = ...) -> None: ...

class DonutsCategory(_message.Message):
    __slots__ = ["name", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: _wrappers_pb2.StringValue
    value: str
    def __init__(self, value: _Optional[str] = ..., name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DonutsFeeData(_message.Message):
    __slots__ = ["fees"]
    FEES_FIELD_NUMBER: _ClassVar[int]
    fees: _containers.RepeatedCompositeFieldContainer[DonutsFeeSet]
    def __init__(self, fees: _Optional[_Iterable[_Union[DonutsFeeSet, _Mapping]]] = ...) -> None: ...

class DonutsFeeSet(_message.Message):
    __slots__ = ["category", "fee_type", "fees"]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    FEES_FIELD_NUMBER: _ClassVar[int]
    FEE_TYPE_FIELD_NUMBER: _ClassVar[int]
    category: DonutsCategory
    fee_type: DonutsFeeType
    fees: _containers.RepeatedCompositeFieldContainer[DonutsAmount]
    def __init__(self, fees: _Optional[_Iterable[_Union[DonutsAmount, _Mapping]]] = ..., fee_type: _Optional[_Union[DonutsFeeType, _Mapping]] = ..., category: _Optional[_Union[DonutsCategory, _Mapping]] = ...) -> None: ...

class DonutsFeeType(_message.Message):
    __slots__ = ["fee_type", "name"]
    class FeeTypes(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    Custom: DonutsFeeType.FeeTypes
    FEE_TYPE_FIELD_NUMBER: _ClassVar[int]
    Fee: DonutsFeeType.FeeTypes
    NAME_FIELD_NUMBER: _ClassVar[int]
    Price: DonutsFeeType.FeeTypes
    fee_type: DonutsFeeType.FeeTypes
    name: _wrappers_pb2.StringValue
    def __init__(self, fee_type: _Optional[_Union[DonutsFeeType.FeeTypes, str]] = ..., name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class Fee(_message.Message):
    __slots__ = ["applied", "description", "grace_period", "refundable", "value"]
    APPLIED_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GRACE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    REFUNDABLE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    applied: Applied
    description: _wrappers_pb2.StringValue
    grace_period: _wrappers_pb2.StringValue
    refundable: _wrappers_pb2.BoolValue
    value: str
    def __init__(self, value: _Optional[str] = ..., description: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., refundable: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., grace_period: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., applied: _Optional[_Union[Applied, str]] = ...) -> None: ...

class FeeAgreement(_message.Message):
    __slots__ = ["currency", "fees"]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    FEES_FIELD_NUMBER: _ClassVar[int]
    currency: _wrappers_pb2.StringValue
    fees: _containers.RepeatedCompositeFieldContainer[Fee]
    def __init__(self, currency: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., fees: _Optional[_Iterable[_Union[Fee, _Mapping]]] = ...) -> None: ...

class FeeCheck(_message.Message):
    __slots__ = ["commands", "currency"]
    COMMANDS_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    commands: _containers.RepeatedCompositeFieldContainer[FeeCommand]
    currency: _wrappers_pb2.StringValue
    def __init__(self, currency: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., commands: _Optional[_Iterable[_Union[FeeCommand, _Mapping]]] = ...) -> None: ...

class FeeCheckData(_message.Message):
    __slots__ = ["available", "commands", "reason"]
    class FeeCommand(_message.Message):
        __slots__ = ["command", "credits", "currency", "fees", "period", "reason", "standard"]
        CLASS_FIELD_NUMBER: _ClassVar[int]
        COMMAND_FIELD_NUMBER: _ClassVar[int]
        CREDITS_FIELD_NUMBER: _ClassVar[int]
        CURRENCY_FIELD_NUMBER: _ClassVar[int]
        FEES_FIELD_NUMBER: _ClassVar[int]
        PERIOD_FIELD_NUMBER: _ClassVar[int]
        REASON_FIELD_NUMBER: _ClassVar[int]
        STANDARD_FIELD_NUMBER: _ClassVar[int]
        command: Command
        credits: _containers.RepeatedCompositeFieldContainer[Credit]
        currency: str
        fees: _containers.RepeatedCompositeFieldContainer[Fee]
        period: _common_pb2.Period
        reason: _wrappers_pb2.StringValue
        standard: _wrappers_pb2.BoolValue
        def __init__(self, command: _Optional[_Union[Command, str]] = ..., standard: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., period: _Optional[_Union[_common_pb2.Period, _Mapping]] = ..., currency: _Optional[str] = ..., fees: _Optional[_Iterable[_Union[Fee, _Mapping]]] = ..., credits: _Optional[_Iterable[_Union[Credit, _Mapping]]] = ..., reason: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., **kwargs) -> None: ...
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    COMMANDS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    available: bool
    commands: _containers.RepeatedCompositeFieldContainer[FeeCheckData.FeeCommand]
    reason: _wrappers_pb2.StringValue
    def __init__(self, available: bool = ..., commands: _Optional[_Iterable[_Union[FeeCheckData.FeeCommand, _Mapping]]] = ..., reason: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class FeeCommand(_message.Message):
    __slots__ = ["command", "period"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    command: Command
    period: _common_pb2.Period
    def __init__(self, command: _Optional[_Union[Command, str]] = ..., period: _Optional[_Union[_common_pb2.Period, _Mapping]] = ...) -> None: ...

class FeeData(_message.Message):
    __slots__ = ["balance", "credit_limit", "credits", "currency", "fees", "period"]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    CREDITS_FIELD_NUMBER: _ClassVar[int]
    CREDIT_LIMIT_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    FEES_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    balance: _wrappers_pb2.StringValue
    credit_limit: _wrappers_pb2.StringValue
    credits: _containers.RepeatedCompositeFieldContainer[Credit]
    currency: str
    fees: _containers.RepeatedCompositeFieldContainer[Fee]
    period: _common_pb2.Period
    def __init__(self, currency: _Optional[str] = ..., period: _Optional[_Union[_common_pb2.Period, _Mapping]] = ..., fees: _Optional[_Iterable[_Union[Fee, _Mapping]]] = ..., credits: _Optional[_Iterable[_Union[Credit, _Mapping]]] = ..., balance: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., credit_limit: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class Command(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Applied(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
