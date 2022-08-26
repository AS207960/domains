from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QualifiedLawyer(_message.Message):
    __slots__ = ["accreditation_body", "accreditation_id", "accreditation_year", "jurisdiction_country", "jurisdiction_province"]
    ACCREDITATION_BODY_FIELD_NUMBER: _ClassVar[int]
    ACCREDITATION_ID_FIELD_NUMBER: _ClassVar[int]
    ACCREDITATION_YEAR_FIELD_NUMBER: _ClassVar[int]
    JURISDICTION_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    JURISDICTION_PROVINCE_FIELD_NUMBER: _ClassVar[int]
    accreditation_body: str
    accreditation_id: str
    accreditation_year: int
    jurisdiction_country: str
    jurisdiction_province: _wrappers_pb2.StringValue
    def __init__(self, accreditation_id: _Optional[str] = ..., accreditation_body: _Optional[str] = ..., accreditation_year: _Optional[int] = ..., jurisdiction_country: _Optional[str] = ..., jurisdiction_province: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...
