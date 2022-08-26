from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

Courtesy: PollType
Create: PollType
Custom: Environment
DESCRIPTOR: _descriptor.FileDescriptor
Delete: PollType
Development: Environment
Emergency: Reason
End: PollType
Full: Impact
None: Impact
NotSet: PollType
OTE: Environment
Partial: Impact
Planned: Reason
Production: Environment
Staging: Environment
Update: PollType

class Description(_message.Message):
    __slots__ = ["html", "plain"]
    HTML_FIELD_NUMBER: _ClassVar[int]
    PLAIN_FIELD_NUMBER: _ClassVar[int]
    html: str
    plain: str
    def __init__(self, plain: _Optional[str] = ..., html: _Optional[str] = ...) -> None: ...

class Intervention(_message.Message):
    __slots__ = ["connection", "implementation"]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTATION_FIELD_NUMBER: _ClassVar[int]
    connection: bool
    implementation: bool
    def __init__(self, connection: bool = ..., implementation: bool = ...) -> None: ...

class MaintenanceInfoReply(_message.Message):
    __slots__ = ["cmd_resp", "created", "descriptions", "detail_url", "end", "environment", "environment_name", "id", "intervention", "item_type", "name", "poll_type", "reason", "start", "systems", "tlds", "updated"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    DETAIL_URL_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERVENTION_FIELD_NUMBER: _ClassVar[int]
    ITEM_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POLL_TYPE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    SYSTEMS_FIELD_NUMBER: _ClassVar[int]
    TLDS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    created: _timestamp_pb2.Timestamp
    descriptions: _containers.RepeatedCompositeFieldContainer[Description]
    detail_url: _wrappers_pb2.StringValue
    end: _timestamp_pb2.Timestamp
    environment: Environment
    environment_name: _wrappers_pb2.StringValue
    id: str
    intervention: Intervention
    item_type: _containers.RepeatedScalarFieldContainer[str]
    name: _wrappers_pb2.StringValue
    poll_type: PollType
    reason: Reason
    start: _timestamp_pb2.Timestamp
    systems: _containers.RepeatedCompositeFieldContainer[System]
    tlds: _containers.RepeatedScalarFieldContainer[str]
    updated: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., item_type: _Optional[_Iterable[str]] = ..., poll_type: _Optional[_Union[PollType, str]] = ..., environment: _Optional[_Union[Environment, str]] = ..., environment_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., systems: _Optional[_Iterable[_Union[System, _Mapping]]] = ..., start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., reason: _Optional[_Union[Reason, str]] = ..., detail_url: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., descriptions: _Optional[_Iterable[_Union[Description, _Mapping]]] = ..., tlds: _Optional[_Iterable[str]] = ..., intervention: _Optional[_Union[Intervention, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MaintenanceInfoRequest(_message.Message):
    __slots__ = ["id", "registry_name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class MaintenanceListReply(_message.Message):
    __slots__ = ["cmd_resp", "items"]
    class Item(_message.Message):
        __slots__ = ["created", "end", "id", "name", "start", "updated"]
        CREATED_FIELD_NUMBER: _ClassVar[int]
        END_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        START_FIELD_NUMBER: _ClassVar[int]
        UPDATED_FIELD_NUMBER: _ClassVar[int]
        created: _timestamp_pb2.Timestamp
        end: _timestamp_pb2.Timestamp
        id: str
        name: _wrappers_pb2.StringValue
        start: _timestamp_pb2.Timestamp
        updated: _timestamp_pb2.Timestamp
        def __init__(self, id: _Optional[str] = ..., name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    items: _containers.RepeatedCompositeFieldContainer[MaintenanceListReply.Item]
    def __init__(self, items: _Optional[_Iterable[_Union[MaintenanceListReply.Item, _Mapping]]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class System(_message.Message):
    __slots__ = ["host", "impact", "name"]
    HOST_FIELD_NUMBER: _ClassVar[int]
    IMPACT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    host: _wrappers_pb2.StringValue
    impact: Impact
    name: str
    def __init__(self, name: _Optional[str] = ..., host: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., impact: _Optional[_Union[Impact, str]] = ...) -> None: ...

class Environment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Impact(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class Reason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class PollType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
