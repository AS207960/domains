from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from common import common_pb2 as _common_pb2
from marks import marks_pb2 as _marks_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

AssigneeDeclaration: DocumentClass
CopyOfCourtOrder: DocumentClass
Corrected: MarkStatusType
CourtDecision: CourtDocumentClass
CourtOther: CourtDocumentClass
DESCRIPTOR: _descriptor.FileDescriptor
Deactivated: MarkStatusType
DeclarationProofOfUseOneSample: DocumentClass
Eligible: TrexStatus
Expired: MarkStatusType
Incorrect: MarkStatusType
Invalid: MarkStatusType
JPG: FileType
LicenseeDeclaration: DocumentClass
New: MarkStatusType
NoInfo: TrexStatus
NotProtectedExempt: TrexStatus
NotProtectedOther: TrexStatus
NotProtectedOverride: TrexStatus
NotProtectedRegistered: TrexStatus
Other: DocumentClass
OtherProofOfUse: DocumentClass
PDF: FileType
POUCorrected: MarkPOUStatusType
POUExpired: MarkPOUStatusType
POUIncorrect: MarkPOUStatusType
POUInvalid: MarkPOUStatusType
POUNA: MarkPOUStatusType
POUNew: MarkPOUStatusType
POUNotSet: MarkPOUStatusType
POUValid: MarkPOUStatusType
Protected: TrexStatus
Unavailable: TrexStatus
Unknown: MarkStatusType
Verified: MarkStatusType

class AddCase(_message.Message):
    __slots__ = ["court", "documents", "id", "labels", "udrp"]
    COURT_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    UDRP_FIELD_NUMBER: _ClassVar[int]
    court: CourtCase
    documents: _containers.RepeatedCompositeFieldContainer[CaseDocument]
    id: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    udrp: UDRPCase
    def __init__(self, id: _Optional[str] = ..., udrp: _Optional[_Union[UDRPCase, _Mapping]] = ..., court: _Optional[_Union[CourtCase, _Mapping]] = ..., documents: _Optional[_Iterable[_Union[CaseDocument, _Mapping]]] = ..., labels: _Optional[_Iterable[str]] = ...) -> None: ...

class BalanceData(_message.Message):
    __slots__ = ["currency", "status_points", "value"]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    STATUS_POINTS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    currency: str
    status_points: int
    value: str
    def __init__(self, value: _Optional[str] = ..., currency: _Optional[str] = ..., status_points: _Optional[int] = ...) -> None: ...

class CaseAdd(_message.Message):
    __slots__ = ["document", "label"]
    DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    document: CaseDocument
    label: str
    def __init__(self, document: _Optional[_Union[CaseDocument, _Mapping]] = ..., label: _Optional[str] = ...) -> None: ...

class CaseDocument(_message.Message):
    __slots__ = ["contents", "document_class", "file_name", "file_type"]
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_CLASS_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FILE_TYPE_FIELD_NUMBER: _ClassVar[int]
    contents: bytes
    document_class: CourtDocumentClass
    file_name: str
    file_type: FileType
    def __init__(self, document_class: _Optional[_Union[CourtDocumentClass, str]] = ..., file_name: _Optional[str] = ..., file_type: _Optional[_Union[FileType, str]] = ..., contents: _Optional[bytes] = ...) -> None: ...

class CaseRemove(_message.Message):
    __slots__ = ["label"]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    label: str
    def __init__(self, label: _Optional[str] = ...) -> None: ...

class CaseUpdate(_message.Message):
    __slots__ = ["add", "id", "new_court", "new_udrp", "remove"]
    ADD_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NEW_COURT_FIELD_NUMBER: _ClassVar[int]
    NEW_UDRP_FIELD_NUMBER: _ClassVar[int]
    REMOVE_FIELD_NUMBER: _ClassVar[int]
    add: _containers.RepeatedCompositeFieldContainer[CaseAdd]
    id: str
    new_court: CourtCase
    new_udrp: UDRPCase
    remove: _containers.RepeatedCompositeFieldContainer[CaseRemove]
    def __init__(self, id: _Optional[str] = ..., add: _Optional[_Iterable[_Union[CaseAdd, _Mapping]]] = ..., remove: _Optional[_Iterable[_Union[CaseRemove, _Mapping]]] = ..., new_udrp: _Optional[_Union[UDRPCase, _Mapping]] = ..., new_court: _Optional[_Union[CourtCase, _Mapping]] = ...) -> None: ...

