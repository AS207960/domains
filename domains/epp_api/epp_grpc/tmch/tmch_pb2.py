# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tmch/tmch.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from ..common import common_pb2 as common_dot_common__pb2
from ..marks import marks_pb2 as marks_dot_marks__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ftmch/tmch.proto\x12\x08\x65pp.tmch\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x13\x63ommon/common.proto\x1a\x11marks/marks.proto\"5\n\x10MarkCheckRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x02 \x01(\t\"\x83\x01\n\x11MarkCheckResponse\x12\x11\n\tavailable\x18\x01 \x01(\x08\x12,\n\x06reason\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"E\n\x0b\x42\x61lanceData\x12\r\n\x05value\x18\x01 \x01(\t\x12\x10\n\x08\x63urrency\x18\x02 \x01(\t\x12\x15\n\rstatus_points\x18\x03 \x01(\r\"\xcf\x01\n\x11MarkCreateRequest\x12\x1d\n\x04mark\x18\x01 \x01(\x0b\x32\x0f.epp.marks.Mark\x12\"\n\x06period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\x12%\n\tdocuments\x18\x03 \x03(\x0b\x32\x12.epp.tmch.Document\x12%\n\x06labels\x18\x04 \x03(\x0b\x32\x15.epp.tmch.CreateLabel\x12\x12\n\nvariations\x18\x05 \x03(\t\x12\x15\n\rregistry_name\x18\x06 \x01(\t\"\x87\x01\n\x08\x44ocument\x12/\n\x0e\x64ocument_class\x18\x01 \x01(\x0e\x32\x17.epp.tmch.DocumentClass\x12\x11\n\tfile_name\x18\x02 \x01(\t\x12%\n\tfile_type\x18\x03 \x01(\x0e\x32\x12.epp.tmch.FileType\x12\x10\n\x08\x63ontents\x18\x04 \x01(\x0c\"J\n\x0b\x43reateLabel\x12\r\n\x05label\x18\x01 \x01(\t\x12\x15\n\rsmd_inclusion\x18\x02 \x01(\x08\x12\x15\n\rclaims_notify\x18\x03 \x01(\x08\"\xa9\x01\n\x12MarkCreateResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\x30\n\x0c\x63reated_date\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12&\n\x07\x62\x61lance\x18\x03 \x01(\x0b\x32\x15.epp.tmch.BalanceData\x12-\n\x08\x63md_resp\x18\x04 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"4\n\x0fMarkInfoRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x02 \x01(\t\"j\n\nMarkStatus\x12-\n\x0bstatus_type\x18\x01 \x01(\x0e\x32\x18.epp.tmch.MarkStatusType\x12-\n\x07message\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"p\n\rMarkPOUStatus\x12\x30\n\x0bstatus_type\x18\x01 \x01(\x0e\x32\x1b.epp.tmch.MarkPOUStatusType\x12-\n\x07message\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xf0\x03\n\x10MarkInfoResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12$\n\x06status\x18\x02 \x01(\x0b\x32\x14.epp.tmch.MarkStatus\x12+\n\npou_status\x18\x03 \x01(\x0b\x32\x17.epp.tmch.MarkPOUStatus\x12#\n\x06labels\x18\x04 \x03(\x0b\x32\x13.epp.tmch.MarkLabel\x12+\n\nvariations\x18\x0b \x03(\x0b\x32\x17.epp.tmch.MarkVariation\x12\x31\n\rcreation_date\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12/\n\x0bupdate_date\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12/\n\x0b\x65xpiry_date\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x33\n\x0fpou_expiry_date\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x32\n\x0e\x63orrect_before\x18\t \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x08\x63md_resp\x18\n \x01(\x0b\x32\x1b.epp.common.CommandResponse\"Z\n\tMarkLabel\x12\x0f\n\x07\x61_label\x18\x01 \x01(\t\x12\x0f\n\x07u_label\x18\x02 \x01(\t\x12\x15\n\rsmd_inclusion\x18\x03 \x01(\x08\x12\x14\n\x0c\x63laim_notify\x18\x04 \x01(\x08\"u\n\rMarkLabelTrex\x12\x0f\n\x07\x65nabled\x18\x01 \x01(\x08\x12)\n\x05until\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12(\n\x04tlds\x18\x03 \x03(\x0b\x32\x1a.epp.tmch.MarkLabelTrexTLD\"t\n\x10MarkLabelTrexTLD\x12\x0b\n\x03tld\x18\x01 \x01(\t\x12-\n\x07\x63omment\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12$\n\x06status\x18\x03 \x01(\x0e\x32\x14.epp.tmch.TrexStatus\"Y\n\rMarkVariation\x12\x0f\n\x07\x61_label\x18\x01 \x01(\t\x12\x0f\n\x07u_label\x18\x02 \x01(\t\x12\x16\n\x0evariation_type\x18\x03 \x01(\t\x12\x0e\n\x06\x61\x63tive\x18\x04 \x01(\x08\"\x93\x01\n\x13MarkSMDInfoResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12$\n\x06status\x18\x02 \x01(\x0b\x32\x14.epp.tmch.MarkStatus\x12\x0e\n\x06smd_id\x18\x03 \x01(\t\x12\x0b\n\x03smd\x18\x04 \x01(\t\x12-\n\x08\x63md_resp\x18\x05 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"\x85\x02\n\x11MarkUpdateRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12$\n\x03\x61\x64\x64\x18\x02 \x03(\x0b\x32\x17.epp.tmch.MarkUpdateAdd\x12*\n\x06remove\x18\x03 \x03(\x0b\x32\x1a.epp.tmch.MarkUpdateRemove\x12!\n\x08new_mark\x18\x04 \x01(\x0b\x32\x0f.epp.marks.Mark\x12,\n\rupdate_labels\x18\x05 \x03(\x0b\x32\x15.epp.tmch.CreateLabel\x12*\n\x0cupdate_cases\x18\x06 \x03(\x0b\x32\x14.epp.tmch.CaseUpdate\x12\x15\n\rregistry_name\x18\x07 \x01(\t\"C\n\x12MarkUpdateResponse\x12-\n\x08\x63md_resp\x18\x01 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"\xa1\x01\n\rMarkUpdateAdd\x12&\n\x08\x64ocument\x18\x01 \x01(\x0b\x32\x12.epp.tmch.DocumentH\x00\x12&\n\x05label\x18\x02 \x01(\x0b\x32\x15.epp.tmch.CreateLabelH\x00\x12\x13\n\tvariation\x18\x03 \x01(\tH\x00\x12!\n\x04\x63\x61se\x18\x04 \x01(\x0b\x32\x11.epp.tmch.AddCaseH\x00\x42\x08\n\x06update\"B\n\x10MarkUpdateRemove\x12\x0f\n\x05label\x18\x01 \x01(\tH\x00\x12\x13\n\tvariation\x18\x02 \x01(\tH\x00\x42\x08\n\x06update\"\xa2\x01\n\x07\x41\x64\x64\x43\x61se\x12\n\n\x02id\x18\x01 \x01(\t\x12\"\n\x04udrp\x18\x02 \x01(\x0b\x32\x12.epp.tmch.UDRPCaseH\x00\x12$\n\x05\x63ourt\x18\x03 \x01(\x0b\x32\x13.epp.tmch.CourtCaseH\x00\x12)\n\tdocuments\x18\x04 \x03(\x0b\x32\x16.epp.tmch.CaseDocument\x12\x0e\n\x06labels\x18\x05 \x03(\tB\x06\n\x04\x63\x61se\"\xbc\x01\n\nCaseUpdate\x12\n\n\x02id\x18\x01 \x01(\t\x12\x1e\n\x03\x61\x64\x64\x18\x02 \x03(\x0b\x32\x11.epp.tmch.CaseAdd\x12$\n\x06remove\x18\x03 \x03(\x0b\x32\x14.epp.tmch.CaseRemove\x12&\n\x08new_udrp\x18\x04 \x01(\x0b\x32\x12.epp.tmch.UDRPCaseH\x00\x12(\n\tnew_court\x18\x05 \x01(\x0b\x32\x13.epp.tmch.CourtCaseH\x00\x42\n\n\x08new_case\"P\n\x07\x43\x61seAdd\x12*\n\x08\x64ocument\x18\x04 \x01(\x0b\x32\x16.epp.tmch.CaseDocumentH\x00\x12\x0f\n\x05label\x18\x02 \x01(\tH\x00\x42\x08\n\x06update\"\'\n\nCaseRemove\x12\x0f\n\x05label\x18\x01 \x01(\tH\x00\x42\x08\n\x06update\"D\n\x08UDRPCase\x12\x0f\n\x07\x63\x61se_id\x18\x01 \x01(\t\x12\x10\n\x08provider\x18\x02 \x01(\t\x12\x15\n\rcase_language\x18\x03 \x01(\t\"r\n\tCourtCase\x12\x13\n\x0b\x64\x65\x63ision_id\x18\x01 \x01(\t\x12\x12\n\ncourt_name\x18\x02 \x01(\t\x12\x14\n\x0c\x63ountry_code\x18\x03 \x01(\t\x12\x15\n\rcase_language\x18\x04 \x01(\t\x12\x0f\n\x07regions\x18\x05 \x03(\t\"\x90\x01\n\x0c\x43\x61seDocument\x12\x34\n\x0e\x64ocument_class\x18\x01 \x01(\x0e\x32\x1c.epp.tmch.CourtDocumentClass\x12\x11\n\tfile_name\x18\x02 \x01(\t\x12%\n\tfile_type\x18\x03 \x01(\x0e\x32\x12.epp.tmch.FileType\x12\x10\n\x08\x63ontents\x18\x04 \x01(\x0c\"\x96\x01\n\x10MarkRenewRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12&\n\nadd_period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\x12\x37\n\x13\x63urrent_expiry_date\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x15\n\rregistry_name\x18\x04 \x01(\t\"\xab\x01\n\x11MarkRenewResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\x33\n\x0fnew_expiry_date\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12&\n\x07\x62\x61lance\x18\x03 \x01(\x0b\x32\x15.epp.tmch.BalanceData\x12-\n\x08\x63md_resp\x18\x04 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"K\n\x13MarkTransferRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x11\n\tauth_info\x18\x02 \x01(\t\x12\x15\n\rregistry_name\x18\x03 \x01(\t\"\xac\x01\n\x14MarkTransferResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\x31\n\rtransfer_date\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12&\n\x07\x62\x61lance\x18\x03 \x01(\x0b\x32\x15.epp.tmch.BalanceData\x12-\n\x08\x63md_resp\x18\x04 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"@\n\x1bMarkTransferInitiateRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x03 \x01(\t\"l\n\x1cMarkTransferInitiateResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\x11\n\tauth_info\x18\x02 \x01(\t\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"i\n\x17MarkTrexActivateRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12+\n\x06labels\x18\x02 \x03(\x0b\x32\x1b.epp.tmch.TrexActivateLabel\x12\x15\n\rregistry_name\x18\x04 \x01(\t\"F\n\x11TrexActivateLabel\x12\r\n\x05label\x18\x01 \x01(\t\x12\"\n\x06period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\"I\n\x18MarkTrexActivateResponse\x12-\n\x08\x63md_resp\x18\x01 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"c\n\x14MarkTrexRenewRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12(\n\x06labels\x18\x02 \x03(\x0b\x32\x18.epp.tmch.TrexRenewLabel\x12\x15\n\rregistry_name\x18\x04 \x01(\t\"\x80\x01\n\x0eTrexRenewLabel\x12\r\n\x05label\x18\x01 \x01(\t\x12&\n\nadd_period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\x12\x37\n\x13\x63urrent_expiry_date\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"F\n\x15MarkTrexRenewResponse\x12-\n\x08\x63md_resp\x18\x01 \x01(\x0b\x32\x1b.epp.common.CommandResponse*\x9b\x01\n\rDocumentClass\x12\t\n\x05Other\x10\x00\x12\x17\n\x13LicenseeDeclaration\x10\x01\x12\x17\n\x13\x41ssigneeDeclaration\x10\x02\x12\"\n\x1e\x44\x65\x63larationProofOfUseOneSample\x10\x03\x12\x13\n\x0fOtherProofOfUse\x10\x04\x12\x14\n\x10\x43opyOfCourtOrder\x10\x05*\x1c\n\x08\x46ileType\x12\x07\n\x03PDF\x10\x00\x12\x07\n\x03JPG\x10\x01*}\n\x0eMarkStatusType\x12\x0b\n\x07Unknown\x10\x00\x12\x07\n\x03New\x10\x01\x12\x0c\n\x08Verified\x10\x02\x12\r\n\tIncorrect\x10\x03\x12\r\n\tCorrected\x10\x04\x12\x0b\n\x07Invalid\x10\x05\x12\x0b\n\x07\x45xpired\x10\x06\x12\x0f\n\x0b\x44\x65\x61\x63tivated\x10\x07*\x8b\x01\n\x11MarkPOUStatusType\x12\r\n\tPOUNotSet\x10\x00\x12\x0c\n\x08POUValid\x10\x01\x12\x0e\n\nPOUInvalid\x10\x02\x12\x0e\n\nPOUExpired\x10\x03\x12\t\n\x05POUNA\x10\x04\x12\n\n\x06POUNew\x10\x05\x12\x10\n\x0cPOUIncorrect\x10\x06\x12\x10\n\x0cPOUCorrected\x10\x07*\xab\x01\n\nTrexStatus\x12\n\n\x06NoInfo\x10\x00\x12\x18\n\x14NotProtectedOverride\x10\x01\x12\x1a\n\x16NotProtectedRegistered\x10\x02\x12\x16\n\x12NotProtectedExempt\x10\x03\x12\x15\n\x11NotProtectedOther\x10\x04\x12\r\n\tProtected\x10\x05\x12\x0f\n\x0bUnavailable\x10\x06\x12\x0c\n\x08\x45ligible\x10\x07*7\n\x12\x43ourtDocumentClass\x12\x0e\n\nCourtOther\x10\x00\x12\x11\n\rCourtDecision\x10\x01\x42/Z-github.com/as207960/epp-proxy/gen/go/epp/tmchb\x06proto3')

_DOCUMENTCLASS = DESCRIPTOR.enum_types_by_name['DocumentClass']
DocumentClass = enum_type_wrapper.EnumTypeWrapper(_DOCUMENTCLASS)
_FILETYPE = DESCRIPTOR.enum_types_by_name['FileType']
FileType = enum_type_wrapper.EnumTypeWrapper(_FILETYPE)
_MARKSTATUSTYPE = DESCRIPTOR.enum_types_by_name['MarkStatusType']
MarkStatusType = enum_type_wrapper.EnumTypeWrapper(_MARKSTATUSTYPE)
_MARKPOUSTATUSTYPE = DESCRIPTOR.enum_types_by_name['MarkPOUStatusType']
MarkPOUStatusType = enum_type_wrapper.EnumTypeWrapper(_MARKPOUSTATUSTYPE)
_TREXSTATUS = DESCRIPTOR.enum_types_by_name['TrexStatus']
TrexStatus = enum_type_wrapper.EnumTypeWrapper(_TREXSTATUS)
_COURTDOCUMENTCLASS = DESCRIPTOR.enum_types_by_name['CourtDocumentClass']
CourtDocumentClass = enum_type_wrapper.EnumTypeWrapper(_COURTDOCUMENTCLASS)
Other = 0
LicenseeDeclaration = 1
AssigneeDeclaration = 2
DeclarationProofOfUseOneSample = 3
OtherProofOfUse = 4
CopyOfCourtOrder = 5
PDF = 0
JPG = 1
Unknown = 0
New = 1
Verified = 2
Incorrect = 3
Corrected = 4
Invalid = 5
Expired = 6
Deactivated = 7
POUNotSet = 0
POUValid = 1
POUInvalid = 2
POUExpired = 3
POUNA = 4
POUNew = 5
POUIncorrect = 6
POUCorrected = 7
NoInfo = 0
NotProtectedOverride = 1
NotProtectedRegistered = 2
NotProtectedExempt = 3
NotProtectedOther = 4
Protected = 5
Unavailable = 6
Eligible = 7
CourtOther = 0
CourtDecision = 1


_MARKCHECKREQUEST = DESCRIPTOR.message_types_by_name['MarkCheckRequest']
_MARKCHECKRESPONSE = DESCRIPTOR.message_types_by_name['MarkCheckResponse']
_BALANCEDATA = DESCRIPTOR.message_types_by_name['BalanceData']
_MARKCREATEREQUEST = DESCRIPTOR.message_types_by_name['MarkCreateRequest']
_DOCUMENT = DESCRIPTOR.message_types_by_name['Document']
_CREATELABEL = DESCRIPTOR.message_types_by_name['CreateLabel']
_MARKCREATERESPONSE = DESCRIPTOR.message_types_by_name['MarkCreateResponse']
_MARKINFOREQUEST = DESCRIPTOR.message_types_by_name['MarkInfoRequest']
_MARKSTATUS = DESCRIPTOR.message_types_by_name['MarkStatus']
_MARKPOUSTATUS = DESCRIPTOR.message_types_by_name['MarkPOUStatus']
_MARKINFORESPONSE = DESCRIPTOR.message_types_by_name['MarkInfoResponse']
_MARKLABEL = DESCRIPTOR.message_types_by_name['MarkLabel']
_MARKLABELTREX = DESCRIPTOR.message_types_by_name['MarkLabelTrex']
_MARKLABELTREXTLD = DESCRIPTOR.message_types_by_name['MarkLabelTrexTLD']
_MARKVARIATION = DESCRIPTOR.message_types_by_name['MarkVariation']
_MARKSMDINFORESPONSE = DESCRIPTOR.message_types_by_name['MarkSMDInfoResponse']
_MARKUPDATEREQUEST = DESCRIPTOR.message_types_by_name['MarkUpdateRequest']
_MARKUPDATERESPONSE = DESCRIPTOR.message_types_by_name['MarkUpdateResponse']
_MARKUPDATEADD = DESCRIPTOR.message_types_by_name['MarkUpdateAdd']
_MARKUPDATEREMOVE = DESCRIPTOR.message_types_by_name['MarkUpdateRemove']
_ADDCASE = DESCRIPTOR.message_types_by_name['AddCase']
_CASEUPDATE = DESCRIPTOR.message_types_by_name['CaseUpdate']
_CASEADD = DESCRIPTOR.message_types_by_name['CaseAdd']
_CASEREMOVE = DESCRIPTOR.message_types_by_name['CaseRemove']
_UDRPCASE = DESCRIPTOR.message_types_by_name['UDRPCase']
_COURTCASE = DESCRIPTOR.message_types_by_name['CourtCase']
_CASEDOCUMENT = DESCRIPTOR.message_types_by_name['CaseDocument']
_MARKRENEWREQUEST = DESCRIPTOR.message_types_by_name['MarkRenewRequest']
_MARKRENEWRESPONSE = DESCRIPTOR.message_types_by_name['MarkRenewResponse']
_MARKTRANSFERREQUEST = DESCRIPTOR.message_types_by_name['MarkTransferRequest']
_MARKTRANSFERRESPONSE = DESCRIPTOR.message_types_by_name['MarkTransferResponse']
_MARKTRANSFERINITIATEREQUEST = DESCRIPTOR.message_types_by_name['MarkTransferInitiateRequest']
_MARKTRANSFERINITIATERESPONSE = DESCRIPTOR.message_types_by_name['MarkTransferInitiateResponse']
_MARKTREXACTIVATEREQUEST = DESCRIPTOR.message_types_by_name['MarkTrexActivateRequest']
_TREXACTIVATELABEL = DESCRIPTOR.message_types_by_name['TrexActivateLabel']
_MARKTREXACTIVATERESPONSE = DESCRIPTOR.message_types_by_name['MarkTrexActivateResponse']
_MARKTREXRENEWREQUEST = DESCRIPTOR.message_types_by_name['MarkTrexRenewRequest']
_TREXRENEWLABEL = DESCRIPTOR.message_types_by_name['TrexRenewLabel']
_MARKTREXRENEWRESPONSE = DESCRIPTOR.message_types_by_name['MarkTrexRenewResponse']
MarkCheckRequest = _reflection.GeneratedProtocolMessageType('MarkCheckRequest', (_message.Message,), {
  'DESCRIPTOR' : _MARKCHECKREQUEST,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkCheckRequest)
  })
_sym_db.RegisterMessage(MarkCheckRequest)

MarkCheckResponse = _reflection.GeneratedProtocolMessageType('MarkCheckResponse', (_message.Message,), {
  'DESCRIPTOR' : _MARKCHECKRESPONSE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkCheckResponse)
  })
_sym_db.RegisterMessage(MarkCheckResponse)

BalanceData = _reflection.GeneratedProtocolMessageType('BalanceData', (_message.Message,), {
  'DESCRIPTOR' : _BALANCEDATA,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.BalanceData)
  })
_sym_db.RegisterMessage(BalanceData)

MarkCreateRequest = _reflection.GeneratedProtocolMessageType('MarkCreateRequest', (_message.Message,), {
  'DESCRIPTOR' : _MARKCREATEREQUEST,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkCreateRequest)
  })
_sym_db.RegisterMessage(MarkCreateRequest)

Document = _reflection.GeneratedProtocolMessageType('Document', (_message.Message,), {
  'DESCRIPTOR' : _DOCUMENT,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.Document)
  })
_sym_db.RegisterMessage(Document)

CreateLabel = _reflection.GeneratedProtocolMessageType('CreateLabel', (_message.Message,), {
  'DESCRIPTOR' : _CREATELABEL,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.CreateLabel)
  })
_sym_db.RegisterMessage(CreateLabel)

MarkCreateResponse = _reflection.GeneratedProtocolMessageType('MarkCreateResponse', (_message.Message,), {
  'DESCRIPTOR' : _MARKCREATERESPONSE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkCreateResponse)
  })
