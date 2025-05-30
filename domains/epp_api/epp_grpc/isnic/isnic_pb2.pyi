"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import builtins
import collections.abc
import common.common_pb2
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import google.protobuf.wrappers_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _ContactStatus:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _ContactStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_ContactStatus.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    Ok: _ContactStatus.ValueType  # 0
    OkUnconfirmed: _ContactStatus.ValueType  # 1
    PendingCreate: _ContactStatus.ValueType  # 2
    ServerExpired: _ContactStatus.ValueType  # 3
    ServerSuspended: _ContactStatus.ValueType  # 4

class ContactStatus(_ContactStatus, metaclass=_ContactStatusEnumTypeWrapper): ...

Ok: ContactStatus.ValueType  # 0
OkUnconfirmed: ContactStatus.ValueType  # 1
PendingCreate: ContactStatus.ValueType  # 2
ServerExpired: ContactStatus.ValueType  # 3
ServerSuspended: ContactStatus.ValueType  # 4
global___ContactStatus = ContactStatus

@typing.final
class PaymentInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing.final
    class Card(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        ID_FIELD_NUMBER: builtins.int
        CVC_FIELD_NUMBER: builtins.int
        id: builtins.int
        cvc: builtins.str
        def __init__(
            self,
            *,
            id: builtins.int = ...,
            cvc: builtins.str = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing.Literal["cvc", b"cvc", "id", b"id"]) -> None: ...

    PREPAID_FIELD_NUMBER: builtins.int
    CARD_FIELD_NUMBER: builtins.int
    prepaid: builtins.int
    @property
    def card(self) -> global___PaymentInfo.Card: ...
    def __init__(
        self,
        *,
        prepaid: builtins.int = ...,
        card: global___PaymentInfo.Card | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["card", b"card", "payment_method", b"payment_method", "prepaid", b"prepaid"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["card", b"card", "payment_method", b"payment_method", "prepaid", b"prepaid"]) -> None: ...
    def WhichOneof(self, oneof_group: typing.Literal["payment_method", b"payment_method"]) -> typing.Literal["prepaid", "card"] | None: ...

global___PaymentInfo = PaymentInfo

@typing.final
class DomainInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ZONE_CONTACT_FIELD_NUMBER: builtins.int
    @property
    def zone_contact(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        zone_contact: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["zone_contact", b"zone_contact"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["zone_contact", b"zone_contact"]) -> None: ...

global___DomainInfo = DomainInfo

@typing.final
class DomainUpdate(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    REMOVE_ALL_NS_FIELD_NUMBER: builtins.int
    NEW_MASTER_NS_FIELD_NUMBER: builtins.int
    remove_all_ns: builtins.bool
    @property
    def new_master_ns(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    def __init__(
        self,
        *,
        remove_all_ns: builtins.bool = ...,
        new_master_ns: collections.abc.Iterable[builtins.str] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["new_master_ns", b"new_master_ns", "remove_all_ns", b"remove_all_ns"]) -> None: ...

global___DomainUpdate = DomainUpdate

@typing.final
class ContactInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    STATUSES_FIELD_NUMBER: builtins.int
    MOBILE_FIELD_NUMBER: builtins.int
    SID_FIELD_NUMBER: builtins.int
    AUTO_UPDATE_FROM_NATIONAL_REGISTRY_FIELD_NUMBER: builtins.int
    PAPER_INVOICES_FIELD_NUMBER: builtins.int
    auto_update_from_national_registry: builtins.bool
    paper_invoices: builtins.bool
    @property
    def statuses(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[global___ContactStatus.ValueType]: ...
    @property
    def mobile(self) -> common.common_pb2.Phone: ...
    @property
    def sid(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        statuses: collections.abc.Iterable[global___ContactStatus.ValueType] | None = ...,
        mobile: common.common_pb2.Phone | None = ...,
        sid: google.protobuf.wrappers_pb2.StringValue | None = ...,
        auto_update_from_national_registry: builtins.bool = ...,
        paper_invoices: builtins.bool = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["mobile", b"mobile", "sid", b"sid"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["auto_update_from_national_registry", b"auto_update_from_national_registry", "mobile", b"mobile", "paper_invoices", b"paper_invoices", "sid", b"sid", "statuses", b"statuses"]) -> None: ...

global___ContactInfo = ContactInfo

@typing.final
class ContactCreate(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    MOBILE_FIELD_NUMBER: builtins.int
    SID_FIELD_NUMBER: builtins.int
    AUTO_UPDATE_FROM_NATIONAL_REGISTRY_FIELD_NUMBER: builtins.int
    PAPER_INVOICES_FIELD_NUMBER: builtins.int
    LANG_FIELD_NUMBER: builtins.int
    auto_update_from_national_registry: builtins.bool
    paper_invoices: builtins.bool
    @property
    def mobile(self) -> common.common_pb2.Phone: ...
    @property
    def sid(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    @property
    def lang(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        mobile: common.common_pb2.Phone | None = ...,
        sid: google.protobuf.wrappers_pb2.StringValue | None = ...,
        auto_update_from_national_registry: builtins.bool = ...,
        paper_invoices: builtins.bool = ...,
        lang: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["lang", b"lang", "mobile", b"mobile", "sid", b"sid"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["auto_update_from_national_registry", b"auto_update_from_national_registry", "lang", b"lang", "mobile", b"mobile", "paper_invoices", b"paper_invoices", "sid", b"sid"]) -> None: ...

global___ContactCreate = ContactCreate

@typing.final
class ContactUpdate(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    MOBILE_FIELD_NUMBER: builtins.int
    AUTO_UPDATE_FROM_NATIONAL_REGISTRY_FIELD_NUMBER: builtins.int
    PAPER_INVOICES_FIELD_NUMBER: builtins.int
    LANG_FIELD_NUMBER: builtins.int
    PASSWORD_FIELD_NUMBER: builtins.int
    password: builtins.str
    @property
    def mobile(self) -> common.common_pb2.Phone: ...
    @property
    def auto_update_from_national_registry(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
    @property
    def paper_invoices(self) -> google.protobuf.wrappers_pb2.BoolValue: ...
    @property
    def lang(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        mobile: common.common_pb2.Phone | None = ...,
        auto_update_from_national_registry: google.protobuf.wrappers_pb2.BoolValue | None = ...,
        paper_invoices: google.protobuf.wrappers_pb2.BoolValue | None = ...,
        lang: google.protobuf.wrappers_pb2.StringValue | None = ...,
        password: builtins.str = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["auto_update_from_national_registry", b"auto_update_from_national_registry", "lang", b"lang", "mobile", b"mobile", "paper_invoices", b"paper_invoices"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["auto_update_from_national_registry", b"auto_update_from_national_registry", "lang", b"lang", "mobile", b"mobile", "paper_invoices", b"paper_invoices", "password", b"password"]) -> None: ...

global___ContactUpdate = ContactUpdate

@typing.final
class HostInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ZONE_CONTACT_FIELD_NUMBER: builtins.int
    @property
    def zone_contact(self) -> google.protobuf.wrappers_pb2.StringValue: ...
    def __init__(
        self,
        *,
        zone_contact: google.protobuf.wrappers_pb2.StringValue | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["zone_contact", b"zone_contact"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["zone_contact", b"zone_contact"]) -> None: ...

global___HostInfo = HostInfo
