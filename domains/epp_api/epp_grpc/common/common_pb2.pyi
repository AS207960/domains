from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

ClientApproved: TransferStatus
ClientCancelled: TransferStatus
ClientRejected: TransferStatus
DESCRIPTOR: _descriptor.FileDescriptor
Pending: TransferStatus
ServerApproved: TransferStatus
ServerCancelled: TransferStatus
UnknownStatus: TransferStatus

class CommandExtraValue(_message.Message):
    __slots__ = ["reason", "value"]
    REASON_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    reason: str
    value: str
    def __init__(self, reason: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class CommandResponse(_message.Message):
    __slots__ = ["extra_values", "transaction_id"]
    EXTRA_VALUES_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    extra_values: _containers.RepeatedCompositeFieldContainer[CommandExtraValue]
    transaction_id: CommandTransactionID
    def __init__(self, extra_values: _Optional[_Iterable[_Union[CommandExtraValue, _Mapping]]] = ..., transaction_id: _Optional[_Union[CommandTransactionID, _Mapping]] = ...) -> None: ...

class CommandTransactionID(_message.Message):
    __slots__ = ["client", "server"]
    CLIENT_FIELD_NUMBER: _ClassVar[int]
    SERVER_FIELD_NUMBER: _ClassVar[int]
    client: str
    server: str
    def __init__(self, client: _Optional[str] = ..., server: _Optional[str] = ...) -> None: ...

class IPAddress(_message.Message):
    __slots__ = ["address", "type"]
    class IPVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    IPv4: IPAddress.IPVersion
    IPv6: IPAddress.IPVersion
    TYPE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN: IPAddress.IPVersion
    address: str
    type: IPAddress.IPVersion
    def __init__(self, address: _Optional[str] = ..., type: _Optional[_Union[IPAddress.IPVersion, str]] = ...) -> None: ...

class Period(_message.Message):
    __slots__ = ["unit", "value"]
    class Unit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    Months: Period.Unit
    UNIT_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    Years: Period.Unit
    unit: Period.Unit
    value: int
    def __init__(self, value: _Optional[int] = ..., unit: _Optional[_Union[Period.Unit, str]] = ...) -> None: ...

class Phone(_message.Message):
    __slots__ = ["extension", "number"]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    extension: _wrappers_pb2.StringValue
    number: str
    def __init__(self, number: _Optional[str] = ..., extension: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class TransferStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