_sym_db.RegisterMessage(MarkCreateResponse)

MarkInfoRequest = _reflection.GeneratedProtocolMessageType('MarkInfoRequest', (_message.Message,), {
  'DESCRIPTOR' : _MARKINFOREQUEST,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkInfoRequest)
  })
_sym_db.RegisterMessage(MarkInfoRequest)

MarkStatus = _reflection.GeneratedProtocolMessageType('MarkStatus', (_message.Message,), {
  'DESCRIPTOR' : _MARKSTATUS,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkStatus)
  })
_sym_db.RegisterMessage(MarkStatus)

MarkPOUStatus = _reflection.GeneratedProtocolMessageType('MarkPOUStatus', (_message.Message,), {
  'DESCRIPTOR' : _MARKPOUSTATUS,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkPOUStatus)
  })
_sym_db.RegisterMessage(MarkPOUStatus)

MarkInfoResponse = _reflection.GeneratedProtocolMessageType('MarkInfoResponse', (_message.Message,), {
  'DESCRIPTOR' : _MARKINFORESPONSE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkInfoResponse)
  })
_sym_db.RegisterMessage(MarkInfoResponse)

MarkLabel = _reflection.GeneratedProtocolMessageType('MarkLabel', (_message.Message,), {
  'DESCRIPTOR' : _MARKLABEL,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkLabel)
  })
