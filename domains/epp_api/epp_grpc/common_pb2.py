# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: common.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='common.proto',
  package='epp.common',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x0c\x63ommon.proto\x12\nepp.common\"y\n\tIPAddress\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12-\n\x04type\x18\x02 \x01(\x0e\x32\x1f.epp.common.IPAddress.IPVersion\",\n\tIPVersion\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x08\n\x04IPv4\x10\x01\x12\x08\n\x04IPv6\x10\x02*\x96\x01\n\x0eTransferStatus\x12\x11\n\rUnknownStatus\x10\x00\x12\x12\n\x0e\x43lientApproved\x10\x01\x12\x13\n\x0f\x43lientCancelled\x10\x02\x12\x12\n\x0e\x43lientRejected\x10\x03\x12\x0b\n\x07Pending\x10\x04\x12\x12\n\x0eServerApproved\x10\x05\x12\x13\n\x0fServerCancelled\x10\x06\x62\x06proto3'
)

_TRANSFERSTATUS = _descriptor.EnumDescriptor(
  name='TransferStatus',
  full_name='epp.common.TransferStatus',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UnknownStatus', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ClientApproved', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ClientCancelled', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ClientRejected', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='Pending', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ServerApproved', index=5, number=5,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ServerCancelled', index=6, number=6,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=152,
  serialized_end=302,
)
_sym_db.RegisterEnumDescriptor(_TRANSFERSTATUS)

TransferStatus = enum_type_wrapper.EnumTypeWrapper(_TRANSFERSTATUS)
UnknownStatus = 0
ClientApproved = 1
ClientCancelled = 2
ClientRejected = 3
Pending = 4
ServerApproved = 5
ServerCancelled = 6


_IPADDRESS_IPVERSION = _descriptor.EnumDescriptor(
  name='IPVersion',
  full_name='epp.common.IPAddress.IPVersion',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IPv4', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IPv6', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=105,
  serialized_end=149,
)
_sym_db.RegisterEnumDescriptor(_IPADDRESS_IPVERSION)


_IPADDRESS = _descriptor.Descriptor(
  name='IPAddress',
  full_name='epp.common.IPAddress',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='address', full_name='epp.common.IPAddress.address', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='type', full_name='epp.common.IPAddress.type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _IPADDRESS_IPVERSION,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=28,
  serialized_end=149,
)

_IPADDRESS.fields_by_name['type'].enum_type = _IPADDRESS_IPVERSION
_IPADDRESS_IPVERSION.containing_type = _IPADDRESS
DESCRIPTOR.message_types_by_name['IPAddress'] = _IPADDRESS
DESCRIPTOR.enum_types_by_name['TransferStatus'] = _TRANSFERSTATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

IPAddress = _reflection.GeneratedProtocolMessageType('IPAddress', (_message.Message,), {
  'DESCRIPTOR' : _IPADDRESS,
  '__module__' : 'common_pb2'
  # @@protoc_insertion_point(class_scope:epp.common.IPAddress)
  })
_sym_db.RegisterMessage(IPAddress)


# @@protoc_insertion_point(module_scope)
