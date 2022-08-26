from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

Allocated: StatusType
Custom: StatusType
DESCRIPTOR: _descriptor.FileDescriptor
Invalid: StatusType
PendingAllocation: StatusType
PendingValidation: StatusType
Rejected: StatusType
Validated: StatusType

class ClaimsKey(_message.Message):
    __slots__ = ["key", "validator_id"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_ID_FIELD_NUMBER: _ClassVar[int]
    key: str
    validator_id: _wrappers_pb2.StringValue
    def __init__(self, key: _Optional[str] = ..., validator_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class CodeMark(_message.Message):
    __slots__ = ["code", "mark", "validator"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MARK_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_FIELD_NUMBER: _ClassVar[int]
    code: _wrappers_pb2.StringValue
    mark: _wrappers_pb2.StringValue
    validator: _wrappers_pb2.StringValue
    def __init__(self, code: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., validator: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., mark: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class CoreNICApplicationInfo(_message.Message):
    __slots__ = ["info", "info_type"]
    INFO_FIELD_NUMBER: _ClassVar[int]
    INFO_TYPE_FIELD_NUMBER: _ClassVar[int]
    info: str
    info_type: _wrappers_pb2.StringValue
    def __init__(self, info: _Optional[str] = ..., info_type: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class LaunchCreate(_message.Message):
    __slots__ = ["code_mark", "core_nic_augmented_mark", "create_type", "notices", "phase", "signed_mark"]
    class CreateType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    Application: LaunchCreate.CreateType
    CODE_MARK_FIELD_NUMBER: _ClassVar[int]
    CORE_NIC_AUGMENTED_MARK_FIELD_NUMBER: _ClassVar[int]
    CREATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NOTICES_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    Registration: LaunchCreate.CreateType
    SIGNED_MARK_FIELD_NUMBER: _ClassVar[int]
    code_mark: _containers.RepeatedCompositeFieldContainer[CodeMark]
    core_nic_augmented_mark: _containers.RepeatedCompositeFieldContainer[CoreNICApplicationInfo]
    create_type: LaunchCreate.CreateType
    notices: _containers.RepeatedCompositeFieldContainer[Notice]
    phase: Phase
    signed_mark: _wrappers_pb2.StringValue
    def __init__(self, phase: _Optional[_Union[Phase, _Mapping]] = ..., code_mark: _Optional[_Iterable[_Union[CodeMark, _Mapping]]] = ..., notices: _Optional[_Iterable[_Union[Notice, _Mapping]]] = ..., signed_mark: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., create_type: _Optional[_Union[LaunchCreate.CreateType, str]] = ..., core_nic_augmented_mark: _Optional[_Iterable[_Union[CoreNICApplicationInfo, _Mapping]]] = ...) -> None: ...

class LaunchData(_message.Message):
    __slots__ = ["application_Id", "phase"]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    application_Id: _wrappers_pb2.StringValue
    phase: Phase
    def __init__(self, phase: _Optional[_Union[Phase, _Mapping]] = ..., application_Id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class LaunchInfo(_message.Message):
    __slots__ = ["application_id", "include_mark", "phase"]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_MARK_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    application_id: _wrappers_pb2.StringValue
    include_mark: bool
    phase: Phase
    def __init__(self, include_mark: bool = ..., phase: _Optional[_Union[Phase, _Mapping]] = ..., application_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class LaunchInfoData(_message.Message):
    __slots__ = ["application_id", "mark", "phase", "status"]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    MARK_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    application_id: _wrappers_pb2.StringValue
    mark: _wrappers_pb2.StringValue
    phase: Phase
    status: Status
    def __init__(self, phase: _Optional[_Union[Phase, _Mapping]] = ..., application_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., status: _Optional[_Union[Status, _Mapping]] = ..., mark: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class Notice(_message.Message):
    __slots__ = ["accepted_after", "not_after", "notice_id", "validator"]
    ACCEPTED_AFTER_FIELD_NUMBER: _ClassVar[int]
    NOTICE_ID_FIELD_NUMBER: _ClassVar[int]
    NOT_AFTER_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_FIELD_NUMBER: _ClassVar[int]
    accepted_after: _timestamp_pb2.Timestamp
    not_after: _timestamp_pb2.Timestamp
    notice_id: str
    validator: _wrappers_pb2.StringValue
    def __init__(self, notice_id: _Optional[str] = ..., validator: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., not_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., accepted_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Phase(_message.Message):
    __slots__ = ["phase_name", "phase_type"]
    class PhaseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    Claims: Phase.PhaseType
    Custom: Phase.PhaseType
    Landrush: Phase.PhaseType
    Open: Phase.PhaseType
    PHASE_NAME_FIELD_NUMBER: _ClassVar[int]
    PHASE_TYPE_FIELD_NUMBER: _ClassVar[int]
    Sunrise: Phase.PhaseType
    phase_name: _wrappers_pb2.StringValue
    phase_type: Phase.PhaseType
    def __init__(self, phase_type: _Optional[_Union[Phase.PhaseType, str]] = ..., phase_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class Status(_message.Message):
    __slots__ = ["message", "status_name", "status_type"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_TYPE_FIELD_NUMBER: _ClassVar[int]
    message: _wrappers_pb2.StringValue
    status_name: _wrappers_pb2.StringValue
    status_type: StatusType
    def __init__(self, status_type: _Optional[_Union[StatusType, str]] = ..., status_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., message: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class StatusType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