_sym_db.RegisterMessage(MarkLabel)

MarkLabelTrex = _reflection.GeneratedProtocolMessageType('MarkLabelTrex', (_message.Message,), {
  'DESCRIPTOR' : _MARKLABELTREX,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkLabelTrex)
  })
_sym_db.RegisterMessage(MarkLabelTrex)

MarkLabelTrexTLD = _reflection.GeneratedProtocolMessageType('MarkLabelTrexTLD', (_message.Message,), {
  'DESCRIPTOR' : _MARKLABELTREXTLD,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkLabelTrexTLD)
  })
_sym_db.RegisterMessage(MarkLabelTrexTLD)

MarkVariation = _reflection.GeneratedProtocolMessageType('MarkVariation', (_message.Message,), {
  'DESCRIPTOR' : _MARKVARIATION,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkVariation)
  })
_sym_db.RegisterMessage(MarkVariation)

MarkSMDInfoResponse = _reflection.GeneratedProtocolMessageType('MarkSMDInfoResponse', (_message.Message,), {
  'DESCRIPTOR' : _MARKSMDINFORESPONSE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkSMDInfoResponse)
  })
_sym_db.RegisterMessage(MarkSMDInfoResponse)

MarkUpdateRequest = _reflection.GeneratedProtocolMessageType('MarkUpdateRequest', (_message.Message,), {
  'DESCRIPTOR' : _MARKUPDATEREQUEST,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkUpdateRequest)
  })
