from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

ClientDeleteProhibited: DomainStatus
ClientHold: DomainStatus
ClientRenewProhibited: DomainStatus
ClientTransferProhibited: DomainStatus
ClientUpdateProhibited: DomainStatus
DESCRIPTOR: _descriptor.FileDescriptor
Inactive: DomainStatus
Ok: DomainStatus
PendingCreate: DomainStatus
PendingDelete: DomainStatus
PendingRenew: DomainStatus
PendingTransfer: DomainStatus
PendingUpdate: DomainStatus
ServerDeleteProhibited: DomainStatus
ServerHold: DomainStatus
ServerRenewProhibited: DomainStatus
ServerTransferProhibited: DomainStatus
ServerUpdateProhibited: DomainStatus

class DomainStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
