from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

Available: DomainState
DESCRIPTOR: _descriptor.FileDescriptor
NoLongerRequired: DomainStatus
NotWithinRegistry: DomainState
RealTime: Environment
Registered: DomainState
RegisteredUntilExpiry: DomainStatus
RenewalRequired: DomainStatus
RulesPrevent: DomainState
TimeDelay: Environment
Unknown: DomainStatus

class DomainRequest(_message.Message):
    __slots__ = ["environment", "name", "registry_name"]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    environment: Environment
    name: str
    registry_name: str
    def __init__(self, name: _Optional[str] = ..., environment: _Optional[_Union[Environment, str]] = ..., registry_name: _Optional[str] = ...) -> None: ...

class DomainResponse(_message.Message):
    __slots__ = ["created", "detagged", "expiry", "registration_state", "status", "suspended", "tag"]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    DETAGGED_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_FIELD_NUMBER: _ClassVar[int]
    REGISTRATION_STATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUSPENDED_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    created: _timestamp_pb2.Timestamp
    detagged: bool
    expiry: _timestamp_pb2.Timestamp
    registration_state: DomainState
    status: DomainStatus
    suspended: _wrappers_pb2.BoolValue
    tag: str
    def __init__(self, registration_state: _Optional[_Union[DomainState, str]] = ..., detagged: bool = ..., suspended: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expiry: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[_Union[DomainStatus, str]] = ..., tag: _Optional[str] = ...) -> None: ...

class UsageRequest(_message.Message):
    __slots__ = ["environment", "registry_name"]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    environment: Environment
    registry_name: str
    def __init__(self, environment: _Optional[_Union[Environment, str]] = ..., registry_name: _Optional[str] = ...) -> None: ...

class UsageResponse(_message.Message):
    __slots__ = ["usage_24", "usage_60"]
    USAGE_24_FIELD_NUMBER: _ClassVar[int]
    USAGE_60_FIELD_NUMBER: _ClassVar[int]
    usage_24: int
    usage_60: int
    def __init__(self, usage_60: _Optional[int] = ..., usage_24: _Optional[int] = ...) -> None: ...

class Environment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DomainState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DomainStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