_sym_db.RegisterMessage(MarkUpdateRequest)

MarkUpdateResponse = _reflection.GeneratedProtocolMessageType('MarkUpdateResponse', (_message.Message,), {
  'DESCRIPTOR' : _MARKUPDATERESPONSE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkUpdateResponse)
  })
_sym_db.RegisterMessage(MarkUpdateResponse)

MarkUpdateAdd = _reflection.GeneratedProtocolMessageType('MarkUpdateAdd', (_message.Message,), {
  'DESCRIPTOR' : _MARKUPDATEADD,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkUpdateAdd)
  })
_sym_db.RegisterMessage(MarkUpdateAdd)

MarkUpdateRemove = _reflection.GeneratedProtocolMessageType('MarkUpdateRemove', (_message.Message,), {
  'DESCRIPTOR' : _MARKUPDATEREMOVE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkUpdateRemove)
  })
_sym_db.RegisterMessage(MarkUpdateRemove)

AddCase = _reflection.GeneratedProtocolMessageType('AddCase', (_message.Message,), {
  'DESCRIPTOR' : _ADDCASE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.AddCase)
  })
_sym_db.RegisterMessage(AddCase)

CaseUpdate = _reflection.GeneratedProtocolMessageType('CaseUpdate', (_message.Message,), {
  'DESCRIPTOR' : _CASEUPDATE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.CaseUpdate)
  })
