# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: nominet/nominet.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from ..domain import domain_pb2 as domain_dot_domain__pb2
from ..contact import contact_pb2 as contact_dot_contact__pb2
from ..common import common_pb2 as common_dot_common__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15nominet/nominet.proto\x12\x0b\x65pp.nominet\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x13\x64omain/domain.proto\x1a\x15\x63ontact/contact.proto\x1a\x13\x63ommon/common.proto\"r\n\x16HandshakeAcceptRequest\x12\x15\n\rregistry_name\x18\x01 \x01(\t\x12\x0f\n\x07\x63\x61se_id\x18\x02 \x01(\t\x12\x30\n\nregistrant\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"@\n\x16HandshakeRejectRequest\x12\x15\n\rregistry_name\x18\x01 \x01(\t\x12\x0f\n\x07\x63\x61se_id\x18\x02 \x01(\t\"a\n\x0eHandshakeReply\x12\x0f\n\x07\x63\x61se_id\x18\x01 \x01(\t\x12\x0f\n\x07\x64omains\x18\x02 \x03(\t\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"c\n\x0eReleaseRequest\x12\x15\n\rregistry_name\x18\x01 \x01(\t\x12\x15\n\rregistrar_tag\x18\x02 \x01(\t\x12#\n\x06object\x18\x03 \x01(\x0b\x32\x13.epp.nominet.Object\":\n\x06Object\x12\x10\n\x06\x64omain\x18\x03 \x01(\tH\x00\x12\x14\n\nregistrant\x18\x04 \x01(\tH\x00\x42\x08\n\x06object\"}\n\x0cReleaseReply\x12\x0f\n\x07pending\x18\x01 \x01(\x08\x12-\n\x07message\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"\xe1\x01\n\x13NominetTagListReply\x12\x32\n\x04tags\x18\x01 \x03(\x0b\x32$.epp.nominet.NominetTagListReply.Tag\x12-\n\x08\x63md_resp\x18\x02 \x01(\x0b\x32\x1b.epp.common.CommandResponse\x1ag\n\x03Tag\x12\x0b\n\x03tag\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x32\n\x0ctrading_name\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x11\n\thandshake\x18\x04 \x01(\x08\"0\n\x0c\x44omainCancel\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x12\n\noriginator\x18\x02 \x01(\t\"p\n\rDomainRelease\x12\x12\n\naccount_id\x18\x01 \x01(\t\x12\x15\n\raccount_moved\x18\x02 \x01(\x08\x12\x0c\n\x04\x66rom\x18\x03 \x01(\t\x12\x15\n\rregistrar_tag\x18\x04 \x01(\t\x12\x0f\n\x07\x64omains\x18\x05 \x03(\t\"\xcf\x01\n\x15\x44omainRegistrarChange\x12\x12\n\noriginator\x18\x01 \x01(\t\x12\x15\n\rregistrar_tag\x18\x02 \x01(\t\x12-\n\x07\x63\x61se_id\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12,\n\x07\x64omains\x18\x04 \x03(\x0b\x32\x1b.epp.domain.DomainInfoReply\x12.\n\x07\x63ontact\x18\x05 \x01(\x0b\x32\x1d.epp.contact.ContactInfoReply\"8\n\nHostCancel\x12\x14\n\x0chost_objects\x18\x01 \x03(\t\x12\x14\n\x0c\x64omain_names\x18\x02 \x03(\t\"\xa4\x02\n\x07Process\x12\x30\n\x05stage\x18\x01 \x01(\x0e\x32!.epp.nominet.Process.ProcessStage\x12.\n\x07\x63ontact\x18\x02 \x01(\x0b\x32\x1d.epp.contact.ContactInfoReply\x12\x14\n\x0cprocess_type\x18\x03 \x01(\t\x12\x30\n\x0csuspend_date\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12/\n\x0b\x63\x61ncel_date\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x14\n\x0c\x64omain_names\x18\x06 \x03(\t\"(\n\x0cProcessStage\x12\x0b\n\x07Initial\x10\x00\x12\x0b\n\x07Updated\x10\x01\"`\n\x07Suspend\x12\x0e\n\x06reason\x18\x01 \x01(\t\x12/\n\x0b\x63\x61ncel_date\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x14\n\x0c\x64omain_names\x18\x03 \x03(\t\",\n\nDomainFail\x12\x0e\n\x06\x64omain\x18\x01 \x01(\t\x12\x0e\n\x06reason\x18\x02 \x01(\t\"\xc9\x01\n\x12RegistrantTransfer\x12\x12\n\noriginator\x18\x01 \x01(\t\x12\x12\n\naccount_id\x18\x02 \x01(\t\x12\x16\n\x0eold_account_id\x18\x03 \x01(\t\x12-\n\x07\x63\x61se_id\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x14\n\x0c\x64omain_names\x18\x05 \x03(\t\x12.\n\x07\x63ontact\x18\x06 \x01(\x0b\x32\x1d.epp.contact.ContactInfoReply\"C\n\x16\x43ontactValidateRequest\x12\x15\n\rregistry_name\x18\x01 \x01(\t\x12\x12\n\ncontact_id\x18\x02 \x01(\t\"E\n\x14\x43ontactValidateReply\x12-\n\x08\x63md_resp\x18\x01 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"\\\n\x0bLockRequest\x12\x15\n\rregistry_name\x18\x01 \x01(\t\x12\x11\n\tlock_type\x18\x02 \x01(\t\x12#\n\x06object\x18\x03 \x01(\x0b\x32\x13.epp.nominet.Object\":\n\tLockReply\x12-\n\x08\x63md_resp\x18\x01 \x01(\x0b\x32\x1b.epp.common.CommandResponseB2Z0github.com/as207960/epp-proxy/gen/go/epp/nominetb\x06proto3')



_HANDSHAKEACCEPTREQUEST = DESCRIPTOR.message_types_by_name['HandshakeAcceptRequest']
_HANDSHAKEREJECTREQUEST = DESCRIPTOR.message_types_by_name['HandshakeRejectRequest']
_HANDSHAKEREPLY = DESCRIPTOR.message_types_by_name['HandshakeReply']
_RELEASEREQUEST = DESCRIPTOR.message_types_by_name['ReleaseRequest']
_OBJECT = DESCRIPTOR.message_types_by_name['Object']
_RELEASEREPLY = DESCRIPTOR.message_types_by_name['ReleaseReply']
_NOMINETTAGLISTREPLY = DESCRIPTOR.message_types_by_name['NominetTagListReply']
_NOMINETTAGLISTREPLY_TAG = _NOMINETTAGLISTREPLY.nested_types_by_name['Tag']
_DOMAINCANCEL = DESCRIPTOR.message_types_by_name['DomainCancel']
_DOMAINRELEASE = DESCRIPTOR.message_types_by_name['DomainRelease']
_DOMAINREGISTRARCHANGE = DESCRIPTOR.message_types_by_name['DomainRegistrarChange']
_HOSTCANCEL = DESCRIPTOR.message_types_by_name['HostCancel']
_PROCESS = DESCRIPTOR.message_types_by_name['Process']
_SUSPEND = DESCRIPTOR.message_types_by_name['Suspend']
_DOMAINFAIL = DESCRIPTOR.message_types_by_name['DomainFail']
_REGISTRANTTRANSFER = DESCRIPTOR.message_types_by_name['RegistrantTransfer']
_CONTACTVALIDATEREQUEST = DESCRIPTOR.message_types_by_name['ContactValidateRequest']
_CONTACTVALIDATEREPLY = DESCRIPTOR.message_types_by_name['ContactValidateReply']
_LOCKREQUEST = DESCRIPTOR.message_types_by_name['LockRequest']
_LOCKREPLY = DESCRIPTOR.message_types_by_name['LockReply']
_PROCESS_PROCESSSTAGE = _PROCESS.enum_types_by_name['ProcessStage']
HandshakeAcceptRequest = _reflection.GeneratedProtocolMessageType('HandshakeAcceptRequest', (_message.Message,), {
  'DESCRIPTOR' : _HANDSHAKEACCEPTREQUEST,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.HandshakeAcceptRequest)
  })
_sym_db.RegisterMessage(HandshakeAcceptRequest)

HandshakeRejectRequest = _reflection.GeneratedProtocolMessageType('HandshakeRejectRequest', (_message.Message,), {
  'DESCRIPTOR' : _HANDSHAKEREJECTREQUEST,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.HandshakeRejectRequest)
  })
_sym_db.RegisterMessage(HandshakeRejectRequest)

HandshakeReply = _reflection.GeneratedProtocolMessageType('HandshakeReply', (_message.Message,), {
  'DESCRIPTOR' : _HANDSHAKEREPLY,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.HandshakeReply)
  })
_sym_db.RegisterMessage(HandshakeReply)

ReleaseRequest = _reflection.GeneratedProtocolMessageType('ReleaseRequest', (_message.Message,), {
  'DESCRIPTOR' : _RELEASEREQUEST,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.ReleaseRequest)
  })
