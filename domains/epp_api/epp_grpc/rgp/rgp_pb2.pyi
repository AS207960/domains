from fee import fee_pb2 as _fee_pb2
from common import common_pb2 as _common_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

AddPeriod: RGPState
AutoRenewPeriod: RGPState
DESCRIPTOR: _descriptor.FileDescriptor
PendingDelete: RGPState
PendingRestore: RGPState
RedemptionPeriod: RGPState
RenewPeriod: RGPState
TransferPeriod: RGPState
Unknown: RGPState

class ReportReply(_message.Message):
    __slots__ = ["cmd_resp", "fee_data", "pending", "registry_name"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    fee_data: _fee_pb2.FeeData
    pending: bool
    registry_name: str
    def __init__(self, pending: bool = ..., fee_data: _Optional[_Union[_fee_pb2.FeeData, _Mapping]] = ..., registry_name: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class ReportRequest(_message.Message):
    __slots__ = ["delete_time", "donuts_fee_agreement", "name", "other_information", "post_data", "pre_data", "registry_name", "restore_reason", "restore_time", "statement_1", "statement_2"]
    DELETE_TIME_FIELD_NUMBER: _ClassVar[int]
    DONUTS_FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OTHER_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    POST_DATA_FIELD_NUMBER: _ClassVar[int]
    PRE_DATA_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    RESTORE_REASON_FIELD_NUMBER: _ClassVar[int]
    RESTORE_TIME_FIELD_NUMBER: _ClassVar[int]
    STATEMENT_1_FIELD_NUMBER: _ClassVar[int]
    STATEMENT_2_FIELD_NUMBER: _ClassVar[int]
    delete_time: _timestamp_pb2.Timestamp
    donuts_fee_agreement: _fee_pb2.DonutsFeeData
    name: str
    other_information: str
    post_data: str
    pre_data: str
    registry_name: _wrappers_pb2.StringValue
    restore_reason: str
    restore_time: _timestamp_pb2.Timestamp
    statement_1: str
    statement_2: str
    def __init__(self, name: _Optional[str] = ..., pre_data: _Optional[str] = ..., post_data: _Optional[str] = ..., delete_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., restore_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., restore_reason: _Optional[str] = ..., statement_1: _Optional[str] = ..., statement_2: _Optional[str] = ..., other_information: _Optional[str] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., donuts_fee_agreement: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ...) -> None: ...

class RequestRequest(_message.Message):
    __slots__ = ["donuts_fee_agreement", "name", "registry_name"]
    DONUTS_FEE_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    donuts_fee_agreement: _fee_pb2.DonutsFeeData
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., donuts_fee_agreement: _Optional[_Union[_fee_pb2.DonutsFeeData, _Mapping]] = ...) -> None: ...

class RestoreReply(_message.Message):
    __slots__ = ["cmd_resp", "fee_data", "pending", "registry_name", "state"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    FEE_DATA_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    fee_data: _fee_pb2.FeeData
    pending: bool
    registry_name: str
    state: _containers.RepeatedScalarFieldContainer[RGPState]
    def __init__(self, pending: bool = ..., state: _Optional[_Iterable[_Union[RGPState, str]]] = ..., fee_data: _Optional[_Union[_fee_pb2.FeeData, _Mapping]] = ..., registry_name: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class RGPState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