_sym_db.RegisterMessage(CaseUpdate)

CaseAdd = _reflection.GeneratedProtocolMessageType('CaseAdd', (_message.Message,), {
  'DESCRIPTOR' : _CASEADD,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.CaseAdd)
  })
_sym_db.RegisterMessage(CaseAdd)

CaseRemove = _reflection.GeneratedProtocolMessageType('CaseRemove', (_message.Message,), {
  'DESCRIPTOR' : _CASEREMOVE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.CaseRemove)
  })
_sym_db.RegisterMessage(CaseRemove)

UDRPCase = _reflection.GeneratedProtocolMessageType('UDRPCase', (_message.Message,), {
  'DESCRIPTOR' : _UDRPCASE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.UDRPCase)
  })
_sym_db.RegisterMessage(UDRPCase)

CourtCase = _reflection.GeneratedProtocolMessageType('CourtCase', (_message.Message,), {
  'DESCRIPTOR' : _COURTCASE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.CourtCase)
  })
_sym_db.RegisterMessage(CourtCase)

CaseDocument = _reflection.GeneratedProtocolMessageType('CaseDocument', (_message.Message,), {
  'DESCRIPTOR' : _CASEDOCUMENT,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.CaseDocument)
  })
_sym_db.RegisterMessage(CaseDocument)