class CourtCase(_message.Message):
    __slots__ = ["case_language", "country_code", "court_name", "decision_id", "regions"]
    CASE_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_CODE_FIELD_NUMBER: _ClassVar[int]
    COURT_NAME_FIELD_NUMBER: _ClassVar[int]
    DECISION_ID_FIELD_NUMBER: _ClassVar[int]
    REGIONS_FIELD_NUMBER: _ClassVar[int]
    case_language: str
    country_code: str
    court_name: str
    decision_id: str
    regions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, decision_id: _Optional[str] = ..., court_name: _Optional[str] = ..., country_code: _Optional[str] = ..., case_language: _Optional[str] = ..., regions: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateLabel(_message.Message):
    __slots__ = ["claims_notify", "label", "smd_inclusion"]
    CLAIMS_NOTIFY_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    SMD_INCLUSION_FIELD_NUMBER: _ClassVar[int]
    claims_notify: bool
    label: str
    smd_inclusion: bool
    def __init__(self, label: _Optional[str] = ..., smd_inclusion: bool = ..., claims_notify: bool = ...) -> None: ...

class Document(_message.Message):
    __slots__ = ["contents", "document_class", "file_name", "file_type"]
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_CLASS_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FILE_TYPE_FIELD_NUMBER: _ClassVar[int]
    contents: bytes
    document_class: DocumentClass
    file_name: str
    file_type: FileType
    def __init__(self, document_class: _Optional[_Union[DocumentClass, str]] = ..., file_name: _Optional[str] = ..., file_type: _Optional[_Union[FileType, str]] = ..., contents: _Optional[bytes] = ...) -> None: ...

