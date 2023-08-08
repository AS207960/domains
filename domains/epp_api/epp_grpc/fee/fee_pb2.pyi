"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import common.common_pb2
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.wrappers_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _Command:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _CommandEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_Command.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    Create: _Command.ValueType  # 0
    Renew: _Command.ValueType  # 1
    Transfer: _Command.ValueType  # 2
    Delete: _Command.ValueType  # 4
    Restore: _Command.ValueType  # 3
    Update: _Command.ValueType  # 5
    Check: _Command.ValueType  # 6
    Info: _Command.ValueType  # 7
    Custom: _Command.ValueType  # 8

class Command(_Command, metaclass=_CommandEnumTypeWrapper): ...

Create: Command.ValueType  # 0
Renew: Command.ValueType  # 1
Transfer: Command.ValueType  # 2
Delete: Command.ValueType  # 4
Restore: Command.ValueType  # 3
Update: Command.ValueType  # 5
Check: Command.ValueType  # 6
Info: Command.ValueType  # 7
Custom: Command.ValueType  # 8
global___Command = Command

class _Applied:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _AppliedEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_Applied.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    Immediate: _Applied.ValueType  # 0
    Delayed: _Applied.ValueType  # 1
    Unspecified: _Applied.ValueType  # 2

class Applied(_Applied, metaclass=_AppliedEnumTypeWrapper): ...

Immediate: Applied.ValueType  # 0
Delayed: Applied.ValueType  # 1
Unspecified: Applied.ValueType  # 2
global___Applied = Applied