MarkRenewRequest = _reflection.GeneratedProtocolMessageType('MarkRenewRequest', (_message.Message,), {
  'DESCRIPTOR' : _MARKRENEWREQUEST,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkRenewRequest)
  })
_sym_db.RegisterMessage(MarkRenewRequest)

MarkRenewResponse = _reflection.GeneratedProtocolMessageType('MarkRenewResponse', (_message.Message,), {
  'DESCRIPTOR' : _MARKRENEWRESPONSE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkRenewResponse)
  })
_sym_db.RegisterMessage(MarkRenewResponse)

MarkTransferRequest = _reflection.GeneratedProtocolMessageType('MarkTransferRequest', (_message.Message,), {
  'DESCRIPTOR' : _MARKTRANSFERREQUEST,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkTransferRequest)
  })
_sym_db.RegisterMessage(MarkTransferRequest)

MarkTransferResponse = _reflection.GeneratedProtocolMessageType('MarkTransferResponse', (_message.Message,), {
  'DESCRIPTOR' : _MARKTRANSFERRESPONSE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkTransferResponse)
  })
_sym_db.RegisterMessage(MarkTransferResponse)

MarkTransferInitiateRequest = _reflection.GeneratedProtocolMessageType('MarkTransferInitiateRequest', (_message.Message,), {
  'DESCRIPTOR' : _MARKTRANSFERINITIATEREQUEST,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkTransferInitiateRequest)
  })