_sym_db.RegisterMessage(ReleaseRequest)

Object = _reflection.GeneratedProtocolMessageType('Object', (_message.Message,), {
  'DESCRIPTOR' : _OBJECT,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.Object)
  })
_sym_db.RegisterMessage(Object)

ReleaseReply = _reflection.GeneratedProtocolMessageType('ReleaseReply', (_message.Message,), {
  'DESCRIPTOR' : _RELEASEREPLY,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.ReleaseReply)
  })
_sym_db.RegisterMessage(ReleaseReply)

NominetTagListReply = _reflection.GeneratedProtocolMessageType('NominetTagListReply', (_message.Message,), {

  'Tag' : _reflection.GeneratedProtocolMessageType('Tag', (_message.Message,), {
    'DESCRIPTOR' : _NOMINETTAGLISTREPLY_TAG,
    '__module__' : 'nominet.nominet_pb2'
    # @@protoc_insertion_point(class_scope:epp.nominet.NominetTagListReply.Tag)
    })
  ,
  'DESCRIPTOR' : _NOMINETTAGLISTREPLY,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.NominetTagListReply)
  })
_sym_db.RegisterMessage(NominetTagListReply)
_sym_db.RegisterMessage(NominetTagListReply.Tag)

DomainCancel = _reflection.GeneratedProtocolMessageType('DomainCancel', (_message.Message,), {
  'DESCRIPTOR' : _DOMAINCANCEL,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.DomainCancel)
  })
