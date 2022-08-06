# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: host/host.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from ..common import common_pb2 as common_dot_common__pb2
from ..isnic import isnic_pb2 as isnic_dot_isnic__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fhost/host.proto\x12\x08\x65pp.host\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x13\x63ommon/common.proto\x1a\x11isnic/isnic.proto\"7\n\x10HostCheckRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x02 \x01(\t\"\x80\x01\n\x0eHostCheckReply\x12\x11\n\tavailable\x18\x01 \x01(\x08\x12,\n\x06reason\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"6\n\x0fHostInfoRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x02 \x01(\t\"\xdc\x03\n\rHostInfoReply\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0bregistry_id\x18\x02 \x01(\t\x12&\n\x08statuses\x18\x03 \x03(\x0e\x32\x14.epp.host.HostStatus\x12(\n\taddresses\x18\x04 \x03(\x0b\x32\x15.epp.common.IPAddress\x12\x11\n\tclient_id\x18\x05 \x01(\t\x12\x37\n\x11\x63lient_created_id\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\rcreation_date\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x39\n\x13last_updated_client\x18\x08 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x35\n\x11last_updated_date\x18\t \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x36\n\x12last_transfer_date\x18\n \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x08\x63md_resp\x18\x0b \x01(\x0b\x32\x1b.epp.common.CommandResponse\"\x8b\x01\n\x11HostCreateRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12(\n\taddresses\x18\x02 \x03(\x0b\x32\x15.epp.common.IPAddress\x12\x15\n\rregistry_name\x18\x03 \x01(\t\x12\'\n\nisnic_info\x18\x04 \x01(\x0b\x32\x13.epp.isnic.HostInfo\"\x98\x01\n\x0fHostCreateReply\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07pending\x18\x02 \x01(\x08\x12\x31\n\rcreation_date\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x08\x63md_resp\x18\x05 \x01(\x0b\x32\x1b.epp.common.CommandResponseJ\x04\x08\x04\x10\x05\"8\n\x11HostDeleteRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x02 \x01(\t\"W\n\x0fHostDeleteReply\x12\x0f\n\x07pending\x18\x01 \x01(\x08\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponseJ\x04\x08\x02\x10\x03\"\xd7\x02\n\x11HostUpdateRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12.\n\x03\x61\x64\x64\x18\x02 \x03(\x0b\x32!.epp.host.HostUpdateRequest.Param\x12\x31\n\x06remove\x18\x03 \x03(\x0b\x32!.epp.host.HostUpdateRequest.Param\x12.\n\x08new_name\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x15\n\rregistry_name\x18\x05 \x01(\t\x12\'\n\nisnic_info\x18\x06 \x01(\x0b\x32\x13.epp.isnic.HostInfo\x1a\x61\n\x05Param\x12(\n\x07\x61\x64\x64ress\x18\x01 \x01(\x0b\x32\x15.epp.common.IPAddressH\x00\x12%\n\x05state\x18\x02 \x01(\x0e\x32\x14.epp.host.HostStatusH\x00\x42\x07\n\x05param\"W\n\x0fHostUpdateReply\x12\x0f\n\x07pending\x18\x01 \x01(\x08\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponseJ\x04\x08\x02\x10\x03*\xde\x01\n\nHostStatus\x12\x1a\n\x16\x43lientDeleteProhibited\x10\x00\x12\x1a\n\x16\x43lientUpdateProhibited\x10\x01\x12\n\n\x06Linked\x10\x02\x12\x06\n\x02Ok\x10\x03\x12\x11\n\rPendingCreate\x10\x04\x12\x11\n\rPendingDelete\x10\x05\x12\x13\n\x0fPendingTransfer\x10\x06\x12\x11\n\rPendingUpdate\x10\x07\x12\x1a\n\x16ServerDeleteProhibited\x10\x08\x12\x1a\n\x16ServerUpdateProhibited\x10\tB/Z-github.com/as207960/epp-proxy/gen/go/epp/hostb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'host.host_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z-github.com/as207960/epp-proxy/gen/go/epp/host'
  _HOSTSTATUS._serialized_start=1737
  _HOSTSTATUS._serialized_end=1959
  _HOSTCHECKREQUEST._serialized_start=134
  _HOSTCHECKREQUEST._serialized_end=189
  _HOSTCHECKREPLY._serialized_start=192
  _HOSTCHECKREPLY._serialized_end=320
  _HOSTINFOREQUEST._serialized_start=322
  _HOSTINFOREQUEST._serialized_end=376
  _HOSTINFOREPLY._serialized_start=379
  _HOSTINFOREPLY._serialized_end=855
  _HOSTCREATEREQUEST._serialized_start=858
  _HOSTCREATEREQUEST._serialized_end=997
  _HOSTCREATEREPLY._serialized_start=1000
  _HOSTCREATEREPLY._serialized_end=1152
  _HOSTDELETEREQUEST._serialized_start=1154
  _HOSTDELETEREQUEST._serialized_end=1210
  _HOSTDELETEREPLY._serialized_start=1212
  _HOSTDELETEREPLY._serialized_end=1299
  _HOSTUPDATEREQUEST._serialized_start=1302
  _HOSTUPDATEREQUEST._serialized_end=1645
  _HOSTUPDATEREQUEST_PARAM._serialized_start=1548
  _HOSTUPDATEREQUEST_PARAM._serialized_end=1645
  _HOSTUPDATEREPLY._serialized_start=1647
  _HOSTUPDATEREPLY._serialized_end=1734
# @@protoc_insertion_point(module_scope)