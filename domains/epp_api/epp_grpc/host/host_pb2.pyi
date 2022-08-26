from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from common import common_pb2 as _common_pb2
from isnic import isnic_pb2 as _isnic_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

ClientDeleteProhibited: HostStatus
ClientUpdateProhibited: HostStatus
DESCRIPTOR: _descriptor.FileDescriptor
Linked: HostStatus
Ok: HostStatus
PendingCreate: HostStatus
PendingDelete: HostStatus
PendingTransfer: HostStatus
PendingUpdate: HostStatus
ServerDeleteProhibited: HostStatus
ServerUpdateProhibited: HostStatus

class HostCheckReply(_message.Message):
    __slots__ = ["available", "cmd_resp", "reason"]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    available: bool
    cmd_resp: _common_pb2.CommandResponse
    reason: _wrappers_pb2.StringValue
    def __init__(self, available: bool = ..., reason: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class HostCheckRequest(_message.Message):
    __slots__ = ["name", "registry_name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    registry_name: str
    def __init__(self, name: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class HostCreateReply(_message.Message):
    __slots__ = ["cmd_resp", "creation_date", "name", "pending"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    creation_date: _timestamp_pb2.Timestamp
    name: str
    pending: bool
    def __init__(self, name: _Optional[str] = ..., pending: bool = ..., creation_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class HostCreateRequest(_message.Message):
    __slots__ = ["addresses", "isnic_info", "name", "registry_name"]
    ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    ISNIC_INFO_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    addresses: _containers.RepeatedCompositeFieldContainer[_common_pb2.IPAddress]
    isnic_info: _isnic_pb2.HostInfo
    name: str
    registry_name: str
    def __init__(self, name: _Optional[str] = ..., addresses: _Optional[_Iterable[_Union[_common_pb2.IPAddress, _Mapping]]] = ..., registry_name: _Optional[str] = ..., isnic_info: _Optional[_Union[_isnic_pb2.HostInfo, _Mapping]] = ...) -> None: ...

class HostDeleteReply(_message.Message):
    __slots__ = ["cmd_resp", "pending"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    pending: bool
    def __init__(self, pending: bool = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class HostDeleteRequest(_message.Message):
    __slots__ = ["name", "registry_name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    registry_name: str
    def __init__(self, name: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class HostInfoReply(_message.Message):
    __slots__ = ["addresses", "client_created_id", "client_id", "cmd_resp", "creation_date", "last_transfer_date", "last_updated_client", "last_updated_date", "name", "registry_id", "statuses"]
    ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    CLIENT_CREATED_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    LAST_TRANSFER_DATE_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_CLIENT_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_DATE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_ID_FIELD_NUMBER: _ClassVar[int]
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    addresses: _containers.RepeatedCompositeFieldContainer[_common_pb2.IPAddress]
    client_created_id: _wrappers_pb2.StringValue
    client_id: str
    cmd_resp: _common_pb2.CommandResponse
    creation_date: _timestamp_pb2.Timestamp
    last_transfer_date: _timestamp_pb2.Timestamp
    last_updated_client: _wrappers_pb2.StringValue
    last_updated_date: _timestamp_pb2.Timestamp
    name: str
    registry_id: str
    statuses: _containers.RepeatedScalarFieldContainer[HostStatus]
    def __init__(self, name: _Optional[str] = ..., registry_id: _Optional[str] = ..., statuses: _Optional[_Iterable[_Union[HostStatus, str]]] = ..., addresses: _Optional[_Iterable[_Union[_common_pb2.IPAddress, _Mapping]]] = ..., client_id: _Optional[str] = ..., client_created_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., creation_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_updated_client: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., last_updated_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_transfer_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class HostInfoRequest(_message.Message):
    __slots__ = ["name", "registry_name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    registry_name: str
    def __init__(self, name: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class HostUpdateReply(_message.Message):
    __slots__ = ["cmd_resp", "pending"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    pending: bool
    def __init__(self, pending: bool = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class HostUpdateRequest(_message.Message):
    __slots__ = ["add", "isnic_info", "name", "new_name", "registry_name", "remove"]
    class Param(_message.Message):
        __slots__ = ["address", "state"]
        ADDRESS_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        address: _common_pb2.IPAddress
        state: HostStatus
        def __init__(self, address: _Optional[_Union[_common_pb2.IPAddress, _Mapping]] = ..., state: _Optional[_Union[HostStatus, str]] = ...) -> None: ...
    ADD_FIELD_NUMBER: _ClassVar[int]
    ISNIC_INFO_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NEW_NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    REMOVE_FIELD_NUMBER: _ClassVar[int]
    add: _containers.RepeatedCompositeFieldContainer[HostUpdateRequest.Param]
    isnic_info: _isnic_pb2.HostInfo
    name: str
    new_name: _wrappers_pb2.StringValue
    registry_name: str
    remove: _containers.RepeatedCompositeFieldContainer[HostUpdateRequest.Param]
    def __init__(self, name: _Optional[str] = ..., add: _Optional[_Iterable[_Union[HostUpdateRequest.Param, _Mapping]]] = ..., remove: _Optional[_Iterable[_Union[HostUpdateRequest.Param, _Mapping]]] = ..., new_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., registry_name: _Optional[str] = ..., isnic_info: _Optional[_Union[_isnic_pb2.HostInfo, _Mapping]] = ...) -> None: ...

class HostStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