_sym_db.RegisterMessage(DomainCancel)

DomainRelease = _reflection.GeneratedProtocolMessageType('DomainRelease', (_message.Message,), {
  'DESCRIPTOR' : _DOMAINRELEASE,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.DomainRelease)
  })
_sym_db.RegisterMessage(DomainRelease)

DomainRegistrarChange = _reflection.GeneratedProtocolMessageType('DomainRegistrarChange', (_message.Message,), {
  'DESCRIPTOR' : _DOMAINREGISTRARCHANGE,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.DomainRegistrarChange)
  })
_sym_db.RegisterMessage(DomainRegistrarChange)

HostCancel = _reflection.GeneratedProtocolMessageType('HostCancel', (_message.Message,), {
  'DESCRIPTOR' : _HOSTCANCEL,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.HostCancel)
  })
_sym_db.RegisterMessage(HostCancel)

Process = _reflection.GeneratedProtocolMessageType('Process', (_message.Message,), {
  'DESCRIPTOR' : _PROCESS,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.Process)
  })
_sym_db.RegisterMessage(Process)

Suspend = _reflection.GeneratedProtocolMessageType('Suspend', (_message.Message,), {
  'DESCRIPTOR' : _SUSPEND,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.Suspend)
  })
_sym_db.RegisterMessage(Suspend)

DomainFail = _reflection.GeneratedProtocolMessageType('DomainFail', (_message.Message,), {
  'DESCRIPTOR' : _DOMAINFAIL,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.DomainFail)
  })
_sym_db.RegisterMessage(DomainFail)

