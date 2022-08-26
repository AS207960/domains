from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PersonalRegistrationCreate(_message.Message):
    __slots__ = ["bundled_rate"]
    BUNDLED_RATE_FIELD_NUMBER: _ClassVar[int]
    bundled_rate: bool
    def __init__(self, bundled_rate: bool = ...) -> None: ...

class PersonalRegistrationInfo(_message.Message):
    __slots__ = ["consent_id"]
    CONSENT_ID_FIELD_NUMBER: _ClassVar[int]
    consent_id: str
    def __init__(self, consent_id: _Optional[str] = ...) -> None: ...
