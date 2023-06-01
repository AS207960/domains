"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.message
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class PersonalRegistrationCreate(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    BUNDLED_RATE_FIELD_NUMBER: builtins.int
    bundled_rate: builtins.bool
    def __init__(
        self,
        *,
        bundled_rate: builtins.bool = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["bundled_rate", b"bundled_rate"]) -> None: ...

global___PersonalRegistrationCreate = PersonalRegistrationCreate

@typing_extensions.final
class PersonalRegistrationInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CONSENT_ID_FIELD_NUMBER: builtins.int
    consent_id: builtins.str
    def __init__(
        self,
        *,
        consent_id: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["consent_id", b"consent_id"]) -> None: ...

global___PersonalRegistrationInfo = PersonalRegistrationInfo
