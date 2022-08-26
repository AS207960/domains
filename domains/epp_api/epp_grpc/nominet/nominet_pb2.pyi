from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from domain import domain_pb2 as _domain_pb2
from contact import contact_pb2 as _contact_pb2
from common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContactValidateReply(_message.Message):
    __slots__ = ["cmd_resp"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    def __init__(self, cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class ContactValidateRequest(_message.Message):
    __slots__ = ["contact_id", "registry_name"]
    CONTACT_ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    contact_id: str
    registry_name: str
    def __init__(self, registry_name: _Optional[str] = ..., contact_id: _Optional[str] = ...) -> None: ...

class DomainCancel(_message.Message):
    __slots__ = ["name", "originator"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORIGINATOR_FIELD_NUMBER: _ClassVar[int]
    name: str
    originator: str
    def __init__(self, name: _Optional[str] = ..., originator: _Optional[str] = ...) -> None: ...

class DomainFail(_message.Message):
    __slots__ = ["domain", "reason"]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    domain: str
    reason: str
    def __init__(self, domain: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class DomainRegistrarChange(_message.Message):
    __slots__ = ["case_id", "contact", "domains", "originator", "registrar_tag"]
    CASE_ID_FIELD_NUMBER: _ClassVar[int]
    CONTACT_FIELD_NUMBER: _ClassVar[int]
    DOMAINS_FIELD_NUMBER: _ClassVar[int]
    ORIGINATOR_FIELD_NUMBER: _ClassVar[int]
    REGISTRAR_TAG_FIELD_NUMBER: _ClassVar[int]
    case_id: _wrappers_pb2.StringValue
    contact: _contact_pb2.ContactInfoReply
    domains: _containers.RepeatedCompositeFieldContainer[_domain_pb2.DomainInfoReply]
    originator: str
    registrar_tag: str
    def __init__(self, originator: _Optional[str] = ..., registrar_tag: _Optional[str] = ..., case_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., domains: _Optional[_Iterable[_Union[_domain_pb2.DomainInfoReply, _Mapping]]] = ..., contact: _Optional[_Union[_contact_pb2.ContactInfoReply, _Mapping]] = ...) -> None: ...

class DomainRelease(_message.Message):
    __slots__ = ["account_id", "account_moved", "domains", "registrar_tag"]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_MOVED_FIELD_NUMBER: _ClassVar[int]
    DOMAINS_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    REGISTRAR_TAG_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    account_moved: bool
    domains: _containers.RepeatedScalarFieldContainer[str]
    registrar_tag: str
    def __init__(self, account_id: _Optional[str] = ..., account_moved: bool = ..., registrar_tag: _Optional[str] = ..., domains: _Optional[_Iterable[str]] = ..., **kwargs) -> None: ...

class HandshakeAcceptRequest(_message.Message):
    __slots__ = ["case_id", "registrant", "registry_name"]
    CASE_ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    case_id: str
    registrant: _wrappers_pb2.StringValue
    registry_name: str
    def __init__(self, registry_name: _Optional[str] = ..., case_id: _Optional[str] = ..., registrant: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class HandshakeRejectRequest(_message.Message):
    __slots__ = ["case_id", "registry_name"]
    CASE_ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    case_id: str
    registry_name: str
    def __init__(self, registry_name: _Optional[str] = ..., case_id: _Optional[str] = ...) -> None: ...

class HandshakeReply(_message.Message):
    __slots__ = ["case_id", "cmd_resp", "domains"]
    CASE_ID_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    DOMAINS_FIELD_NUMBER: _ClassVar[int]
    case_id: str
    cmd_resp: _common_pb2.CommandResponse
    domains: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, case_id: _Optional[str] = ..., domains: _Optional[_Iterable[str]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class HostCancel(_message.Message):
    __slots__ = ["domain_names", "host_objects"]
    DOMAIN_NAMES_FIELD_NUMBER: _ClassVar[int]
    HOST_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    domain_names: _containers.RepeatedScalarFieldContainer[str]
    host_objects: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, host_objects: _Optional[_Iterable[str]] = ..., domain_names: _Optional[_Iterable[str]] = ...) -> None: ...

class LockReply(_message.Message):
    __slots__ = ["cmd_resp"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    def __init__(self, cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class LockRequest(_message.Message):
    __slots__ = ["lock_type", "object", "registry_name"]
    LOCK_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    lock_type: str
    object: Object
    registry_name: str
    def __init__(self, registry_name: _Optional[str] = ..., lock_type: _Optional[str] = ..., object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class NominetTagListReply(_message.Message):
    __slots__ = ["cmd_resp", "tags"]
    class Tag(_message.Message):
        __slots__ = ["handshake", "name", "tag", "trading_name"]
        HANDSHAKE_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        TAG_FIELD_NUMBER: _ClassVar[int]
        TRADING_NAME_FIELD_NUMBER: _ClassVar[int]
        handshake: bool
        name: str
        tag: str
        trading_name: _wrappers_pb2.StringValue
        def __init__(self, tag: _Optional[str] = ..., name: _Optional[str] = ..., trading_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., handshake: bool = ...) -> None: ...
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    tags: _containers.RepeatedCompositeFieldContainer[NominetTagListReply.Tag]
    def __init__(self, tags: _Optional[_Iterable[_Union[NominetTagListReply.Tag, _Mapping]]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class Object(_message.Message):
    __slots__ = ["domain", "registrant"]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_FIELD_NUMBER: _ClassVar[int]
    domain: str
    registrant: str
    def __init__(self, domain: _Optional[str] = ..., registrant: _Optional[str] = ...) -> None: ...

class Process(_message.Message):
    __slots__ = ["cancel_date", "contact", "domain_names", "process_type", "stage", "suspend_date"]
    class ProcessStage(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    CANCEL_DATE_FIELD_NUMBER: _ClassVar[int]
    CONTACT_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_NAMES_FIELD_NUMBER: _ClassVar[int]
    Initial: Process.ProcessStage
    PROCESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    SUSPEND_DATE_FIELD_NUMBER: _ClassVar[int]
    Updated: Process.ProcessStage
    cancel_date: _timestamp_pb2.Timestamp
    contact: _contact_pb2.ContactInfoReply
    domain_names: _containers.RepeatedScalarFieldContainer[str]
    process_type: str
    stage: Process.ProcessStage
    suspend_date: _timestamp_pb2.Timestamp
    def __init__(self, stage: _Optional[_Union[Process.ProcessStage, str]] = ..., contact: _Optional[_Union[_contact_pb2.ContactInfoReply, _Mapping]] = ..., process_type: _Optional[str] = ..., suspend_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cancel_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., domain_names: _Optional[_Iterable[str]] = ...) -> None: ...

class RegistrantTransfer(_message.Message):
    __slots__ = ["account_id", "case_id", "contact", "domain_names", "old_account_id", "originator"]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CASE_ID_FIELD_NUMBER: _ClassVar[int]
    CONTACT_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_NAMES_FIELD_NUMBER: _ClassVar[int]
    OLD_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINATOR_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    case_id: _wrappers_pb2.StringValue
    contact: _contact_pb2.ContactInfoReply
    domain_names: _containers.RepeatedScalarFieldContainer[str]
    old_account_id: str
    originator: str
    def __init__(self, originator: _Optional[str] = ..., account_id: _Optional[str] = ..., old_account_id: _Optional[str] = ..., case_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., domain_names: _Optional[_Iterable[str]] = ..., contact: _Optional[_Union[_contact_pb2.ContactInfoReply, _Mapping]] = ...) -> None: ...

class ReleaseReply(_message.Message):
    __slots__ = ["cmd_resp", "message", "pending"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    message: _wrappers_pb2.StringValue
    pending: bool
    def __init__(self, pending: bool = ..., message: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class ReleaseRequest(_message.Message):
    __slots__ = ["object", "registrar_tag", "registry_name"]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    REGISTRAR_TAG_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    object: Object
    registrar_tag: str
    registry_name: str
    def __init__(self, registry_name: _Optional[str] = ..., registrar_tag: _Optional[str] = ..., object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class Suspend(_message.Message):
    __slots__ = ["cancel_date", "domain_names", "reason"]
    CANCEL_DATE_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_NAMES_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    cancel_date: _timestamp_pb2.Timestamp
    domain_names: _containers.RepeatedScalarFieldContainer[str]
    reason: str
    def __init__(self, reason: _Optional[str] = ..., cancel_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., domain_names: _Optional[_Iterable[str]] = ...) -> None: ...
