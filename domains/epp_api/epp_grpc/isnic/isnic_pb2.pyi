from google.protobuf import wrappers_pb2 as _wrappers_pb2
from common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
Ok: ContactStatus
OkUnconfirmed: ContactStatus
PendingCreate: ContactStatus
ServerExpired: ContactStatus
ServerSuspended: ContactStatus

class ContactCreate(_message.Message):
    __slots__ = ["auto_update_from_national_registry", "lang", "mobile", "paper_invoices", "sid"]
    AUTO_UPDATE_FROM_NATIONAL_REGISTRY_FIELD_NUMBER: _ClassVar[int]
    LANG_FIELD_NUMBER: _ClassVar[int]
    MOBILE_FIELD_NUMBER: _ClassVar[int]
    PAPER_INVOICES_FIELD_NUMBER: _ClassVar[int]
    SID_FIELD_NUMBER: _ClassVar[int]
    auto_update_from_national_registry: bool
    lang: _wrappers_pb2.StringValue
    mobile: _common_pb2.Phone
    paper_invoices: bool
    sid: _wrappers_pb2.StringValue
    def __init__(self, mobile: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., sid: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., auto_update_from_national_registry: bool = ..., paper_invoices: bool = ..., lang: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class ContactInfo(_message.Message):
    __slots__ = ["auto_update_from_national_registry", "mobile", "paper_invoices", "sid", "statuses"]
    AUTO_UPDATE_FROM_NATIONAL_REGISTRY_FIELD_NUMBER: _ClassVar[int]
    MOBILE_FIELD_NUMBER: _ClassVar[int]
    PAPER_INVOICES_FIELD_NUMBER: _ClassVar[int]
    SID_FIELD_NUMBER: _ClassVar[int]
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    auto_update_from_national_registry: bool
    mobile: _common_pb2.Phone
    paper_invoices: bool
    sid: _wrappers_pb2.StringValue
    statuses: _containers.RepeatedScalarFieldContainer[ContactStatus]
    def __init__(self, statuses: _Optional[_Iterable[_Union[ContactStatus, str]]] = ..., mobile: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., sid: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., auto_update_from_national_registry: bool = ..., paper_invoices: bool = ...) -> None: ...

class ContactUpdate(_message.Message):
    __slots__ = ["auto_update_from_national_registry", "lang", "mobile", "paper_invoices", "password"]
    AUTO_UPDATE_FROM_NATIONAL_REGISTRY_FIELD_NUMBER: _ClassVar[int]
    LANG_FIELD_NUMBER: _ClassVar[int]
    MOBILE_FIELD_NUMBER: _ClassVar[int]
    PAPER_INVOICES_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    auto_update_from_national_registry: _wrappers_pb2.BoolValue
    lang: _wrappers_pb2.StringValue
    mobile: _common_pb2.Phone
    paper_invoices: _wrappers_pb2.BoolValue
    password: str
    def __init__(self, mobile: _Optional[_Union[_common_pb2.Phone, _Mapping]] = ..., auto_update_from_national_registry: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., paper_invoices: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., lang: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., password: _Optional[str] = ...) -> None: ...

class DomainInfo(_message.Message):
    __slots__ = ["zone_contact"]
    ZONE_CONTACT_FIELD_NUMBER: _ClassVar[int]
    zone_contact: _wrappers_pb2.StringValue
    def __init__(self, zone_contact: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainUpdate(_message.Message):
    __slots__ = ["new_master_ns", "remove_all_ns"]
    NEW_MASTER_NS_FIELD_NUMBER: _ClassVar[int]
    REMOVE_ALL_NS_FIELD_NUMBER: _ClassVar[int]
    new_master_ns: _containers.RepeatedScalarFieldContainer[str]
    remove_all_ns: bool
    def __init__(self, remove_all_ns: bool = ..., new_master_ns: _Optional[_Iterable[str]] = ...) -> None: ...

class HostInfo(_message.Message):
    __slots__ = ["zone_contact"]
    ZONE_CONTACT_FIELD_NUMBER: _ClassVar[int]
    zone_contact: _wrappers_pb2.StringValue
    def __init__(self, zone_contact: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class PaymentInfo(_message.Message):
    __slots__ = ["card", "prepaid"]
    class Card(_message.Message):
        __slots__ = ["cvc", "id"]
        CVC_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        cvc: str
        id: int
        def __init__(self, id: _Optional[int] = ..., cvc: _Optional[str] = ...) -> None: ...
    CARD_FIELD_NUMBER: _ClassVar[int]
    PREPAID_FIELD_NUMBER: _ClassVar[int]
    card: PaymentInfo.Card
    prepaid: int
    def __init__(self, prepaid: _Optional[int] = ..., card: _Optional[_Union[PaymentInfo.Card, _Mapping]] = ...) -> None: ...

class ContactStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
