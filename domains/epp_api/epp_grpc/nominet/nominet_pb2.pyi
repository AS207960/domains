"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import common.common_pb2
import contact.contact_pb2
import domain.domain_pb2
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

@typing_extensions.final
class HandshakeAcceptRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    CASE_ID_FIELD_NUMBER: builtins.int
    REGISTRANT_FIELD_NUMBER: builtins.int
    registry_name: builtins.str
    case_id: builtins.str
    @property
    def registrant(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        registry_name: builtins.str = ...,
        case_id: builtins.str = ...,
        registrant: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["registrant", b"registrant"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["case_id", b"case_id", "registrant", b"registrant", "registry_name", b"registry_name"]) -> None: ...

global___HandshakeAcceptRequest = HandshakeAcceptRequest

@typing_extensions.final
class HandshakeRejectRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    CASE_ID_FIELD_NUMBER: builtins.int
    registry_name: builtins.str
    case_id: builtins.str
    def __init__(
        self,
        *,
        registry_name: builtins.str = ...,
        case_id: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["case_id", b"case_id", "registry_name", b"registry_name"]) -> None: ...

global___HandshakeRejectRequest = HandshakeRejectRequest

@typing_extensions.final
class HandshakeReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CASE_ID_FIELD_NUMBER: builtins.int
    DOMAINS_FIELD_NUMBER: builtins.int
    CMD_RESP_FIELD_NUMBER: builtins.int
    case_id: builtins.str
    @property
    def domains(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    def __init__(
        self,
        *,
        case_id: builtins.str = ...,
        domains: collections.abc.Iterable[builtins.str] | None = ...,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["case_id", b"case_id", "cmd_resp", b"cmd_resp", "domains", b"domains"]) -> None: ...

global___HandshakeReply = HandshakeReply

@typing_extensions.final
class ReleaseRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    REGISTRAR_TAG_FIELD_NUMBER: builtins.int
    OBJECT_FIELD_NUMBER: builtins.int
    registry_name: builtins.str
    registrar_tag: builtins.str
    @property
    def object(self) -> global___Object: ...
    def __init__(
        self,
        *,
        registry_name: builtins.str = ...,
        registrar_tag: builtins.str = ...,
        object: global___Object | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["object", b"object"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["object", b"object", "registrar_tag", b"registrar_tag", "registry_name", b"registry_name"]) -> None: ...

global___ReleaseRequest = ReleaseRequest

@typing_extensions.final
class Object(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DOMAIN_FIELD_NUMBER: builtins.int
    REGISTRANT_FIELD_NUMBER: builtins.int
    domain: builtins.str
    registrant: builtins.str
    def __init__(
        self,
        *,
        domain: builtins.str = ...,
        registrant: builtins.str = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["domain", b"domain", "object", b"object", "registrant", b"registrant"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["domain", b"domain", "object", b"object", "registrant", b"registrant"]) -> None: ...
    def WhichOneof(self, oneof_group: typing_extensions.Literal["object", b"object"]) -> typing_extensions.Literal["domain", "registrant"] | None: ...

global___Object = Object

@typing_extensions.final
class ReleaseReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    PENDING_FIELD_NUMBER: builtins.int
    MESSAGE_FIELD_NUMBER: builtins.int
    CMD_RESP_FIELD_NUMBER: builtins.int
    pending: builtins.bool
    @property
    def message(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    def __init__(
        self,
        *,
        pending: builtins.bool = ...,
        message: google.protobuf.wrappers_pb2.StringValue | None = ...,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp", "message", b"message"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp", "message", b"message", "pending", b"pending"]) -> None: ...

global___ReleaseReply = ReleaseReply

@typing_extensions.final
class NominetTagListReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class Tag(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        TAG_FIELD_NUMBER: builtins.int
        NAME_FIELD_NUMBER: builtins.int
        TRADING_NAME_FIELD_NUMBER: builtins.int
        HANDSHAKE_FIELD_NUMBER: builtins.int
        tag: builtins.str
        name: builtins.str
        @property
        def trading_name(self) -> google.protobuf.wrappers_pb2.StringValue: ...
        handshake: builtins.bool
        def __init__(
            self,
            *,
            tag: builtins.str = ...,
            name: builtins.str = ...,
            trading_name: google.protobuf.wrappers_pb2.StringValue | None = ...,
            handshake: builtins.bool = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["trading_name", b"trading_name"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["handshake", b"handshake", "name", b"name", "tag", b"tag", "trading_name", b"trading_name"]) -> None: ...

    TAGS_FIELD_NUMBER: builtins.int
    CMD_RESP_FIELD_NUMBER: builtins.int
    @property
    def tags(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___NominetTagListReply.Tag]: ...
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    def __init__(
        self,
        *,
        tags: collections.abc.Iterable[global___NominetTagListReply.Tag] | None = ...,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp", "tags", b"tags"]) -> None: ...

global___NominetTagListReply = NominetTagListReply

@typing_extensions.final
class DomainCancel(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    NAME_FIELD_NUMBER: builtins.int
    ORIGINATOR_FIELD_NUMBER: builtins.int
    name: builtins.str
    originator: builtins.str
    def __init__(
        self,
        *,
        name: builtins.str = ...,
        originator: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["name", b"name", "originator", b"originator"]) -> None: ...

global___DomainCancel = DomainCancel

@typing_extensions.final
class DomainRelease(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ACCOUNT_ID_FIELD_NUMBER: builtins.int
    ACCOUNT_MOVED_FIELD_NUMBER: builtins.int
    FROM_FIELD_NUMBER: builtins.int
    REGISTRAR_TAG_FIELD_NUMBER: builtins.int
    DOMAINS_FIELD_NUMBER: builtins.int
    account_id: builtins.str
    account_moved: builtins.bool
    registrar_tag: builtins.str
    @property
    def domains(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    def __init__(
        self,
        *,
        account_id: builtins.str = ...,
        account_moved: builtins.bool = ...,
        registrar_tag: builtins.str = ...,
        domains: collections.abc.Iterable[builtins.str] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "account_moved", b"account_moved", "domains", b"domains", "from", b"from", "registrar_tag", b"registrar_tag"]) -> None: ...

global___DomainRelease = DomainRelease

@typing_extensions.final
class DomainRegistrarChange(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ORIGINATOR_FIELD_NUMBER: builtins.int
    REGISTRAR_TAG_FIELD_NUMBER: builtins.int
    CASE_ID_FIELD_NUMBER: builtins.int
    DOMAINS_FIELD_NUMBER: builtins.int
    CONTACT_FIELD_NUMBER: builtins.int
    originator: builtins.str
    registrar_tag: builtins.str
    @property
    def case_id(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def domains(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[domain.domain_pb2.DomainInfoReply]: ...
    @property
    def contact(self) -> contact.contact_pb2.ContactInfoReply: ...
    def __init__(
        self,
        *,
        originator: builtins.str = ...,
        registrar_tag: builtins.str = ...,
        case_id: google.protobuf.wrappers_pb2.StringValue | None = ...,
        domains: collections.abc.Iterable[domain.domain_pb2.DomainInfoReply] | None = ...,
        contact: contact.contact_pb2.ContactInfoReply | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["case_id", b"case_id", "contact", b"contact"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["case_id", b"case_id", "contact", b"contact", "domains", b"domains", "originator", b"originator", "registrar_tag", b"registrar_tag"]) -> None: ...

global___DomainRegistrarChange = DomainRegistrarChange

@typing_extensions.final
class HostCancel(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    HOST_OBJECTS_FIELD_NUMBER: builtins.int
    DOMAIN_NAMES_FIELD_NUMBER: builtins.int
    @property
    def host_objects(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    @property
    def domain_names(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    def __init__(
        self,
        *,
        host_objects: collections.abc.Iterable[builtins.str] | None = ...,
        domain_names: collections.abc.Iterable[builtins.str] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["domain_names", b"domain_names", "host_objects", b"host_objects"]) -> None: ...

global___HostCancel = HostCancel

@typing_extensions.final
class Process(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _ProcessStage:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _ProcessStageEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[Process._ProcessStage.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        Initial: Process._ProcessStage.ValueType  # 0
        Updated: Process._ProcessStage.ValueType  # 1

    class ProcessStage(_ProcessStage, metaclass=_ProcessStageEnumTypeWrapper): ...
    Initial: Process.ProcessStage.ValueType  # 0
    Updated: Process.ProcessStage.ValueType  # 1

    STAGE_FIELD_NUMBER: builtins.int
    CONTACT_FIELD_NUMBER: builtins.int
    PROCESS_TYPE_FIELD_NUMBER: builtins.int
    SUSPEND_DATE_FIELD_NUMBER: builtins.int
    CANCEL_DATE_FIELD_NUMBER: builtins.int
    DOMAIN_NAMES_FIELD_NUMBER: builtins.int
    stage: global___Process.ProcessStage.ValueType
    @property
    def contact(self) -> contact.contact_pb2.ContactInfoReply: ...
    process_type: builtins.str
    @property
    def suspend_date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    @property
    def cancel_date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    @property
    def domain_names(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    def __init__(
        self,
        *,
        stage: global___Process.ProcessStage.ValueType = ...,
        contact: contact.contact_pb2.ContactInfoReply | None = ...,
        process_type: builtins.str = ...,
        suspend_date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        cancel_date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        domain_names: collections.abc.Iterable[builtins.str] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cancel_date", b"cancel_date", "contact", b"contact", "suspend_date", b"suspend_date"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["cancel_date", b"cancel_date", "contact", b"contact", "domain_names", b"domain_names", "process_type", b"process_type", "stage", b"stage", "suspend_date", b"suspend_date"]) -> None: ...

global___Process = Process

@typing_extensions.final
class Suspend(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    REASON_FIELD_NUMBER: builtins.int
    CANCEL_DATE_FIELD_NUMBER: builtins.int
    DOMAIN_NAMES_FIELD_NUMBER: builtins.int
    reason: builtins.str
    @property
    def cancel_date(self) -> google.protobuf.timestamp_pb2.Timestamp: ...
    @property
    def domain_names(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    def __init__(
        self,
        *,
        reason: builtins.str = ...,
        cancel_date: google.protobuf.timestamp_pb2.Timestamp | None = ...,
        domain_names: collections.abc.Iterable[builtins.str] | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cancel_date", b"cancel_date"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["cancel_date", b"cancel_date", "domain_names", b"domain_names", "reason", b"reason"]) -> None: ...

global___Suspend = Suspend

@typing_extensions.final
class DomainFail(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DOMAIN_FIELD_NUMBER: builtins.int
    REASON_FIELD_NUMBER: builtins.int
    domain: builtins.str
    reason: builtins.str
    def __init__(
        self,
        *,
        domain: builtins.str = ...,
        reason: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["domain", b"domain", "reason", b"reason"]) -> None: ...

global___DomainFail = DomainFail

@typing_extensions.final
class RegistrantTransfer(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ORIGINATOR_FIELD_NUMBER: builtins.int
    ACCOUNT_ID_FIELD_NUMBER: builtins.int
    OLD_ACCOUNT_ID_FIELD_NUMBER: builtins.int
    CASE_ID_FIELD_NUMBER: builtins.int
    DOMAIN_NAMES_FIELD_NUMBER: builtins.int
    CONTACT_FIELD_NUMBER: builtins.int
    originator: builtins.str
    account_id: builtins.str
    old_account_id: builtins.str
    @property
    def case_id(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def domain_names(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    @property
    def contact(self) -> contact.contact_pb2.ContactInfoReply: ...
    def __init__(
        self,
        *,
        originator: builtins.str = ...,
        account_id: builtins.str = ...,
        old_account_id: builtins.str = ...,
        case_id: google.protobuf.wrappers_pb2.StringValue | None = ...,
        domain_names: collections.abc.Iterable[builtins.str] | None = ...,
        contact: contact.contact_pb2.ContactInfoReply | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["case_id", b"case_id", "contact", b"contact"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["account_id", b"account_id", "case_id", b"case_id", "contact", b"contact", "domain_names", b"domain_names", "old_account_id", b"old_account_id", "originator", b"originator"]) -> None: ...

global___RegistrantTransfer = RegistrantTransfer

@typing_extensions.final
class ContactValidateRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    CONTACT_ID_FIELD_NUMBER: builtins.int
    registry_name: builtins.str
    contact_id: builtins.str
    def __init__(
        self,
        *,
        registry_name: builtins.str = ...,
        contact_id: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["contact_id", b"contact_id", "registry_name", b"registry_name"]) -> None: ...

global___ContactValidateRequest = ContactValidateRequest

@typing_extensions.final
class ContactValidateReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CMD_RESP_FIELD_NUMBER: builtins.int
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    def __init__(
        self,
        *,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp"]) -> None: ...

global___ContactValidateReply = ContactValidateReply

@typing_extensions.final
class LockRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    REGISTRY_NAME_FIELD_NUMBER: builtins.int
    LOCK_TYPE_FIELD_NUMBER: builtins.int
    OBJECT_FIELD_NUMBER: builtins.int
    registry_name: builtins.str
    lock_type: builtins.str
    @property
    def object(self) -> global___Object: ...
    def __init__(
        self,
        *,
        registry_name: builtins.str = ...,
        lock_type: builtins.str = ...,
        object: global___Object | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["object", b"object"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["lock_type", b"lock_type", "object", b"object", "registry_name", b"registry_name"]) -> None: ...

global___LockRequest = LockRequest

@typing_extensions.final
class LockReply(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CMD_RESP_FIELD_NUMBER: builtins.int
    @property
    def cmd_resp(self) -> common.common_pb2.CommandResponse: ...
    def __init__(
        self,
        *,
        cmd_resp: common.common_pb2.CommandResponse | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["cmd_resp", b"cmd_resp"]) -> None: ...

global___LockReply = LockReply