class MarkCheckRequest(_message.Message):
    __slots__ = ["id", "registry_name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class MarkCheckResponse(_message.Message):
    __slots__ = ["available", "cmd_resp", "reason"]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    available: bool
    cmd_resp: _common_pb2.CommandResponse
    reason: _wrappers_pb2.StringValue
    def __init__(self, available: bool = ..., reason: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MarkCreateRequest(_message.Message):
    __slots__ = ["documents", "labels", "mark", "period", "registry_name", "variations"]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    MARK_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    VARIATIONS_FIELD_NUMBER: _ClassVar[int]
    documents: _containers.RepeatedCompositeFieldContainer[Document]
    labels: _containers.RepeatedCompositeFieldContainer[CreateLabel]
    mark: _marks_pb2.Mark
    period: _common_pb2.Period
    registry_name: str
    variations: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, mark: _Optional[_Union[_marks_pb2.Mark, _Mapping]] = ..., period: _Optional[_Union[_common_pb2.Period, _Mapping]] = ..., documents: _Optional[_Iterable[_Union[Document, _Mapping]]] = ..., labels: _Optional[_Iterable[_Union[CreateLabel, _Mapping]]] = ..., variations: _Optional[_Iterable[str]] = ..., registry_name: _Optional[str] = ...) -> None: ...

class MarkCreateResponse(_message.Message):
    __slots__ = ["balance", "cmd_resp", "created_date", "id"]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CREATED_DATE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    balance: BalanceData
    cmd_resp: _common_pb2.CommandResponse
    created_date: _timestamp_pb2.Timestamp
    id: str
    def __init__(self, id: _Optional[str] = ..., created_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., balance: _Optional[_Union[BalanceData, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MarkInfoRequest(_message.Message):
    __slots__ = ["id", "registry_name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class MarkInfoResponse(_message.Message):
    __slots__ = ["cmd_resp", "correct_before", "creation_date", "expiry_date", "id", "labels", "pou_expiry_date", "pou_status", "status", "update_date", "variations"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CORRECT_BEFORE_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    POU_EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    POU_STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    UPDATE_DATE_FIELD_NUMBER: _ClassVar[int]
    VARIATIONS_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    correct_before: _timestamp_pb2.Timestamp
    creation_date: _timestamp_pb2.Timestamp
    expiry_date: _timestamp_pb2.Timestamp
    id: str
    labels: _containers.RepeatedCompositeFieldContainer[MarkLabel]
    pou_expiry_date: _timestamp_pb2.Timestamp
    pou_status: MarkPOUStatus
    status: MarkStatus
    update_date: _timestamp_pb2.Timestamp
    variations: _containers.RepeatedCompositeFieldContainer[MarkVariation]
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[MarkStatus, _Mapping]] = ..., pou_status: _Optional[_Union[MarkPOUStatus, _Mapping]] = ..., labels: _Optional[_Iterable[_Union[MarkLabel, _Mapping]]] = ..., variations: _Optional[_Iterable[_Union[MarkVariation, _Mapping]]] = ..., creation_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., update_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., pou_expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., correct_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MarkLabel(_message.Message):
    __slots__ = ["a_label", "claim_notify", "smd_inclusion", "u_label"]
    A_LABEL_FIELD_NUMBER: _ClassVar[int]
    CLAIM_NOTIFY_FIELD_NUMBER: _ClassVar[int]
    SMD_INCLUSION_FIELD_NUMBER: _ClassVar[int]
    U_LABEL_FIELD_NUMBER: _ClassVar[int]
    a_label: str
    claim_notify: bool
    smd_inclusion: bool
    u_label: str
    def __init__(self, a_label: _Optional[str] = ..., u_label: _Optional[str] = ..., smd_inclusion: bool = ..., claim_notify: bool = ...) -> None: ...

class MarkLabelTrex(_message.Message):
    __slots__ = ["enabled", "tlds", "until"]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    TLDS_FIELD_NUMBER: _ClassVar[int]
    UNTIL_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    tlds: _containers.RepeatedCompositeFieldContainer[MarkLabelTrexTLD]
    until: _timestamp_pb2.Timestamp
    def __init__(self, enabled: bool = ..., until: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., tlds: _Optional[_Iterable[_Union[MarkLabelTrexTLD, _Mapping]]] = ...) -> None: ...

class MarkLabelTrexTLD(_message.Message):
    __slots__ = ["comment", "status", "tld"]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TLD_FIELD_NUMBER: _ClassVar[int]
    comment: _wrappers_pb2.StringValue
    status: TrexStatus
    tld: str
    def __init__(self, tld: _Optional[str] = ..., comment: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., status: _Optional[_Union[TrexStatus, str]] = ...) -> None: ...

class MarkPOUStatus(_message.Message):
    __slots__ = ["message", "status_type"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_TYPE_FIELD_NUMBER: _ClassVar[int]
    message: _wrappers_pb2.StringValue
    status_type: MarkPOUStatusType
    def __init__(self, status_type: _Optional[_Union[MarkPOUStatusType, str]] = ..., message: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class MarkRenewRequest(_message.Message):
    __slots__ = ["add_period", "current_expiry_date", "id", "registry_name"]
    ADD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    CURRENT_EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    add_period: _common_pb2.Period
    current_expiry_date: _timestamp_pb2.Timestamp
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., add_period: _Optional[_Union[_common_pb2.Period, _Mapping]] = ..., current_expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., registry_name: _Optional[str] = ...) -> None: ...

class MarkRenewResponse(_message.Message):
    __slots__ = ["balance", "cmd_resp", "id", "new_expiry_date"]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NEW_EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    balance: BalanceData
    cmd_resp: _common_pb2.CommandResponse
    id: str
    new_expiry_date: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., new_expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., balance: _Optional[_Union[BalanceData, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MarkSMDInfoResponse(_message.Message):
    __slots__ = ["cmd_resp", "id", "smd", "smd_id", "status"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    SMD_FIELD_NUMBER: _ClassVar[int]
    SMD_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    id: str
    smd: str
    smd_id: str
    status: MarkStatus
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[MarkStatus, _Mapping]] = ..., smd_id: _Optional[str] = ..., smd: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MarkStatus(_message.Message):
    __slots__ = ["message", "status_type"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_TYPE_FIELD_NUMBER: _ClassVar[int]
    message: _wrappers_pb2.StringValue
    status_type: MarkStatusType
    def __init__(self, status_type: _Optional[_Union[MarkStatusType, str]] = ..., message: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class MarkTransferInitiateRequest(_message.Message):
    __slots__ = ["id", "registry_name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class MarkTransferInitiateResponse(_message.Message):
    __slots__ = ["auth_info", "cmd_resp", "id"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    auth_info: str
    cmd_resp: _common_pb2.CommandResponse
    id: str
    def __init__(self, id: _Optional[str] = ..., auth_info: _Optional[str] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MarkTransferRequest(_message.Message):
    __slots__ = ["auth_info", "id", "registry_name"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    auth_info: str
    id: str
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., auth_info: _Optional[str] = ..., registry_name: _Optional[str] = ...) -> None: ...

class MarkTransferResponse(_message.Message):
    __slots__ = ["balance", "cmd_resp", "id", "transfer_date"]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_DATE_FIELD_NUMBER: _ClassVar[int]
    balance: BalanceData
    cmd_resp: _common_pb2.CommandResponse
    id: str
    transfer_date: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., transfer_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., balance: _Optional[_Union[BalanceData, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MarkTrexActivateRequest(_message.Message):
    __slots__ = ["id", "labels", "registry_name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    labels: _containers.RepeatedCompositeFieldContainer[TrexActivateLabel]
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., labels: _Optional[_Iterable[_Union[TrexActivateLabel, _Mapping]]] = ..., registry_name: _Optional[str] = ...) -> None: ...

class MarkTrexActivateResponse(_message.Message):
    __slots__ = ["cmd_resp"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    def __init__(self, cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MarkTrexRenewRequest(_message.Message):
    __slots__ = ["id", "labels", "registry_name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    labels: _containers.RepeatedCompositeFieldContainer[TrexRenewLabel]
    registry_name: str
    def __init__(self, id: _Optional[str] = ..., labels: _Optional[_Iterable[_Union[TrexRenewLabel, _Mapping]]] = ..., registry_name: _Optional[str] = ...) -> None: ...

class MarkTrexRenewResponse(_message.Message):
    __slots__ = ["cmd_resp"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    def __init__(self, cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MarkUpdateAdd(_message.Message):
    __slots__ = ["case", "document", "label", "variation"]
    CASE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    VARIATION_FIELD_NUMBER: _ClassVar[int]
    case: AddCase
    document: Document
    label: CreateLabel
    variation: str
    def __init__(self, document: _Optional[_Union[Document, _Mapping]] = ..., label: _Optional[_Union[CreateLabel, _Mapping]] = ..., variation: _Optional[str] = ..., case: _Optional[_Union[AddCase, _Mapping]] = ...) -> None: ...

class MarkUpdateRemove(_message.Message):
    __slots__ = ["label", "variation"]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    VARIATION_FIELD_NUMBER: _ClassVar[int]
    label: str
    variation: str
    def __init__(self, label: _Optional[str] = ..., variation: _Optional[str] = ...) -> None: ...

class MarkUpdateRequest(_message.Message):
    __slots__ = ["add", "id", "new_mark", "registry_name", "remove", "update_cases", "update_labels"]
    ADD_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NEW_MARK_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    REMOVE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_CASES_FIELD_NUMBER: _ClassVar[int]
    UPDATE_LABELS_FIELD_NUMBER: _ClassVar[int]
    add: _containers.RepeatedCompositeFieldContainer[MarkUpdateAdd]
    id: str
    new_mark: _marks_pb2.Mark
    registry_name: str
    remove: _containers.RepeatedCompositeFieldContainer[MarkUpdateRemove]
    update_cases: _containers.RepeatedCompositeFieldContainer[CaseUpdate]
    update_labels: _containers.RepeatedCompositeFieldContainer[CreateLabel]
    def __init__(self, id: _Optional[str] = ..., add: _Optional[_Iterable[_Union[MarkUpdateAdd, _Mapping]]] = ..., remove: _Optional[_Iterable[_Union[MarkUpdateRemove, _Mapping]]] = ..., new_mark: _Optional[_Union[_marks_pb2.Mark, _Mapping]] = ..., update_labels: _Optional[_Iterable[_Union[CreateLabel, _Mapping]]] = ..., update_cases: _Optional[_Iterable[_Union[CaseUpdate, _Mapping]]] = ..., registry_name: _Optional[str] = ...) -> None: ...

class MarkUpdateResponse(_message.Message):
    __slots__ = ["cmd_resp"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    def __init__(self, cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class MarkVariation(_message.Message):
    __slots__ = ["a_label", "active", "u_label", "variation_type"]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    A_LABEL_FIELD_NUMBER: _ClassVar[int]
    U_LABEL_FIELD_NUMBER: _ClassVar[int]
    VARIATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    a_label: str
    active: bool
    u_label: str
    variation_type: str
    def __init__(self, a_label: _Optional[str] = ..., u_label: _Optional[str] = ..., variation_type: _Optional[str] = ..., active: bool = ...) -> None: ...

class TrexActivateLabel(_message.Message):
    __slots__ = ["label", "period"]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    label: str
    period: _common_pb2.Period
    def __init__(self, label: _Optional[str] = ..., period: _Optional[_Union[_common_pb2.Period, _Mapping]] = ...) -> None: ...

class TrexRenewLabel(_message.Message):
    __slots__ = ["add_period", "current_expiry_date", "label"]
    ADD_PERIOD_FIELD_NUMBER: _ClassVar[int]
    CURRENT_EXPIRY_DATE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    add_period: _common_pb2.Period
    current_expiry_date: _timestamp_pb2.Timestamp
    label: str
    def __init__(self, label: _Optional[str] = ..., add_period: _Optional[_Union[_common_pb2.Period, _Mapping]] = ..., current_expiry_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UDRPCase(_message.Message):
    __slots__ = ["case_id", "case_language", "provider"]
    CASE_ID_FIELD_NUMBER: _ClassVar[int]
    CASE_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    case_id: str
    case_language: str
    provider: str
    def __init__(self, case_id: _Optional[str] = ..., provider: _Optional[str] = ..., case_language: _Optional[str] = ...) -> None: ...

class DocumentClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class FileType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class MarkStatusType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class MarkPOUStatusType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class TrexStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class CourtDocumentClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
