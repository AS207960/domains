# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: contact/contact.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from common import common_pb2 as common_dot_common__pb2
from eurid import eurid_pb2 as eurid_dot_eurid__pb2
from contact.qualified_lawyer import qualified_lawyer_pb2 as contact_dot_qualified__lawyer_dot_qualified__lawyer__pb2
from nominet_ext import nominet_ext_pb2 as nominet__ext_dot_nominet__ext__pb2
from isnic import isnic_pb2 as isnic_dot_isnic__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15\x63ontact/contact.proto\x12\x0b\x65pp.contact\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x13\x63ommon/common.proto\x1a\x11\x65urid/eurid.proto\x1a/contact/qualified_lawyer/qualified_lawyer.proto\x1a\x1dnominet_ext/nominet_ext.proto\x1a\x11isnic/isnic.proto\"\xd0\x02\n\rPostalAddress\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x32\n\x0corganisation\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x0f\n\x07streets\x18\x04 \x03(\t\x12\x0c\n\x04\x63ity\x18\x05 \x01(\t\x12.\n\x08province\x18\x06 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\x0bpostal_code\x18\x07 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x14\n\x0c\x63ountry_code\x18\x08 \x01(\t\x12\x35\n\x0fidentity_number\x18\t \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12.\n\nbirth_date\x18\n \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"8\n\x13\x43ontactCheckRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x02 \x01(\t\"\x83\x01\n\x11\x43ontactCheckReply\x12\x11\n\tavailable\x18\x01 \x01(\x08\x12,\n\x06reason\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"7\n\x12\x43ontactInfoRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x02 \x01(\t\"=\n\nDisclosure\x12/\n\ndisclosure\x18\x01 \x03(\x0e\x32\x1b.epp.contact.DisclosureType\"\xd8\x08\n\x10\x43ontactInfoReply\x12\n\n\x02id\x18\x01 \x01(\t\x12\x13\n\x0bregistry_id\x18\x02 \x01(\t\x12,\n\x08statuses\x18\x03 \x03(\x0e\x32\x1a.epp.contact.ContactStatus\x12\x31\n\rlocal_address\x18\x04 \x01(\x0b\x32\x1a.epp.contact.PostalAddress\x12=\n\x19internationalised_address\x18\x05 \x01(\x0b\x32\x1a.epp.contact.PostalAddress\x12 \n\x05phone\x18\x06 \x01(\x0b\x32\x11.epp.common.Phone\x12\x1e\n\x03\x66\x61x\x18\x07 \x01(\x0b\x32\x11.epp.common.Phone\x12\r\n\x05\x65mail\x18\x08 \x01(\t\x12\x11\n\tclient_id\x18\t \x01(\t\x12\x37\n\x11\x63lient_created_id\x18\n \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x31\n\rcreation_date\x18\x0b \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x39\n\x13last_updated_client\x18\x0c \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x35\n\x11last_updated_date\x18\r \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x36\n\x12last_transfer_date\x18\x0e \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12,\n\x0b\x65ntity_type\x18\x0f \x01(\x0e\x32\x17.epp.contact.EntityType\x12\x32\n\x0ctrading_name\x18\x10 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x0e\x63ompany_number\x18\x11 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12/\n\ndisclosure\x18\x12 \x03(\x0e\x32\x1b.epp.contact.DisclosureType\x12/\n\tauth_info\x18\x13 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12:\n\x14nominet_data_quality\x18\x14 \x01(\x0b\x32\x1c.epp.nominet_ext.DataQuality\x12/\n\neurid_info\x18\x16 \x01(\x0b\x32\x1b.epp.eurid.ContactExtension\x12-\n\x08\x63md_resp\x18\x15 \x01(\x0b\x32\x1b.epp.common.CommandResponse\x12G\n\x10qualified_lawyer\x18\x17 \x01(\x0b\x32-.epp.contact.qualified_lawyer.QualifiedLawyer\x12*\n\nisnic_info\x18\x18 \x01(\x0b\x32\x16.epp.isnic.ContactInfo\"\xfc\x04\n\x14\x43ontactCreateRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x31\n\rlocal_address\x18\x02 \x01(\x0b\x32\x1a.epp.contact.PostalAddress\x12=\n\x19internationalised_address\x18\x03 \x01(\x0b\x32\x1a.epp.contact.PostalAddress\x12 \n\x05phone\x18\x04 \x01(\x0b\x32\x11.epp.common.Phone\x12\x1e\n\x03\x66\x61x\x18\x05 \x01(\x0b\x32\x11.epp.common.Phone\x12\r\n\x05\x65mail\x18\x06 \x01(\t\x12,\n\x0b\x65ntity_type\x18\x07 \x01(\x0e\x32\x17.epp.contact.EntityType\x12\x32\n\x0ctrading_name\x18\x08 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x34\n\x0e\x63ompany_number\x18\t \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12+\n\ndisclosure\x18\n \x01(\x0b\x32\x17.epp.contact.Disclosure\x12/\n\neurid_info\x18\r \x01(\x0b\x32\x1b.epp.eurid.ContactExtension\x12\x15\n\rregistry_name\x18\x0b \x01(\t\x12\x11\n\tauth_info\x18\x0c \x01(\t\x12G\n\x10qualified_lawyer\x18\x0e \x01(\x0b\x32-.epp.contact.qualified_lawyer.QualifiedLawyer\x12,\n\nisnic_info\x18\x0f \x01(\x0b\x32\x18.epp.isnic.ContactCreate\"\x99\x01\n\x12\x43ontactCreateReply\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07pending\x18\x02 \x01(\x08\x12\x31\n\rcreation_date\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x08\x63md_resp\x18\x05 \x01(\x0b\x32\x1b.epp.common.CommandResponseJ\x04\x08\x04\x10\x05\"9\n\x14\x43ontactDeleteRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x02 \x01(\t\"Z\n\x12\x43ontactDeleteReply\x12\x0f\n\x07pending\x18\x01 \x01(\x08\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponseJ\x04\x08\x02\x10\x03\"\xcd\x06\n\x14\x43ontactUpdateRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x30\n\x0c\x61\x64\x64_statuses\x18\x02 \x03(\x0e\x32\x1a.epp.contact.ContactStatus\x12\x33\n\x0fremove_statuses\x18\x03 \x03(\x0e\x32\x1a.epp.contact.ContactStatus\x12\x35\n\x11new_local_address\x18\x04 \x01(\x0b\x32\x1a.epp.contact.PostalAddress\x12\x41\n\x1dnew_internationalised_address\x18\x05 \x01(\x0b\x32\x1a.epp.contact.PostalAddress\x12$\n\tnew_phone\x18\x06 \x01(\x0b\x32\x11.epp.common.Phone\x12\"\n\x07new_fax\x18\x07 \x01(\x0b\x32\x11.epp.common.Phone\x12/\n\tnew_email\x18\x08 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x30\n\x0fnew_entity_type\x18\t \x01(\x0e\x32\x17.epp.contact.EntityType\x12\x36\n\x10new_trading_name\x18\n \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x38\n\x12new_company_number\x18\x0b \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12+\n\ndisclosure\x18\x0c \x01(\x0b\x32\x17.epp.contact.Disclosure\x12\x15\n\rregistry_name\x18\r \x01(\t\x12\x33\n\rnew_auth_info\x18\x0e \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x39\n\x0enew_eurid_info\x18\x0f \x01(\x0b\x32!.epp.eurid.ContactUpdateExtension\x12G\n\x10qualified_lawyer\x18\x10 \x01(\x0b\x32-.epp.contact.qualified_lawyer.QualifiedLawyer\x12,\n\nisnic_info\x18\x11 \x01(\x0b\x32\x18.epp.isnic.ContactUpdate\"Z\n\x12\x43ontactUpdateReply\x12\x0f\n\x07pending\x18\x01 \x01(\x08\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponseJ\x04\x08\x02\x10\x03\"q\n\x1b\x43ontactTransferQueryRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12/\n\tauth_info\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12\x15\n\rregistry_name\x18\x03 \x01(\t\"U\n\x1d\x43ontactTransferRequestRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x11\n\tauth_info\x18\x02 \x01(\t\x12\x15\n\rregistry_name\x18\x03 \x01(\t\"\x9e\x02\n\x14\x43ontactTransferReply\x12\x0f\n\x07pending\x18\x01 \x01(\x08\x12*\n\x06status\x18\x02 \x01(\x0e\x32\x1a.epp.common.TransferStatus\x12\x1b\n\x13requested_client_id\x18\x03 \x01(\t\x12\x32\n\x0erequested_date\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x15\n\ract_client_id\x18\x05 \x01(\t\x12,\n\x08\x61\x63t_date\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x08\x63md_resp\x18\x08 \x01(\x0b\x32\x1b.epp.common.CommandResponseJ\x04\x08\x07\x10\x08\"\xd1\x01\n\x0f\x43ontactPANReply\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06result\x18\x02 \x01(\x08\x12;\n\x15server_transaction_id\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12;\n\x15\x63lient_transaction_id\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12(\n\x04\x64\x61te\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp*\xf3\x05\n\nEntityType\x12\n\n\x06NotSet\x10\x00\x12\x11\n\rUnknownEntity\x10\x01\x12\x14\n\x10UkLimitedCompany\x10\x02\x12\x1a\n\x16UkPublicLimitedCompany\x10\x03\x12\x11\n\rUkPartnership\x10\x04\x12\x10\n\x0cUkSoleTrader\x10\x05\x12!\n\x1dUkLimitedLiabilityPartnership\x10\x06\x12*\n&UkIndustrialProvidentRegisteredCompany\x10\x07\x12\x10\n\x0cUkIndividual\x10\x08\x12\x0c\n\x08UkSchool\x10\t\x12\x17\n\x13UkRegisteredCharity\x10\n\x12\x14\n\x10UkGovernmentBody\x10\x0b\x12\x1f\n\x1bUkCorporationByRoyalCharter\x10\x0c\x12\x13\n\x0fUkStatutoryBody\x10\r\x12\x14\n\x10UkPoliticalParty\x10\x1f\x12\x11\n\rOtherUkEntity\x10\x0e\x12\x15\n\x11\x46innishIndividual\x10\x0f\x12\x12\n\x0e\x46innishCompany\x10\x10\x12\x16\n\x12\x46innishAssociation\x10\x11\x12\x16\n\x12\x46innishInstitution\x10\x12\x12\x19\n\x15\x46innishPoliticalParty\x10\x13\x12\x17\n\x13\x46innishMunicipality\x10\x14\x12\x15\n\x11\x46innishGovernment\x10\x15\x12\x1a\n\x16\x46innishPublicCommunity\x10\x16\x12\x13\n\x0fOtherIndividual\x10\x17\x12\x10\n\x0cOtherCompany\x10\x18\x12\x14\n\x10OtherAssociation\x10\x19\x12\x14\n\x10OtherInstitution\x10\x1a\x12\x17\n\x13OtherPoliticalParty\x10\x1b\x12\x15\n\x11OtherMunicipality\x10\x1c\x12\x13\n\x0fOtherGovernment\x10\x1d\x12\x18\n\x14OtherPublicCommunity\x10\x1e*\xc3\x01\n\x0e\x44isclosureType\x12\r\n\tLocalName\x10\x00\x12\x19\n\x15InternationalisedName\x10\x01\x12\x15\n\x11LocalOrganisation\x10\x02\x12!\n\x1dInternationalisedOrganisation\x10\x03\x12\x10\n\x0cLocalAddress\x10\x04\x12\x1c\n\x18InternationalisedAddress\x10\x05\x12\t\n\x05Voice\x10\x06\x12\x07\n\x03\x46\x61x\x10\x07\x12\t\n\x05\x45mail\x10\x08*\x9d\x02\n\rContactStatus\x12\x1a\n\x16\x43lientDeleteProhibited\x10\x00\x12\x1c\n\x18\x43lientTransferProhibited\x10\x01\x12\x1a\n\x16\x43lientUpdateProhibited\x10\x02\x12\n\n\x06Linked\x10\x03\x12\x06\n\x02Ok\x10\x04\x12\x11\n\rPendingCreate\x10\x05\x12\x11\n\rPendingDelete\x10\x06\x12\x13\n\x0fPendingTransfer\x10\x07\x12\x11\n\rPendingUpdate\x10\x08\x12\x1a\n\x16ServerDeleteProhibited\x10\t\x12\x1c\n\x18ServerTransferProhibited\x10\n\x12\x1a\n\x16ServerUpdateProhibited\x10\x0b\x42\x32Z0github.com/as207960/epp-proxy/gen/go/epp/contactb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'contact.contact_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z0github.com/as207960/epp-proxy/gen/go/epp/contact'
  _ENTITYTYPE._serialized_start=4598
  _ENTITYTYPE._serialized_end=5353
  _DISCLOSURETYPE._serialized_start=5356
  _DISCLOSURETYPE._serialized_end=5551
  _CONTACTSTATUS._serialized_start=5554
  _CONTACTSTATUS._serialized_end=5839
  _POSTALADDRESS._serialized_start=243
  _POSTALADDRESS._serialized_end=579
  _CONTACTCHECKREQUEST._serialized_start=581
  _CONTACTCHECKREQUEST._serialized_end=637
  _CONTACTCHECKREPLY._serialized_start=640
  _CONTACTCHECKREPLY._serialized_end=771
  _CONTACTINFOREQUEST._serialized_start=773
  _CONTACTINFOREQUEST._serialized_end=828
  _DISCLOSURE._serialized_start=830
  _DISCLOSURE._serialized_end=891
  _CONTACTINFOREPLY._serialized_start=894
  _CONTACTINFOREPLY._serialized_end=2006
  _CONTACTCREATEREQUEST._serialized_start=2009
  _CONTACTCREATEREQUEST._serialized_end=2645
  _CONTACTCREATEREPLY._serialized_start=2648
  _CONTACTCREATEREPLY._serialized_end=2801
  _CONTACTDELETEREQUEST._serialized_start=2803
  _CONTACTDELETEREQUEST._serialized_end=2860
  _CONTACTDELETEREPLY._serialized_start=2862
  _CONTACTDELETEREPLY._serialized_end=2952
  _CONTACTUPDATEREQUEST._serialized_start=2955
  _CONTACTUPDATEREQUEST._serialized_end=3800
  _CONTACTUPDATEREPLY._serialized_start=3802
  _CONTACTUPDATEREPLY._serialized_end=3892
  _CONTACTTRANSFERQUERYREQUEST._serialized_start=3894
  _CONTACTTRANSFERQUERYREQUEST._serialized_end=4007
  _CONTACTTRANSFERREQUESTREQUEST._serialized_start=4009
  _CONTACTTRANSFERREQUESTREQUEST._serialized_end=4094
  _CONTACTTRANSFERREPLY._serialized_start=4097
  _CONTACTTRANSFERREPLY._serialized_end=4383
  _CONTACTPANREPLY._serialized_start=4386
  _CONTACTPANREPLY._serialized_end=4595
# @@protoc_insertion_point(module_scope)
