from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from common import common_pb2 as _common_pb2
from domain_common import domain_common_pb2 as _domain_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

Billing: ContactType
DESCRIPTOR: _descriptor.FileDescriptor
OnSite: ContactType
Registrant: ContactType
Reseller: ContactType
Tech: ContactType

class ContactExtension(_message.Message):
    __slots__ = ["citizenship_country", "contact_type", "language", "vat", "whois_email"]
    CITIZENSHIP_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    CONTACT_TYPE_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    VAT_FIELD_NUMBER: _ClassVar[int]
    WHOIS_EMAIL_FIELD_NUMBER: _ClassVar[int]
    citizenship_country: _wrappers_pb2.StringValue
    contact_type: ContactType
    language: str
    vat: _wrappers_pb2.StringValue
    whois_email: _wrappers_pb2.StringValue
    def __init__(self, contact_type: _Optional[_Union[ContactType, str]] = ..., whois_email: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., vat: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., citizenship_country: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., language: _Optional[str] = ...) -> None: ...

class ContactUpdateExtension(_message.Message):
    __slots__ = ["new_citizenship_country", "new_language", "new_vat", "new_whois_email"]
    NEW_CITIZENSHIP_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    NEW_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    NEW_VAT_FIELD_NUMBER: _ClassVar[int]
    NEW_WHOIS_EMAIL_FIELD_NUMBER: _ClassVar[int]
    new_citizenship_country: _wrappers_pb2.StringValue
    new_language: _wrappers_pb2.StringValue
    new_vat: _wrappers_pb2.StringValue
    new_whois_email: _wrappers_pb2.StringValue
    def __init__(self, new_whois_email: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., new_vat: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., new_citizenship_country: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., new_language: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DNSQualityReply(_message.Message):
    __slots__ = ["check_time", "cmd_resp", "registry_name", "score"]
    CHECK_TIME_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    check_time: _timestamp_pb2.Timestamp
    cmd_resp: _common_pb2.CommandResponse
    registry_name: str
    score: str
    def __init__(self, score: _Optional[str] = ..., check_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ..., registry_name: _Optional[str] = ...) -> None: ...

class DNSQualityRequest(_message.Message):
    __slots__ = ["name", "registry_name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DNSSECEligibilityReply(_message.Message):
    __slots__ = ["cmd_resp", "code", "eligible", "message", "registry_name"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    ELIGIBLE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    code: int
    eligible: bool
    message: str
    registry_name: str
    def __init__(self, eligible: bool = ..., message: _Optional[str] = ..., code: _Optional[int] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ..., registry_name: _Optional[str] = ...) -> None: ...

class DNSSECEligibilityRequest(_message.Message):
    __slots__ = ["name", "registry_name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    registry_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[str] = ..., registry_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainCheckData(_message.Message):
    __slots__ = ["available_date", "status"]
    AVAILABLE_DATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    available_date: _timestamp_pb2.Timestamp
    status: _containers.RepeatedScalarFieldContainer[_domain_common_pb2.DomainStatus]
    def __init__(self, available_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[_Iterable[_Union[_domain_common_pb2.DomainStatus, str]]] = ...) -> None: ...

class DomainCreateExtension(_message.Message):
    __slots__ = ["on_site", "reseller"]
    ON_SITE_FIELD_NUMBER: _ClassVar[int]
    RESELLER_FIELD_NUMBER: _ClassVar[int]
    on_site: _wrappers_pb2.StringValue
    reseller: _wrappers_pb2.StringValue
    def __init__(self, on_site: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., reseller: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainDeleteExtension(_message.Message):
    __slots__ = ["cancel", "schedule"]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    cancel: bool
    schedule: _timestamp_pb2.Timestamp
    def __init__(self, schedule: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cancel: bool = ...) -> None: ...

class DomainInfo(_message.Message):
    __slots__ = ["auth_info_valid_until", "delayed", "deletion_date", "max_extension_period", "on_hold", "on_site", "quarantined", "registrant_country", "registrant_country_of_citizenship", "reseller", "seized", "suspended"]
    AUTH_INFO_VALID_UNTIL_FIELD_NUMBER: _ClassVar[int]
    DELAYED_FIELD_NUMBER: _ClassVar[int]
    DELETION_DATE_FIELD_NUMBER: _ClassVar[int]
    MAX_EXTENSION_PERIOD_FIELD_NUMBER: _ClassVar[int]
    ON_HOLD_FIELD_NUMBER: _ClassVar[int]
    ON_SITE_FIELD_NUMBER: _ClassVar[int]
    QUARANTINED_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_COUNTRY_OF_CITIZENSHIP_FIELD_NUMBER: _ClassVar[int]
    RESELLER_FIELD_NUMBER: _ClassVar[int]
    SEIZED_FIELD_NUMBER: _ClassVar[int]
    SUSPENDED_FIELD_NUMBER: _ClassVar[int]
    auth_info_valid_until: _timestamp_pb2.Timestamp
    delayed: bool
    deletion_date: _timestamp_pb2.Timestamp
    max_extension_period: int
    on_hold: bool
    on_site: _wrappers_pb2.StringValue
    quarantined: bool
    registrant_country: str
    registrant_country_of_citizenship: _wrappers_pb2.StringValue
    reseller: _wrappers_pb2.StringValue
    seized: bool
    suspended: bool
    def __init__(self, on_hold: bool = ..., quarantined: bool = ..., suspended: bool = ..., delayed: bool = ..., seized: bool = ..., deletion_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., on_site: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., reseller: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., max_extension_period: _Optional[int] = ..., registrant_country: _Optional[str] = ..., registrant_country_of_citizenship: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., auth_info_valid_until: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DomainInfoRequest(_message.Message):
    __slots__ = ["cancel", "request"]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    cancel: bool
    request: bool
    def __init__(self, request: bool = ..., cancel: bool = ...) -> None: ...

class DomainRenewInfo(_message.Message):
    __slots__ = ["removed_deletion"]
    REMOVED_DELETION_FIELD_NUMBER: _ClassVar[int]
    removed_deletion: bool
    def __init__(self, removed_deletion: bool = ...) -> None: ...

class DomainTransferExtension(_message.Message):
    __slots__ = ["billing", "on_site", "registrant", "reseller", "technical"]
    BILLING_FIELD_NUMBER: _ClassVar[int]
    ON_SITE_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_FIELD_NUMBER: _ClassVar[int]
    RESELLER_FIELD_NUMBER: _ClassVar[int]
    TECHNICAL_FIELD_NUMBER: _ClassVar[int]
    billing: str
    on_site: _wrappers_pb2.StringValue
    registrant: str
    reseller: _wrappers_pb2.StringValue
    technical: _wrappers_pb2.StringValue
    def __init__(self, registrant: _Optional[str] = ..., billing: _Optional[str] = ..., technical: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., reseller: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., on_site: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainTransferInfo(_message.Message):
    __slots__ = ["billing", "delayed", "on_hold", "on_site", "quarantined", "reason", "registrant", "reseller", "technical"]
    BILLING_FIELD_NUMBER: _ClassVar[int]
    DELAYED_FIELD_NUMBER: _ClassVar[int]
    ON_HOLD_FIELD_NUMBER: _ClassVar[int]
    ON_SITE_FIELD_NUMBER: _ClassVar[int]
    QUARANTINED_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_FIELD_NUMBER: _ClassVar[int]
    RESELLER_FIELD_NUMBER: _ClassVar[int]
    TECHNICAL_FIELD_NUMBER: _ClassVar[int]
    billing: str
    delayed: bool
    on_hold: bool
    on_site: _wrappers_pb2.StringValue
    quarantined: bool
    reason: str
    registrant: str
    reseller: _wrappers_pb2.StringValue
    technical: _wrappers_pb2.StringValue
    def __init__(self, on_hold: bool = ..., quarantined: bool = ..., delayed: bool = ..., reason: _Optional[str] = ..., registrant: _Optional[str] = ..., billing: _Optional[str] = ..., on_site: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., technical: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., reseller: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainUpdateExtension(_message.Message):
    __slots__ = ["add_on_site", "add_reseller", "remove_on_site", "remove_reseller"]
    ADD_ON_SITE_FIELD_NUMBER: _ClassVar[int]
    ADD_RESELLER_FIELD_NUMBER: _ClassVar[int]
    REMOVE_ON_SITE_FIELD_NUMBER: _ClassVar[int]
    REMOVE_RESELLER_FIELD_NUMBER: _ClassVar[int]
    add_on_site: _wrappers_pb2.StringValue
    add_reseller: _wrappers_pb2.StringValue
    remove_on_site: _wrappers_pb2.StringValue
    remove_reseller: _wrappers_pb2.StringValue
    def __init__(self, add_on_site: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., add_reseller: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., remove_on_site: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., remove_reseller: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class HitPointsReply(_message.Message):
    __slots__ = ["blocked_until", "cmd_resp", "hit_points", "max_hit_points"]
    BLOCKED_UNTIL_FIELD_NUMBER: _ClassVar[int]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    HIT_POINTS_FIELD_NUMBER: _ClassVar[int]
    MAX_HIT_POINTS_FIELD_NUMBER: _ClassVar[int]
    blocked_until: _timestamp_pb2.Timestamp
    cmd_resp: _common_pb2.CommandResponse
    hit_points: int
    max_hit_points: int
    def __init__(self, hit_points: _Optional[int] = ..., max_hit_points: _Optional[int] = ..., blocked_until: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class IDN(_message.Message):
    __slots__ = ["ace", "unicode"]
    ACE_FIELD_NUMBER: _ClassVar[int]
    UNICODE_FIELD_NUMBER: _ClassVar[int]
    ace: str
    unicode: str
    def __init__(self, ace: _Optional[str] = ..., unicode: _Optional[str] = ...) -> None: ...

class PollReply(_message.Message):
    __slots__ = ["action", "code", "context", "detail", "object", "object_type", "object_unicode", "registrar"]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_UNICODE_FIELD_NUMBER: _ClassVar[int]
    REGISTRAR_FIELD_NUMBER: _ClassVar[int]
    action: str
    code: int
    context: str
    detail: _wrappers_pb2.StringValue
    object: str
    object_type: str
    object_unicode: _wrappers_pb2.StringValue
    registrar: _wrappers_pb2.StringValue
    def __init__(self, context: _Optional[str] = ..., object_type: _Optional[str] = ..., object: _Optional[str] = ..., object_unicode: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., action: _Optional[str] = ..., code: _Optional[int] = ..., detail: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., registrar: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class RegistrationLimitReply(_message.Message):
    __slots__ = ["cmd_resp", "limited_until", "max_monthly_registrations", "monthly_registrations"]
    CMD_RESP_FIELD_NUMBER: _ClassVar[int]
    LIMITED_UNTIL_FIELD_NUMBER: _ClassVar[int]
    MAX_MONTHLY_REGISTRATIONS_FIELD_NUMBER: _ClassVar[int]
    MONTHLY_REGISTRATIONS_FIELD_NUMBER: _ClassVar[int]
    cmd_resp: _common_pb2.CommandResponse
    limited_until: _timestamp_pb2.Timestamp
    max_monthly_registrations: _wrappers_pb2.UInt64Value
    monthly_registrations: int
    def __init__(self, monthly_registrations: _Optional[int] = ..., max_monthly_registrations: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., limited_until: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cmd_resp: _Optional[_Union[_common_pb2.CommandResponse, _Mapping]] = ...) -> None: ...

class ContactType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