_sym_db.RegisterMessage(MarkTransferInitiateRequest)

MarkTransferInitiateResponse = _reflection.GeneratedProtocolMessageType('MarkTransferInitiateResponse', (_message.Message,), {
  'DESCRIPTOR' : _MARKTRANSFERINITIATERESPONSE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkTransferInitiateResponse)
  })
_sym_db.RegisterMessage(MarkTransferInitiateResponse)

MarkTrexActivateRequest = _reflection.GeneratedProtocolMessageType('MarkTrexActivateRequest', (_message.Message,), {
  'DESCRIPTOR' : _MARKTREXACTIVATEREQUEST,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkTrexActivateRequest)
  })
_sym_db.RegisterMessage(MarkTrexActivateRequest)

TrexActivateLabel = _reflection.GeneratedProtocolMessageType('TrexActivateLabel', (_message.Message,), {
  'DESCRIPTOR' : _TREXACTIVATELABEL,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.TrexActivateLabel)
  })
_sym_db.RegisterMessage(TrexActivateLabel)

MarkTrexActivateResponse = _reflection.GeneratedProtocolMessageType('MarkTrexActivateResponse', (_message.Message,), {
  'DESCRIPTOR' : _MARKTREXACTIVATERESPONSE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkTrexActivateResponse)
  })
_sym_db.RegisterMessage(MarkTrexActivateResponse)

MarkTrexRenewRequest = _reflection.GeneratedProtocolMessageType('MarkTrexRenewRequest', (_message.Message,), {
  'DESCRIPTOR' : _MARKTREXRENEWREQUEST,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkTrexRenewRequest)
  })
_sym_db.RegisterMessage(MarkTrexRenewRequest)

TrexRenewLabel = _reflection.GeneratedProtocolMessageType('TrexRenewLabel', (_message.Message,), {
  'DESCRIPTOR' : _TREXRENEWLABEL,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.TrexRenewLabel)
  })
_sym_db.RegisterMessage(TrexRenewLabel)

MarkTrexRenewResponse = _reflection.GeneratedProtocolMessageType('MarkTrexRenewResponse', (_message.Message,), {
  'DESCRIPTOR' : _MARKTREXRENEWRESPONSE,
  '__module__' : 'tmch.tmch_pb2'
  # @@protoc_insertion_point(class_scope:epp.tmch.MarkTrexRenewResponse)
  })
