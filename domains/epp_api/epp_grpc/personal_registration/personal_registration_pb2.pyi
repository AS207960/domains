"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.message
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor = ...

class PersonalRegistrationCreate(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    BUNDLED_RATE_FIELD_NUMBER: builtins.int
    bundled_rate: builtins.bool = ...

    def __init__(self,
        *,
        bundled_rate : builtins.bool = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal[u"bundled_rate",b"bundled_rate"]) -> None: ...
global___PersonalRegistrationCreate = PersonalRegistrationCreate

class PersonalRegistrationInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    CONSENT_ID_FIELD_NUMBER: builtins.int
    consent_id: typing.Text = ...

    def __init__(self,
        *,
        consent_id : typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal[u"consent_id",b"consent_id"]) -> None: ...
global___PersonalRegistrationInfo = PersonalRegistrationInfo
