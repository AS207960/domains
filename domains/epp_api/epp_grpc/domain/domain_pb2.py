# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: domain/domain.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'domain/domain.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from ..common import common_pb2 as common_dot_common__pb2
from ..rgp import rgp_pb2 as rgp_dot_rgp__pb2
from ..fee import fee_pb2 as fee_dot_fee__pb2
from ..eurid import eurid_pb2 as eurid_dot_eurid__pb2
from ..launch import launch_pb2 as launch_dot_launch__pb2
from ..domain_common import domain_common_pb2 as domain__common_dot_domain__common__pb2
from ..isnic import isnic_pb2 as isnic_dot_isnic__pb2
from ..personal_registration import personal_registration_pb2 as personal__registration_dot_personal__registration__pb2
from ..keysys import keysys_pb2 as keysys_dot_keysys__pb2
from ..nominet_ext import nominet_ext_pb2 as nominet__ext_dot_nominet__ext__pb2
from ..ttl import ttl_pb2 as ttl_dot_ttl__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13\x64omain/domain.proto\x12\nepp.domain\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x13\x63ommon/common.proto\x1a\rrgp/rgp.proto\x1a\rfee/fee.proto\x1a\x11\x65urid/eurid.proto\x1a\x13launch/launch.proto\x1a!domain_common/domain_common.proto\x1a\x11isnic/isnic.proto\x1a\x31personal_registration/personal_registration.proto\x1a\x13keysys/keysys.proto\x1a\x1dnominet_ext/nominet_ext.proto\x1a\rttl/ttl.proto\"#\n\x07\x43ontact\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\t\"\x8c\x01\n\nNameServer\x12\x12\n\x08host_obj\x18\x01 \x01(\tH\x00\x12\x13\n\thost_name\x18\x03 \x01(\tH\x00\x12(\n\taddresses\x18\x02 \x03(\x0b\x32\x15.epp.common.IPAddress\x12!\n\teurid_idn\x18\x04 \x01(\x0b\x32\x0e.epp.eurid.IDNB\x08\n\x06server\"9\n\x0b\x44omainHosts\x12*\n\x05hosts\x18\x01 \x01(\x0e\x32\x1b.epp.domain.DomainHostsType\"\xcf\x01\n\x12\x44omainCheckRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12$\n\tfee_check\x18\x02 \x01(\x0b\x32\x11.epp.fee.FeeCheck\x12\'\n\x0claunch_check\x18\x03 \x01(\x0b\x32\x11.epp.launch.Phase\x12\x33\n\rregistry_name\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\'\n\x06keysys\x18\x05 \x01(\x0b\x32\x17.epp.keysys.DomainCheck\"\x86\x01\n\x18\x44omainClaimsCheckRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\'\n\x0claunch_check\x18\x02 \x01(\x0b\x32\x11.epp.launch.Phase\x12\x33\n\rregistry_name\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"`\n\x1b\x44omainTrademarkCheckRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x33\n\rregistry_name\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xc8\x02\n\x10\x44omainCheckReply\x12\x11\n\tavailable\x18\x01 \x01(\x08\x12,\n\x06reason\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\tfee_check\x18\x04 \x01(\x0b\x32\x15.epp.fee.FeeCheckData\x12\x30\n\x10\x64onuts_fee_check\x18\x05 \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12\x15\n\rregistry_name\x18\x03 \x01(\t\x12-\n\x08\x63md_resp\x18\x06 \x01(\x0b\x32\x1b.epp.common.CommandResponse\x12!\n\teurid_idn\x18\x07 \x01(\x0b\x32\x0e.epp.eurid.IDN\x12.\n\neurid_data\x18\x08 \x01(\x0b\x32\x1a.epp.eurid.DomainCheckData\"\x9a\x01\n\x16\x44omainClaimsCheckReply\x12\x0e\n\x06\x65xists\x18\x01 \x01(\x08\x12*\n\x0b\x63laims_keys\x18\x02 \x03(\x0b\x32\x15.epp.launch.ClaimsKey\x12\x15\n\rregistry_name\x18\x03 \x01(\t\x12-\n\x08\x63md_resp\x18\x04 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"\xc4\x02\n\x11\x44omainInfoRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12/\n\tauth_info\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12&\n\x05hosts\x18\x06 \x01(\x0b\x32\x17.epp.domain.DomainHosts\x12+\n\x0blaunch_info\x18\x03 \x01(\x0b\x32\x16.epp.launch.LaunchInfo\x12\x33\n\rregistry_name\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x14\x64onuts_fee_agreement\x18\x05 \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12\x30\n\neurid_data\x18\x07 \x01(\x0b\x32\x1c.epp.eurid.DomainInfoRequest\"\xe2\t\n\x0f\x44omainInfoReply\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0bregistry_id\x18\x02 \x01(\t\x12\x31\n\x08statuses\x18\x03 \x03(\x0e\x32\x1f.epp.domain_common.DomainStatus\x12\x12\n\nregistrant\x18\x04 \x01(\t\x12%\n\x08\x63ontacts\x18\x05 \x03(\x0b\x32\x13.epp.domain.Contact\x12+\n\x0bnameservers\x18\x06 \x03(\x0b\x32\x16.epp.domain.NameServer\x12\r\n\x05hosts\x18\x07 \x03(\t\x12\x11\n\tclient_id\x18\x08 \x01(\t\x12\x37\n\x11\x63lient_created_id\x18\t \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\rcreation_date\x18\n \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12/\n\x0b\x65xpiry_date\x18\x0b \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x39\n\x13last_updated_client\x18\x0c \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x35\n\x11last_updated_date\x18\r \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x36\n\x12last_transfer_date\x18\x0e \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x15\n\rregistry_name\x18\x0f \x01(\t\x12$\n\trgp_state\x18\x10 \x03(\x0e\x32\x11.epp.rgp.RGPState\x12/\n\tauth_info\x18\x11 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\'\n\x07sec_dns\x18\x12 \x01(\x0b\x32\x16.epp.domain.SecDNSData\x12/\n\x0blaunch_info\x18\x13 \x01(\x0b\x32\x1a.epp.launch.LaunchInfoData\x12/\n\x0f\x64onuts_fee_data\x18\x14 \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12:\n\x13verisign_whois_info\x18\x15 \x01(\x0b\x32\x1d.epp.domain.VerisignWhoisInfo\x12!\n\teurid_idn\x18\x17 \x01(\x0b\x32\x0e.epp.eurid.IDN\x12)\n\neurid_data\x18\x18 \x01(\x0b\x32\x15.epp.eurid.DomainInfo\x12)\n\nisnic_info\x18\x19 \x01(\x0b\x32\x15.epp.isnic.DomainInfo\x12R\n\x15personal_registration\x18\x1a \x01(\x0b\x32\x33.epp.personal_registration.PersonalRegistrationInfo\x12&\n\x06keysys\x18\x1b \x01(\x0b\x32\x16.epp.keysys.DomainInfo\x12\x30\n\x0bnominet_ext\x18\x1c \x01(\x0b\x32\x1b.epp.nominet_ext.DomainInfo\x12\x1d\n\x03ttl\x18\x1d \x01(\x0b\x32\x10.epp.ttl.TTLInfo\x12-\n\x08\x63md_resp\x18\x16 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"\xe8\x05\n\x13\x44omainCreateRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\"\n\x06period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\x12\x12\n\nregistrant\x18\x03 \x01(\t\x12%\n\x08\x63ontacts\x18\x04 \x03(\x0b\x32\x13.epp.domain.Contact\x12+\n\x0bnameservers\x18\x05 \x03(\x0b\x32\x16.epp.domain.NameServer\x12\x11\n\tauth_info\x18\x06 \x01(\t\x12\'\n\x07sec_dns\x18\x07 \x01(\x0b\x32\x16.epp.domain.SecDNSData\x12-\n\x0blaunch_data\x18\x08 \x01(\x0b\x32\x18.epp.launch.LaunchCreate\x12\x33\n\rregistry_name\x18\t \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x14\x64onuts_fee_agreement\x18\n \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12,\n\rfee_agreement\x18\x0b \x01(\x0b\x32\x15.epp.fee.FeeAgreement\x12\x34\n\neurid_data\x18\x0c \x01(\x0b\x32 .epp.eurid.DomainCreateExtension\x12-\n\risnic_payment\x18\r \x01(\x0b\x32\x16.epp.isnic.PaymentInfo\x12R\n\x15personal_registration\x18\x0e \x01(\x0b\x32\x33.epp.personal_registration.PersonalRegistrationInfo\x12(\n\x06keysys\x18\x0f \x01(\x0b\x32\x18.epp.keysys.DomainCreate\x12\x32\n\x0bnominet_ext\x18\x1c \x01(\x0b\x32\x1d.epp.nominet_ext.DomainCreate\x12\x1c\n\x03ttl\x18\x10 \x01(\x0b\x32\x0f.epp.ttl.TTLSet\"\xdd\x03\n\x11\x44omainCreateReply\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07pending\x18\x02 \x01(\x08\x12\x31\n\rcreation_date\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12/\n\x0b\x65xpiry_date\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\"\n\x08\x66\x65\x65_data\x18\x06 \x01(\x0b\x32\x10.epp.fee.FeeData\x12/\n\x0f\x64onuts_fee_data\x18\t \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12+\n\x0blaunch_data\x18\x08 \x01(\x0b\x32\x16.epp.launch.LaunchData\x12\x15\n\rregistry_name\x18\x05 \x01(\t\x12-\n\x08\x63md_resp\x18\n \x01(\x0b\x32\x1b.epp.common.CommandResponse\x12!\n\teurid_idn\x18\x0b \x01(\x0b\x32\x0e.epp.eurid.IDN\x12T\n\x15personal_registration\x18\x0c \x01(\x0b\x32\x35.epp.personal_registration.PersonalRegistrationCreateJ\x04\x08\x07\x10\x08\"\x9b\x02\n\x13\x44omainDeleteRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12+\n\x0blaunch_data\x18\x02 \x01(\x0b\x32\x16.epp.launch.LaunchData\x12\x33\n\rregistry_name\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x14\x64onuts_fee_agreement\x18\x04 \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12\x34\n\neurid_data\x18\x05 \x01(\x0b\x32 .epp.eurid.DomainDeleteExtension\x12(\n\x06keysys\x18\x06 \x01(\x0b\x32\x18.epp.keysys.DomainDelete\"\xb7\x01\n\x11\x44omainDeleteReply\x12\x0f\n\x07pending\x18\x01 \x01(\x08\x12\"\n\x08\x66\x65\x65_data\x18\x03 \x01(\x0b\x32\x10.epp.fee.FeeData\x12\x15\n\rregistry_name\x18\x02 \x01(\t\x12-\n\x08\x63md_resp\x18\x05 \x01(\x0b\x32\x1b.epp.common.CommandResponse\x12!\n\teurid_idn\x18\x06 \x01(\x0b\x32\x0e.epp.eurid.IDNJ\x04\x08\x04\x10\x05\"\xe8\x06\n\x13\x44omainUpdateRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x32\n\x03\x61\x64\x64\x18\x02 \x03(\x0b\x32%.epp.domain.DomainUpdateRequest.Param\x12\x35\n\x06remove\x18\x03 \x03(\x0b\x32%.epp.domain.DomainUpdateRequest.Param\x12\x34\n\x0enew_registrant\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x33\n\rnew_auth_info\x18\x05 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\x07sec_dns\x18\x06 \x01(\x0b\x32\x1c.epp.domain.UpdateSecDNSData\x12+\n\x0blaunch_data\x18\x07 \x01(\x0b\x32\x16.epp.launch.LaunchData\x12\x33\n\rregistry_name\x18\x08 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x14\x64onuts_fee_agreement\x18\t \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12,\n\rfee_agreement\x18\n \x01(\x0b\x32\x15.epp.fee.FeeAgreement\x12\x34\n\neurid_data\x18\x0b \x01(\x0b\x32 .epp.eurid.DomainUpdateExtension\x12+\n\nisnic_info\x18\x0c \x01(\x0b\x32\x17.epp.isnic.DomainUpdate\x12(\n\x06keysys\x18\r \x01(\x0b\x32\x18.epp.keysys.DomainUpdate\x12\x32\n\x0bnominet_ext\x18\x1c \x01(\x0b\x32\x1d.epp.nominet_ext.DomainUpdate\x12\x1c\n\x03ttl\x18\x0e \x01(\x0b\x32\x0f.epp.ttl.TTLSet\x1a\x98\x01\n\x05Param\x12,\n\nnameserver\x18\x01 \x01(\x0b\x32\x16.epp.domain.NameServerH\x00\x12&\n\x07\x63ontact\x18\x02 \x01(\x0b\x32\x13.epp.domain.ContactH\x00\x12\x30\n\x05state\x18\x03 \x01(\x0e\x32\x1f.epp.domain_common.DomainStatusH\x00\x42\x07\n\x05param\"r\n\x11\x44omainSyncRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x33\n\rregistry_name\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\r\n\x05month\x18\x03 \x01(\r\x12\x0b\n\x03\x64\x61y\x18\x04 \x01(\r\"\xc5\x01\n\x11\x44omainUpdateReply\x12\x0f\n\x07pending\x18\x01 \x01(\x08\x12\"\n\x08\x66\x65\x65_data\x18\x03 \x01(\x0b\x32\x10.epp.fee.FeeData\x12/\n\x0f\x64onuts_fee_data\x18\x05 \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12\x15\n\rregistry_name\x18\x02 \x01(\t\x12-\n\x08\x63md_resp\x18\x06 \x01(\x0b\x32\x1b.epp.common.CommandResponseJ\x04\x08\x04\x10\x05\"\xf0\x02\n\x12\x44omainRenewRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\"\n\x06period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\x12\x37\n\x13\x63urrent_expiry_date\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x33\n\rregistry_name\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x14\x64onuts_fee_agreement\x18\x05 \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12,\n\rfee_agreement\x18\x06 \x01(\x0b\x32\x15.epp.fee.FeeAgreement\x12-\n\risnic_payment\x18\x07 \x01(\x0b\x32\x16.epp.isnic.PaymentInfo\x12\'\n\x06keysys\x18\x08 \x01(\x0b\x32\x17.epp.keysys.DomainRenew\"\xac\x03\n\x10\x44omainRenewReply\x12\x0c\n\x04name\x18\x06 \x01(\t\x12\x0f\n\x07pending\x18\x01 \x01(\x08\x12/\n\x0b\x65xpiry_date\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\"\n\x08\x66\x65\x65_data\x18\x04 \x01(\x0b\x32\x10.epp.fee.FeeData\x12/\n\x0f\x64onuts_fee_data\x18\x07 \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12\x15\n\rregistry_name\x18\x03 \x01(\t\x12-\n\x08\x63md_resp\x18\x08 \x01(\x0b\x32\x1b.epp.common.CommandResponse\x12!\n\teurid_idn\x18\t \x01(\x0b\x32\x0e.epp.eurid.IDN\x12.\n\neurid_data\x18\n \x01(\x0b\x32\x1a.epp.eurid.DomainRenewInfo\x12T\n\x15personal_registration\x18\x0b \x01(\x0b\x32\x35.epp.personal_registration.PersonalRegistrationCreateJ\x04\x08\x05\x10\x06\"\x90\x01\n\x1a\x44omainTransferQueryRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12/\n\tauth_info\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x33\n\rregistry_name\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xe0\x02\n\x1c\x44omainTransferRequestRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\"\n\x06period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\x12\x11\n\tauth_info\x18\x03 \x01(\t\x12\x33\n\rregistry_name\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x14\x64onuts_fee_agreement\x18\x05 \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12,\n\rfee_agreement\x18\x06 \x01(\x0b\x32\x15.epp.fee.FeeAgreement\x12\x36\n\neurid_data\x18\x07 \x01(\x0b\x32\".epp.eurid.DomainTransferExtension\x12*\n\x06keysys\x18\x08 \x01(\x0b\x32\x1a.epp.keysys.DomainTransfer\"y\n!DomainTransferAcceptRejectRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tauth_info\x18\x02 \x01(\t\x12\x33\n\rregistry_name\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xf4\x04\n\x13\x44omainTransferReply\x12\x0f\n\x07pending\x18\x01 \x01(\x08\x12\x0c\n\x04name\x18\x0c \x01(\t\x12*\n\x06status\x18\x02 \x01(\x0e\x32\x1a.epp.common.TransferStatus\x12\x1b\n\x13requested_client_id\x18\x03 \x01(\t\x12\x32\n\x0erequested_date\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x15\n\ract_client_id\x18\x05 \x01(\t\x12,\n\x08\x61\x63t_date\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12/\n\x0b\x65xpiry_date\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\"\n\x08\x66\x65\x65_data\x18\t \x01(\x0b\x32\x10.epp.fee.FeeData\x12/\n\x0f\x64onuts_fee_data\x18\x0b \x01(\x0b\x32\x16.epp.fee.DonutsFeeData\x12\x15\n\rregistry_name\x18\x08 \x01(\t\x12-\n\x08\x63md_resp\x18\r \x01(\x0b\x32\x1b.epp.common.CommandResponse\x12!\n\teurid_idn\x18\x0e \x01(\x0b\x32\x0e.epp.eurid.IDN\x12\x31\n\neurid_data\x18\x0f \x01(\x0b\x32\x1d.epp.eurid.DomainTransferInfo\x12T\n\x15personal_registration\x18\x10 \x01(\x0b\x32\x35.epp.personal_registration.PersonalRegistrationCreateJ\x04\x08\n\x10\x0b\"\xa3\x01\n\nSecDNSData\x12\x31\n\x0cmax_sig_life\x18\x01 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12+\n\x07\x64s_data\x18\x02 \x01(\x0b\x32\x18.epp.domain.SecDNSDSDataH\x00\x12-\n\x08key_data\x18\x03 \x01(\x0b\x32\x19.epp.domain.SecDNSKeyDataH\x00\x42\x06\n\x04\x64\x61ta\"7\n\x0cSecDNSDSData\x12\'\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x19.epp.domain.SecDNSDSDatum\"\x86\x01\n\rSecDNSDSDatum\x12\x0f\n\x07key_tag\x18\x01 \x01(\r\x12\x11\n\talgorithm\x18\x02 \x01(\r\x12\x13\n\x0b\x64igest_type\x18\x03 \x01(\r\x12\x0e\n\x06\x64igest\x18\x04 \x01(\t\x12,\n\x08key_data\x18\x05 \x01(\x0b\x32\x1a.epp.domain.SecDNSKeyDatum\"9\n\rSecDNSKeyData\x12(\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x1a.epp.domain.SecDNSKeyDatum\"X\n\x0eSecDNSKeyDatum\x12\r\n\x05\x66lags\x18\x01 \x01(\r\x12\x10\n\x08protocol\x18\x02 \x01(\r\x12\x11\n\talgorithm\x18\x03 \x01(\r\x12\x12\n\npublic_key\x18\x04 \x01(\t\"\xdd\x02\n\x10UpdateSecDNSData\x12*\n\x06urgent\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.BoolValue\x12\x35\n\x10new_max_sig_life\x18\x02 \x01(\x0b\x32\x1b.google.protobuf.Int64Value\x12/\n\x0b\x61\x64\x64_ds_data\x18\x03 \x01(\x0b\x32\x18.epp.domain.SecDNSDSDataH\x00\x12\x31\n\x0c\x61\x64\x64_key_data\x18\x04 \x01(\x0b\x32\x19.epp.domain.SecDNSKeyDataH\x00\x12\r\n\x03\x61ll\x18\x05 \x01(\x08H\x01\x12/\n\x0brem_ds_data\x18\x06 \x01(\x0b\x32\x18.epp.domain.SecDNSDSDataH\x01\x12\x31\n\x0crem_key_data\x18\x07 \x01(\x0b\x32\x19.epp.domain.SecDNSKeyDataH\x01\x42\x05\n\x03\x61\x64\x64\x42\x08\n\x06remove\"\xb8\x01\n\x11VerisignWhoisInfo\x12\x11\n\tregistrar\x18\x01 \x01(\t\x12\x32\n\x0cwhois_server\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12)\n\x03url\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\x0biris_server\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xd2\x01\n\x0e\x44omainPANReply\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06result\x18\x02 \x01(\x08\x12;\n\x15server_transaction_id\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12;\n\x15\x63lient_transaction_id\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04\x64\x61te\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp*D\n\x0f\x44omainHostsType\x12\x07\n\x03\x41ll\x10\x00\x12\r\n\tDelegated\x10\x01\x12\x0f\n\x0bSubordinate\x10\x02\x12\x08\n\x04None\x10\x03\x42\x31Z/github.com/as207960/epp-proxy/gen/go/epp/domainb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'domain.domain_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z/github.com/as207960/epp-proxy/gen/go/epp/domain'
  _globals['_DOMAINHOSTSTYPE']._serialized_start=9324
  _globals['_DOMAINHOSTSTYPE']._serialized_end=9392
  _globals['_CONTACT']._serialized_start=363
  _globals['_CONTACT']._serialized_end=398
  _globals['_NAMESERVER']._serialized_start=401
  _globals['_NAMESERVER']._serialized_end=541
  _globals['_DOMAINHOSTS']._serialized_start=543
  _globals['_DOMAINHOSTS']._serialized_end=600
  _globals['_DOMAINCHECKREQUEST']._serialized_start=603
  _globals['_DOMAINCHECKREQUEST']._serialized_end=810
  _globals['_DOMAINCLAIMSCHECKREQUEST']._serialized_start=813
  _globals['_DOMAINCLAIMSCHECKREQUEST']._serialized_end=947
  _globals['_DOMAINTRADEMARKCHECKREQUEST']._serialized_start=949
  _globals['_DOMAINTRADEMARKCHECKREQUEST']._serialized_end=1045
  _globals['_DOMAINCHECKREPLY']._serialized_start=1048
  _globals['_DOMAINCHECKREPLY']._serialized_end=1376
  _globals['_DOMAINCLAIMSCHECKREPLY']._serialized_start=1379
  _globals['_DOMAINCLAIMSCHECKREPLY']._serialized_end=1533
  _globals['_DOMAININFOREQUEST']._serialized_start=1536
  _globals['_DOMAININFOREQUEST']._serialized_end=1860
  _globals['_DOMAININFOREPLY']._serialized_start=1863
  _globals['_DOMAININFOREPLY']._serialized_end=3113
  _globals['_DOMAINCREATEREQUEST']._serialized_start=3116
  _globals['_DOMAINCREATEREQUEST']._serialized_end=3860
  _globals['_DOMAINCREATEREPLY']._serialized_start=3863
  _globals['_DOMAINCREATEREPLY']._serialized_end=4340
  _globals['_DOMAINDELETEREQUEST']._serialized_start=4343
  _globals['_DOMAINDELETEREQUEST']._serialized_end=4626
  _globals['_DOMAINDELETEREPLY']._serialized_start=4629
  _globals['_DOMAINDELETEREPLY']._serialized_end=4812
  _globals['_DOMAINUPDATEREQUEST']._serialized_start=4815
  _globals['_DOMAINUPDATEREQUEST']._serialized_end=5687
  _globals['_DOMAINUPDATEREQUEST_PARAM']._serialized_start=5535
  _globals['_DOMAINUPDATEREQUEST_PARAM']._serialized_end=5687
  _globals['_DOMAINSYNCREQUEST']._serialized_start=5689
  _globals['_DOMAINSYNCREQUEST']._serialized_end=5803
  _globals['_DOMAINUPDATEREPLY']._serialized_start=5806
  _globals['_DOMAINUPDATEREPLY']._serialized_end=6003
  _globals['_DOMAINRENEWREQUEST']._serialized_start=6006
  _globals['_DOMAINRENEWREQUEST']._serialized_end=6374
  _globals['_DOMAINRENEWREPLY']._serialized_start=6377
  _globals['_DOMAINRENEWREPLY']._serialized_end=6805
  _globals['_DOMAINTRANSFERQUERYREQUEST']._serialized_start=6808
  _globals['_DOMAINTRANSFERQUERYREQUEST']._serialized_end=6952
  _globals['_DOMAINTRANSFERREQUESTREQUEST']._serialized_start=6955
  _globals['_DOMAINTRANSFERREQUESTREQUEST']._serialized_end=7307
  _globals['_DOMAINTRANSFERACCEPTREJECTREQUEST']._serialized_start=7309
  _globals['_DOMAINTRANSFERACCEPTREJECTREQUEST']._serialized_end=7430
  _globals['_DOMAINTRANSFERREPLY']._serialized_start=7433
  _globals['_DOMAINTRANSFERREPLY']._serialized_end=8061
  _globals['_SECDNSDATA']._serialized_start=8064
  _globals['_SECDNSDATA']._serialized_end=8227
  _globals['_SECDNSDSDATA']._serialized_start=8229
  _globals['_SECDNSDSDATA']._serialized_end=8284
  _globals['_SECDNSDSDATUM']._serialized_start=8287
  _globals['_SECDNSDSDATUM']._serialized_end=8421
  _globals['_SECDNSKEYDATA']._serialized_start=8423
  _globals['_SECDNSKEYDATA']._serialized_end=8480
  _globals['_SECDNSKEYDATUM']._serialized_start=8482
  _globals['_SECDNSKEYDATUM']._serialized_end=8570
  _globals['_UPDATESECDNSDATA']._serialized_start=8573
  _globals['_UPDATESECDNSDATA']._serialized_end=8922
  _globals['_VERISIGNWHOISINFO']._serialized_start=8925
  _globals['_VERISIGNWHOISINFO']._serialized_end=9109
  _globals['_DOMAINPANREPLY']._serialized_start=9112
  _globals['_DOMAINPANREPLY']._serialized_end=9322
# @@protoc_insertion_point(module_scope)