_sym_db.RegisterMessage(MarkTrexRenewResponse)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z-github.com/as207960/epp-proxy/gen/go/epp/tmch'
  _DOCUMENTCLASS._serialized_start=5026
  _DOCUMENTCLASS._serialized_end=5181
  _FILETYPE._serialized_start=5183
  _FILETYPE._serialized_end=5211
  _MARKSTATUSTYPE._serialized_start=5213
  _MARKSTATUSTYPE._serialized_end=5338
  _MARKPOUSTATUSTYPE._serialized_start=5341
  _MARKPOUSTATUSTYPE._serialized_end=5480
  _TREXSTATUS._serialized_start=5483
  _TREXSTATUS._serialized_end=5654
  _COURTDOCUMENTCLASS._serialized_start=5656
  _COURTDOCUMENTCLASS._serialized_end=5711
  _MARKCHECKREQUEST._serialized_start=134
  _MARKCHECKREQUEST._serialized_end=187
  _MARKCHECKRESPONSE._serialized_start=190
  _MARKCHECKRESPONSE._serialized_end=321
  _BALANCEDATA._serialized_start=323
  _BALANCEDATA._serialized_end=392
  _MARKCREATEREQUEST._serialized_start=395
  _MARKCREATEREQUEST._serialized_end=602
  _DOCUMENT._serialized_start=605
  _DOCUMENT._serialized_end=740
  _CREATELABEL._serialized_start=742
  _CREATELABEL._serialized_end=816
  _MARKCREATERESPONSE._serialized_start=819
  _MARKCREATERESPONSE._serialized_end=988
  _MARKINFOREQUEST._serialized_start=990
  _MARKINFOREQUEST._serialized_end=1042
  _MARKSTATUS._serialized_start=1044
  _MARKSTATUS._serialized_end=1150
  _MARKPOUSTATUS._serialized_start=1152
  _MARKPOUSTATUS._serialized_end=1264
  _MARKINFORESPONSE._serialized_start=1267
  _MARKINFORESPONSE._serialized_end=1763
  _MARKLABEL._serialized_start=1765
  _MARKLABEL._serialized_end=1855
  _MARKLABELTREX._serialized_start=1857
  _MARKLABELTREX._serialized_end=1974
  _MARKLABELTREXTLD._serialized_start=1976
  _MARKLABELTREXTLD._serialized_end=2092
  _MARKVARIATION._serialized_start=2094
  _MARKVARIATION._serialized_end=2183
  _MARKSMDINFORESPONSE._serialized_start=2186
  _MARKSMDINFORESPONSE._serialized_end=2333
  _MARKUPDATEREQUEST._serialized_start=2336
  _MARKUPDATEREQUEST._serialized_end=2597
  _MARKUPDATERESPONSE._serialized_start=2599
  _MARKUPDATERESPONSE._serialized_end=2666
  _MARKUPDATEADD._serialized_start=2669
  _MARKUPDATEADD._serialized_end=2830
  _MARKUPDATEREMOVE._serialized_start=2832
  _MARKUPDATEREMOVE._serialized_end=2898
  _ADDCASE._serialized_start=2901
  _ADDCASE._serialized_end=3063
  _CASEUPDATE._serialized_start=3066
  _CASEUPDATE._serialized_end=3254
  _CASEADD._serialized_start=3256
  _CASEADD._serialized_end=3336
  _CASEREMOVE._serialized_start=3338
  _CASEREMOVE._serialized_end=3377
  _UDRPCASE._serialized_start=3379
  _UDRPCASE._serialized_end=3447
  _COURTCASE._serialized_start=3449
  _COURTCASE._serialized_end=3563
  _CASEDOCUMENT._serialized_start=3566
  _CASEDOCUMENT._serialized_end=3710
  _MARKRENEWREQUEST._serialized_start=3713
  _MARKRENEWREQUEST._serialized_end=3863
  _MARKRENEWRESPONSE._serialized_start=3866
  _MARKRENEWRESPONSE._serialized_end=4037
  _MARKTRANSFERREQUEST._serialized_start=4039
  _MARKTRANSFERREQUEST._serialized_end=4114
  _MARKTRANSFERRESPONSE._serialized_start=4117
  _MARKTRANSFERRESPONSE._serialized_end=4289
  _MARKTRANSFERINITIATEREQUEST._serialized_start=4291
  _MARKTRANSFERINITIATEREQUEST._serialized_end=4355
  _MARKTRANSFERINITIATERESPONSE._serialized_start=4357
  _MARKTRANSFERINITIATERESPONSE._serialized_end=4465
  _MARKTREXACTIVATEREQUEST._serialized_start=4467
  _MARKTREXACTIVATEREQUEST._serialized_end=4572
  _TREXACTIVATELABEL._serialized_start=4574
  _TREXACTIVATELABEL._serialized_end=4644
  _MARKTREXACTIVATERESPONSE._serialized_start=4646
  _MARKTREXACTIVATERESPONSE._serialized_end=4719
  _MARKTREXRENEWREQUEST._serialized_start=4721
  _MARKTREXRENEWREQUEST._serialized_end=4820
  _TREXRENEWLABEL._serialized_start=4823
  _TREXRENEWLABEL._serialized_end=4951
  _MARKTREXRENEWRESPONSE._serialized_start=4953
  _MARKTREXRENEWRESPONSE._serialized_end=5023
# @@protoc_insertion_point(module_scope)