@typing_extensions.final
class Fee(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    VALUE_FIELD_NUMBER: builtins.int
    DESCRIPTION_FIELD_NUMBER: builtins.int
    REFUNDABLE_FIELD_NUMBER: builtins.int
    GRACE_PERIOD_FIELD_NUMBER: builtins.int
    APPLIED_FIELD_NUMBER: builtins.int
    value: builtins.str
    @property
    def description(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def refundable(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
    @property
    def grace_period(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    applied: global___Applied.ValueType
    def __init__(
        self,
        *,
        value: builtins.str = ...,
        description: google.protobuf.wrappers_pb2.StringValue | None = ...,
        refundable: google.protobuf.wrappers_pb2.BoolValue | None = ...,
        grace_period: google.protobuf.wrappers_pb2.StringValue | None = ...,
        applied: global___Applied.ValueType = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["description", b"description", "grace_period", b"grace_period", "refundable", b"refundable"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["applied", b"applied", "description", b"description", "grace_period", b"grace_period", "refundable", b"refundable", "value", b"value"]) -> None: ...

global___Fee = Fee

@typing_extensions.final
class Credit(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    VALUE_FIELD_NUMBER: builtins.int
    DESCRIPTION_FIELD_NUMBER: builtins.int
    value: builtins.str
    @property
    def description(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        value: builtins.str = ...,
        description: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["description", b"description"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["description", b"description", "value", b"value"]) -> None: ...

global___Credit = Credit

@typing_extensions.final
class FeeCheck(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CURRENCY_FIELD_NUMBER: builtins.int
    COMMANDS_FIELD_NUMBER: builtins.int
    @property
    def currency(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def commands(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___FeeCommand]: ...
    def __init__(
        self,
        *,
        currency: google.protobuf.wrappers_pb2.StringValue | None = ...,
        commands: collections.abc.Iterable[global___FeeCommand] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["currency", b"currency"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["commands", b"commands", "currency", b"currency"]) -> None: ...

global___FeeCheck = FeeCheck

@typing_extensions.final
class FeeAgreement(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CURRENCY_FIELD_NUMBER: builtins.int
    FEES_FIELD_NUMBER: builtins.int
    @property
    def currency(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def fees(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Fee]: ...
    def __init__(
        self,
        *,
        currency: google.protobuf.wrappers_pb2.StringValue | None = ...,
        fees: collections.abc.Iterable[global___Fee] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["currency", b"currency"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["currency", b"currency", "fees", b"fees"]) -> None: ...

global___FeeAgreement = FeeAgreement

@typing_extensions.final
class FeeCommand(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    COMMAND_FIELD_NUMBER: builtins.int
    PERIOD_FIELD_NUMBER: builtins.int
    CUSTOM_NAME_FIELD_NUMBER: builtins.int
    PHASE_FIELD_NUMBER: builtins.int
    SUB_PHASE_FIELD_NUMBER: builtins.int
    command: global___Command.ValueType
    @property
    def period(self) -> common.common_pb2.Period: ...
    @property
    def custom_name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def phase(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def sub_phase(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        command: global___Command.ValueType = ...,
        period: common.common_pb2.Period | None = ...,
        custom_name: google.protobuf.wrappers_pb2.StringValue | None = ...,
        phase: google.protobuf.wrappers_pb2.StringValue | None = ...,
        sub_phase: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["custom_name", b"custom_name", "period", b"period", "phase", b"phase", "sub_phase", b"sub_phase"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["command", b"command", "custom_name", b"custom_name", "period", b"period", "phase", b"phase", "sub_phase", b"sub_phase"]) -> None: ...

global___FeeCommand = FeeCommand

@typing_extensions.final
class FeeCheckData(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class FeeCommand(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        COMMAND_FIELD_NUMBER: builtins.int
        STANDARD_FIELD_NUMBER: builtins.int
        PERIOD_FIELD_NUMBER: builtins.int
        CURRENCY_FIELD_NUMBER: builtins.int
        FEES_FIELD_NUMBER: builtins.int
        CREDITS_FIELD_NUMBER: builtins.int
        CLASS_FIELD_NUMBER: builtins.int
        REASON_FIELD_NUMBER: builtins.int
        command: global___Command.ValueType
        @property
        def standard(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
        @property
        def period(self) -> common.common_pb2.Period: ...
        currency: builtins.str
        @property
        def fees(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Fee]: ...
        @property
        def credits(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Credit]: ...
        @property
        def reason(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        def __init__(
            self,
            *,
            command: global___Command.ValueType = ...,
            standard: google.protobuf.wrappers_pb2.BoolValue | None = ...,
            period: common.common_pb2.Period | None = ...,
            currency: builtins.str = ...,
            fees: collections.abc.Iterable[global___Fee] | None = ...,
            credits: collections.abc.Iterable[global___Credit] | None = ...,
            reason: google.protobuf.wrappers_pb2.StringValue | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["class", b"class", "period", b"period", "reason", b"reason", "standard", b"standard"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["class", b"class", "command", b"command", "credits", b"credits", "currency", b"currency", "fees", b"fees", "period", b"period", "reason", b"reason", "standard", b"standard"]) -> None: ...

    AVAILABLE_FIELD_NUMBER: builtins.int
    COMMANDS_FIELD_NUMBER: builtins.int
    REASON_FIELD_NUMBER: builtins.int
    available: builtins.bool
    @property
    def commands(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___FeeCheckData.FeeCommand]: ...
    @property
    def reason(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        available: builtins.bool = ...,
        commands: collections.abc.Iterable[global___FeeCheckData.FeeCommand] | None = ...,
        reason: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["reason", b"reason"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["available", b"available", "commands", b"commands", "reason", b"reason"]) -> None: ...

global___FeeCheckData = FeeCheckData

@typing_extensions.final
class FeeData(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CURRENCY_FIELD_NUMBER: builtins.int
    PERIOD_FIELD_NUMBER: builtins.int
    FEES_FIELD_NUMBER: builtins.int
    CREDITS_FIELD_NUMBER: builtins.int
    BALANCE_FIELD_NUMBER: builtins.int
    CREDIT_LIMIT_FIELD_NUMBER: builtins.int
    currency: builtins.str
    @property
    def period(self) -> common.common_pb2.Period: ...
    @property
    def fees(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Fee]: ...
    @property
    def credits(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Credit]: ...
    @property
    def balance(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def credit_limit(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        currency: builtins.str = ...,
        period: common.common_pb2.Period | None = ...,
        fees: collections.abc.Iterable[global___Fee] | None = ...,
        credits: collections.abc.Iterable[global___Credit] | None = ...,
        balance: google.protobuf.wrappers_pb2.StringValue | None = ...,
        credit_limit: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["balance", b"balance", "credit_limit", b"credit_limit", "period", b"period"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["balance", b"balance", "credit_limit", b"credit_limit", "credits", b"credits", "currency", b"currency", "fees", b"fees", "period", b"period"]) -> None: ...

global___FeeData = FeeData

@typing_extensions.final
class DonutsCategory(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    VALUE_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    value: builtins.str
    @property
    def name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        value: builtins.str = ...,
        name: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["name", b"name"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["name", b"name", "value", b"value"]) -> None: ...

global___DonutsCategory = DonutsCategory

@typing_extensions.final
class DonutsAmount(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    VALUE_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    COMMAND_FIELD_NUMBER: builtins.int
    value: builtins.str
    @property
    def name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    command: global___Command.ValueType
    def __init__(
        self,
        *,
        value: builtins.str = ...,
        name: google.protobuf.wrappers_pb2.StringValue | None = ...,
        command: global___Command.ValueType = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["name", b"name"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["command", b"command", "name", b"name", "value", b"value"]) -> None: ...

global___DonutsAmount = DonutsAmount

@typing_extensions.final
class DonutsFeeType(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _FeeTypes:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _FeeTypesEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[DonutsFeeType._FeeTypes.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        Custom: DonutsFeeType._FeeTypes.ValueType  # 0
        Fee: DonutsFeeType._FeeTypes.ValueType  # 1
        Price: DonutsFeeType._FeeTypes.ValueType  # 2

    class FeeTypes(_FeeTypes, metaclass=_FeeTypesEnumTypeWrapper): ...
    Custom: DonutsFeeType.FeeTypes.ValueType  # 0
    Fee: DonutsFeeType.FeeTypes.ValueType  # 1
    Price: DonutsFeeType.FeeTypes.ValueType  # 2

    FEE_TYPE_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    fee_type: global___DonutsFeeType.FeeTypes.ValueType
    @property
    def name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        fee_type: global___DonutsFeeType.FeeTypes.ValueType = ...,
        name: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["name", b"name"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["fee_type", b"fee_type", "name", b"name"]) -> None: ...

global___DonutsFeeType = DonutsFeeType

@typing_extensions.final
class DonutsFeeSet(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    FEES_FIELD_NUMBER: builtins.int
    FEE_TYPE_FIELD_NUMBER: builtins.int
    CATEGORY_FIELD_NUMBER: builtins.int
    @property
    def fees(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___DonutsAmount]: ...
    @property
    def fee_type(self) -> global___DonutsFeeType: ...
    @property
    def category(self) -> global___DonutsCategory: ...
    def __init__(
        self,
        *,
        fees: collections.abc.Iterable[global___DonutsAmount] | None = ...,
        fee_type: global___DonutsFeeType | None = ...,
        category: global___DonutsCategory | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["category", b"category", "fee_type", b"fee_type"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["category", b"category", "fee_type", b"fee_type", "fees", b"fees"]) -> None: ...

global___DonutsFeeSet = DonutsFeeSet

@typing_extensions.final
class DonutsFeeData(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    FEES_FIELD_NUMBER: builtins.int
    @property
    def fees(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___DonutsFeeSet]: ...
    def __init__(
        self,
        *,
        fees: collections.abc.Iterable[global___DonutsFeeSet] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["fees", b"fees"]) -> None: ...

global___DonutsFeeData = DonutsFeeData