RegistrantTransfer = _reflection.GeneratedProtocolMessageType('RegistrantTransfer', (_message.Message,), {
  'DESCRIPTOR' : _REGISTRANTTRANSFER,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.RegistrantTransfer)
  })
_sym_db.RegisterMessage(RegistrantTransfer)

ContactValidateRequest = _reflection.GeneratedProtocolMessageType('ContactValidateRequest', (_message.Message,), {
  'DESCRIPTOR' : _CONTACTVALIDATEREQUEST,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.ContactValidateRequest)
  })
_sym_db.RegisterMessage(ContactValidateRequest)

ContactValidateReply = _reflection.GeneratedProtocolMessageType('ContactValidateReply', (_message.Message,), {
  'DESCRIPTOR' : _CONTACTVALIDATEREPLY,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.ContactValidateReply)
  })
_sym_db.RegisterMessage(ContactValidateReply)

LockRequest = _reflection.GeneratedProtocolMessageType('LockRequest', (_message.Message,), {
  'DESCRIPTOR' : _LOCKREQUEST,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.LockRequest)
  })
_sym_db.RegisterMessage(LockRequest)

LockReply = _reflection.GeneratedProtocolMessageType('LockReply', (_message.Message,), {
  'DESCRIPTOR' : _LOCKREPLY,
  '__module__' : 'nominet.nominet_pb2'
  # @@protoc_insertion_point(class_scope:epp.nominet.LockReply)
  })
_sym_db.RegisterMessage(LockReply)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z0github.com/as207960/epp-proxy/gen/go/epp/nominet'
  _HANDSHAKEACCEPTREQUEST._serialized_start=168
  _HANDSHAKEACCEPTREQUEST._serialized_end=282
  _HANDSHAKEREJECTREQUEST._serialized_start=284
  _HANDSHAKEREJECTREQUEST._serialized_end=348
  _HANDSHAKEREPLY._serialized_start=350
  _HANDSHAKEREPLY._serialized_end=447
  _RELEASEREQUEST._serialized_start=449
  _RELEASEREQUEST._serialized_end=548
  _OBJECT._serialized_start=550
  _OBJECT._serialized_end=608
  _RELEASEREPLY._serialized_start=610
  _RELEASEREPLY._serialized_end=735
  _NOMINETTAGLISTREPLY._serialized_start=738
  _NOMINETTAGLISTREPLY._serialized_end=963
  _NOMINETTAGLISTREPLY_TAG._serialized_start=860
  _NOMINETTAGLISTREPLY_TAG._serialized_end=963
  _DOMAINCANCEL._serialized_start=965
  _DOMAINCANCEL._serialized_end=1013
  _DOMAINRELEASE._serialized_start=1015
  _DOMAINRELEASE._serialized_end=1127
  _DOMAINREGISTRARCHANGE._serialized_start=1130
  _DOMAINREGISTRARCHANGE._serialized_end=1337
  _HOSTCANCEL._serialized_start=1339
  _HOSTCANCEL._serialized_end=1395
  _PROCESS._serialized_start=1398
  _PROCESS._serialized_end=1690
  _PROCESS_PROCESSSTAGE._serialized_start=1650
  _PROCESS_PROCESSSTAGE._serialized_end=1690
  _SUSPEND._serialized_start=1692
  _SUSPEND._serialized_end=1788
  _DOMAINFAIL._serialized_start=1790
  _DOMAINFAIL._serialized_end=1834
  _REGISTRANTTRANSFER._serialized_start=1837
  _REGISTRANTTRANSFER._serialized_end=2038
  _CONTACTVALIDATEREQUEST._serialized_start=2040
  _CONTACTVALIDATEREQUEST._serialized_end=2107
  _CONTACTVALIDATEREPLY._serialized_start=2109
  _CONTACTVALIDATEREPLY._serialized_end=2178
  _LOCKREQUEST._serialized_start=2180
  _LOCKREQUEST._serialized_end=2272
  _LOCKREPLY._serialized_start=2274
  _LOCKREPLY._serialized_end=2332
# @@protoc_insertion_point(module_scope)
