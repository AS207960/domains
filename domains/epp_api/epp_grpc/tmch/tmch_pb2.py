# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: tmch/tmch.proto
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
    'tmch/tmch.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from ..common import common_pb2 as common_dot_common__pb2
from ..marks import marks_pb2 as marks_dot_marks__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ftmch/tmch.proto\x12\x08\x65pp.tmch\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x13\x63ommon/common.proto\x1a\x11marks/marks.proto\"5\n\x10MarkCheckRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x02 \x01(\t\"\x83\x01\n\x11MarkCheckResponse\x12\x11\n\tavailable\x18\x01 \x01(\x08\x12,\n\x06reason\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"E\n\x0b\x42\x61lanceData\x12\r\n\x05value\x18\x01 \x01(\t\x12\x10\n\x08\x63urrency\x18\x02 \x01(\t\x12\x15\n\rstatus_points\x18\x03 \x01(\r\"\xcf\x01\n\x11MarkCreateRequest\x12\x1d\n\x04mark\x18\x01 \x01(\x0b\x32\x0f.epp.marks.Mark\x12\"\n\x06period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\x12%\n\tdocuments\x18\x03 \x03(\x0b\x32\x12.epp.tmch.Document\x12%\n\x06labels\x18\x04 \x03(\x0b\x32\x15.epp.tmch.CreateLabel\x12\x12\n\nvariations\x18\x05 \x03(\t\x12\x15\n\rregistry_name\x18\x06 \x01(\t\"\x87\x01\n\x08\x44ocument\x12/\n\x0e\x64ocument_class\x18\x01 \x01(\x0e\x32\x17.epp.tmch.DocumentClass\x12\x11\n\tfile_name\x18\x02 \x01(\t\x12%\n\tfile_type\x18\x03 \x01(\x0e\x32\x12.epp.tmch.FileType\x12\x10\n\x08\x63ontents\x18\x04 \x01(\x0c\"J\n\x0b\x43reateLabel\x12\r\n\x05label\x18\x01 \x01(\t\x12\x15\n\rsmd_inclusion\x18\x02 \x01(\x08\x12\x15\n\rclaims_notify\x18\x03 \x01(\x08\"\xa9\x01\n\x12MarkCreateResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\x30\n\x0c\x63reated_date\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12&\n\x07\x62\x61lance\x18\x03 \x01(\x0b\x32\x15.epp.tmch.BalanceData\x12-\n\x08\x63md_resp\x18\x04 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"4\n\x0fMarkInfoRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x02 \x01(\t\"j\n\nMarkStatus\x12-\n\x0bstatus_type\x18\x01 \x01(\x0e\x32\x18.epp.tmch.MarkStatusType\x12-\n\x07message\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"p\n\rMarkPOUStatus\x12\x30\n\x0bstatus_type\x18\x01 \x01(\x0e\x32\x1b.epp.tmch.MarkPOUStatusType\x12-\n\x07message\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\"\xf0\x03\n\x10MarkInfoResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12$\n\x06status\x18\x02 \x01(\x0b\x32\x14.epp.tmch.MarkStatus\x12+\n\npou_status\x18\x03 \x01(\x0b\x32\x17.epp.tmch.MarkPOUStatus\x12#\n\x06labels\x18\x04 \x03(\x0b\x32\x13.epp.tmch.MarkLabel\x12+\n\nvariations\x18\x0b \x03(\x0b\x32\x17.epp.tmch.MarkVariation\x12\x31\n\rcreation_date\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12/\n\x0bupdate_date\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12/\n\x0b\x65xpiry_date\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x33\n\x0fpou_expiry_date\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x32\n\x0e\x63orrect_before\x18\t \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12-\n\x08\x63md_resp\x18\n \x01(\x0b\x32\x1b.epp.common.CommandResponse\"Z\n\tMarkLabel\x12\x0f\n\x07\x61_label\x18\x01 \x01(\t\x12\x0f\n\x07u_label\x18\x02 \x01(\t\x12\x15\n\rsmd_inclusion\x18\x03 \x01(\x08\x12\x14\n\x0c\x63laim_notify\x18\x04 \x01(\x08\"u\n\rMarkLabelTrex\x12\x0f\n\x07\x65nabled\x18\x01 \x01(\x08\x12)\n\x05until\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12(\n\x04tlds\x18\x03 \x03(\x0b\x32\x1a.epp.tmch.MarkLabelTrexTLD\"t\n\x10MarkLabelTrexTLD\x12\x0b\n\x03tld\x18\x01 \x01(\t\x12-\n\x07\x63omment\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.StringValue\x12$\n\x06status\x18\x03 \x01(\x0e\x32\x14.epp.tmch.TrexStatus\"Y\n\rMarkVariation\x12\x0f\n\x07\x61_label\x18\x01 \x01(\t\x12\x0f\n\x07u_label\x18\x02 \x01(\t\x12\x16\n\x0evariation_type\x18\x03 \x01(\t\x12\x0e\n\x06\x61\x63tive\x18\x04 \x01(\x08\"\x93\x01\n\x13MarkSMDInfoResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12$\n\x06status\x18\x02 \x01(\x0b\x32\x14.epp.tmch.MarkStatus\x12\x0e\n\x06smd_id\x18\x03 \x01(\t\x12\x0b\n\x03smd\x18\x04 \x01(\t\x12-\n\x08\x63md_resp\x18\x05 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"\x85\x02\n\x11MarkUpdateRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12$\n\x03\x61\x64\x64\x18\x02 \x03(\x0b\x32\x17.epp.tmch.MarkUpdateAdd\x12*\n\x06remove\x18\x03 \x03(\x0b\x32\x1a.epp.tmch.MarkUpdateRemove\x12!\n\x08new_mark\x18\x04 \x01(\x0b\x32\x0f.epp.marks.Mark\x12,\n\rupdate_labels\x18\x05 \x03(\x0b\x32\x15.epp.tmch.CreateLabel\x12*\n\x0cupdate_cases\x18\x06 \x03(\x0b\x32\x14.epp.tmch.CaseUpdate\x12\x15\n\rregistry_name\x18\x07 \x01(\t\"C\n\x12MarkUpdateResponse\x12-\n\x08\x63md_resp\x18\x01 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"\xa1\x01\n\rMarkUpdateAdd\x12&\n\x08\x64ocument\x18\x01 \x01(\x0b\x32\x12.epp.tmch.DocumentH\x00\x12&\n\x05label\x18\x02 \x01(\x0b\x32\x15.epp.tmch.CreateLabelH\x00\x12\x13\n\tvariation\x18\x03 \x01(\tH\x00\x12!\n\x04\x63\x61se\x18\x04 \x01(\x0b\x32\x11.epp.tmch.AddCaseH\x00\x42\x08\n\x06update\"B\n\x10MarkUpdateRemove\x12\x0f\n\x05label\x18\x01 \x01(\tH\x00\x12\x13\n\tvariation\x18\x02 \x01(\tH\x00\x42\x08\n\x06update\"\xa2\x01\n\x07\x41\x64\x64\x43\x61se\x12\n\n\x02id\x18\x01 \x01(\t\x12\"\n\x04udrp\x18\x02 \x01(\x0b\x32\x12.epp.tmch.UDRPCaseH\x00\x12$\n\x05\x63ourt\x18\x03 \x01(\x0b\x32\x13.epp.tmch.CourtCaseH\x00\x12)\n\tdocuments\x18\x04 \x03(\x0b\x32\x16.epp.tmch.CaseDocument\x12\x0e\n\x06labels\x18\x05 \x03(\tB\x06\n\x04\x63\x61se\"\xbc\x01\n\nCaseUpdate\x12\n\n\x02id\x18\x01 \x01(\t\x12\x1e\n\x03\x61\x64\x64\x18\x02 \x03(\x0b\x32\x11.epp.tmch.CaseAdd\x12$\n\x06remove\x18\x03 \x03(\x0b\x32\x14.epp.tmch.CaseRemove\x12&\n\x08new_udrp\x18\x04 \x01(\x0b\x32\x12.epp.tmch.UDRPCaseH\x00\x12(\n\tnew_court\x18\x05 \x01(\x0b\x32\x13.epp.tmch.CourtCaseH\x00\x42\n\n\x08new_case\"P\n\x07\x43\x61seAdd\x12*\n\x08\x64ocument\x18\x04 \x01(\x0b\x32\x16.epp.tmch.CaseDocumentH\x00\x12\x0f\n\x05label\x18\x02 \x01(\tH\x00\x42\x08\n\x06update\"\'\n\nCaseRemove\x12\x0f\n\x05label\x18\x01 \x01(\tH\x00\x42\x08\n\x06update\"D\n\x08UDRPCase\x12\x0f\n\x07\x63\x61se_id\x18\x01 \x01(\t\x12\x10\n\x08provider\x18\x02 \x01(\t\x12\x15\n\rcase_language\x18\x03 \x01(\t\"r\n\tCourtCase\x12\x13\n\x0b\x64\x65\x63ision_id\x18\x01 \x01(\t\x12\x12\n\ncourt_name\x18\x02 \x01(\t\x12\x14\n\x0c\x63ountry_code\x18\x03 \x01(\t\x12\x15\n\rcase_language\x18\x04 \x01(\t\x12\x0f\n\x07regions\x18\x05 \x03(\t\"\x90\x01\n\x0c\x43\x61seDocument\x12\x34\n\x0e\x64ocument_class\x18\x01 \x01(\x0e\x32\x1c.epp.tmch.CourtDocumentClass\x12\x11\n\tfile_name\x18\x02 \x01(\t\x12%\n\tfile_type\x18\x03 \x01(\x0e\x32\x12.epp.tmch.FileType\x12\x10\n\x08\x63ontents\x18\x04 \x01(\x0c\"\x96\x01\n\x10MarkRenewRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12&\n\nadd_period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\x12\x37\n\x13\x63urrent_expiry_date\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x15\n\rregistry_name\x18\x04 \x01(\t\"\xab\x01\n\x11MarkRenewResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\x33\n\x0fnew_expiry_date\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12&\n\x07\x62\x61lance\x18\x03 \x01(\x0b\x32\x15.epp.tmch.BalanceData\x12-\n\x08\x63md_resp\x18\x04 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"K\n\x13MarkTransferRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x11\n\tauth_info\x18\x02 \x01(\t\x12\x15\n\rregistry_name\x18\x03 \x01(\t\"\xac\x01\n\x14MarkTransferResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\x31\n\rtransfer_date\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12&\n\x07\x62\x61lance\x18\x03 \x01(\x0b\x32\x15.epp.tmch.BalanceData\x12-\n\x08\x63md_resp\x18\x04 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"@\n\x1bMarkTransferInitiateRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x15\n\rregistry_name\x18\x03 \x01(\t\"l\n\x1cMarkTransferInitiateResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\x11\n\tauth_info\x18\x02 \x01(\t\x12-\n\x08\x63md_resp\x18\x03 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"i\n\x17MarkTrexActivateRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12+\n\x06labels\x18\x02 \x03(\x0b\x32\x1b.epp.tmch.TrexActivateLabel\x12\x15\n\rregistry_name\x18\x04 \x01(\t\"F\n\x11TrexActivateLabel\x12\r\n\x05label\x18\x01 \x01(\t\x12\"\n\x06period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\"I\n\x18MarkTrexActivateResponse\x12-\n\x08\x63md_resp\x18\x01 \x01(\x0b\x32\x1b.epp.common.CommandResponse\"c\n\x14MarkTrexRenewRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12(\n\x06labels\x18\x02 \x03(\x0b\x32\x18.epp.tmch.TrexRenewLabel\x12\x15\n\rregistry_name\x18\x04 \x01(\t\"\x80\x01\n\x0eTrexRenewLabel\x12\r\n\x05label\x18\x01 \x01(\t\x12&\n\nadd_period\x18\x02 \x01(\x0b\x32\x12.epp.common.Period\x12\x37\n\x13\x63urrent_expiry_date\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"F\n\x15MarkTrexRenewResponse\x12-\n\x08\x63md_resp\x18\x01 \x01(\x0b\x32\x1b.epp.common.CommandResponse*\x9b\x01\n\rDocumentClass\x12\t\n\x05Other\x10\x00\x12\x17\n\x13LicenseeDeclaration\x10\x01\x12\x17\n\x13\x41ssigneeDeclaration\x10\x02\x12\"\n\x1e\x44\x65\x63larationProofOfUseOneSample\x10\x03\x12\x13\n\x0fOtherProofOfUse\x10\x04\x12\x14\n\x10\x43opyOfCourtOrder\x10\x05*\x1c\n\x08\x46ileType\x12\x07\n\x03PDF\x10\x00\x12\x07\n\x03JPG\x10\x01*}\n\x0eMarkStatusType\x12\x0b\n\x07Unknown\x10\x00\x12\x07\n\x03New\x10\x01\x12\x0c\n\x08Verified\x10\x02\x12\r\n\tIncorrect\x10\x03\x12\r\n\tCorrected\x10\x04\x12\x0b\n\x07Invalid\x10\x05\x12\x0b\n\x07\x45xpired\x10\x06\x12\x0f\n\x0b\x44\x65\x61\x63tivated\x10\x07*\x8b\x01\n\x11MarkPOUStatusType\x12\r\n\tPOUNotSet\x10\x00\x12\x0c\n\x08POUValid\x10\x01\x12\x0e\n\nPOUInvalid\x10\x02\x12\x0e\n\nPOUExpired\x10\x03\x12\t\n\x05POUNA\x10\x04\x12\n\n\x06POUNew\x10\x05\x12\x10\n\x0cPOUIncorrect\x10\x06\x12\x10\n\x0cPOUCorrected\x10\x07*\xab\x01\n\nTrexStatus\x12\n\n\x06NoInfo\x10\x00\x12\x18\n\x14NotProtectedOverride\x10\x01\x12\x1a\n\x16NotProtectedRegistered\x10\x02\x12\x16\n\x12NotProtectedExempt\x10\x03\x12\x15\n\x11NotProtectedOther\x10\x04\x12\r\n\tProtected\x10\x05\x12\x0f\n\x0bUnavailable\x10\x06\x12\x0c\n\x08\x45ligible\x10\x07*7\n\x12\x43ourtDocumentClass\x12\x0e\n\nCourtOther\x10\x00\x12\x11\n\rCourtDecision\x10\x01\x42/Z-github.com/as207960/epp-proxy/gen/go/epp/tmchb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tmch.tmch_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z-github.com/as207960/epp-proxy/gen/go/epp/tmch'
  _globals['_DOCUMENTCLASS']._serialized_start=5026
  _globals['_DOCUMENTCLASS']._serialized_end=5181
  _globals['_FILETYPE']._serialized_start=5183
  _globals['_FILETYPE']._serialized_end=5211
  _globals['_MARKSTATUSTYPE']._serialized_start=5213
  _globals['_MARKSTATUSTYPE']._serialized_end=5338
  _globals['_MARKPOUSTATUSTYPE']._serialized_start=5341
  _globals['_MARKPOUSTATUSTYPE']._serialized_end=5480
  _globals['_TREXSTATUS']._serialized_start=5483
  _globals['_TREXSTATUS']._serialized_end=5654
  _globals['_COURTDOCUMENTCLASS']._serialized_start=5656
  _globals['_COURTDOCUMENTCLASS']._serialized_end=5711
  _globals['_MARKCHECKREQUEST']._serialized_start=134
  _globals['_MARKCHECKREQUEST']._serialized_end=187
  _globals['_MARKCHECKRESPONSE']._serialized_start=190
  _globals['_MARKCHECKRESPONSE']._serialized_end=321
  _globals['_BALANCEDATA']._serialized_start=323
  _globals['_BALANCEDATA']._serialized_end=392
  _globals['_MARKCREATEREQUEST']._serialized_start=395
  _globals['_MARKCREATEREQUEST']._serialized_end=602
  _globals['_DOCUMENT']._serialized_start=605
  _globals['_DOCUMENT']._serialized_end=740
  _globals['_CREATELABEL']._serialized_start=742
  _globals['_CREATELABEL']._serialized_end=816
  _globals['_MARKCREATERESPONSE']._serialized_start=819
  _globals['_MARKCREATERESPONSE']._serialized_end=988
  _globals['_MARKINFOREQUEST']._serialized_start=990
  _globals['_MARKINFOREQUEST']._serialized_end=1042
  _globals['_MARKSTATUS']._serialized_start=1044
  _globals['_MARKSTATUS']._serialized_end=1150
  _globals['_MARKPOUSTATUS']._serialized_start=1152
  _globals['_MARKPOUSTATUS']._serialized_end=1264
  _globals['_MARKINFORESPONSE']._serialized_start=1267
  _globals['_MARKINFORESPONSE']._serialized_end=1763
  _globals['_MARKLABEL']._serialized_start=1765
  _globals['_MARKLABEL']._serialized_end=1855
  _globals['_MARKLABELTREX']._serialized_start=1857
  _globals['_MARKLABELTREX']._serialized_end=1974
  _globals['_MARKLABELTREXTLD']._serialized_start=1976
  _globals['_MARKLABELTREXTLD']._serialized_end=2092
  _globals['_MARKVARIATION']._serialized_start=2094
  _globals['_MARKVARIATION']._serialized_end=2183
  _globals['_MARKSMDINFORESPONSE']._serialized_start=2186
  _globals['_MARKSMDINFORESPONSE']._serialized_end=2333
  _globals['_MARKUPDATEREQUEST']._serialized_start=2336
  _globals['_MARKUPDATEREQUEST']._serialized_end=2597
  _globals['_MARKUPDATERESPONSE']._serialized_start=2599
  _globals['_MARKUPDATERESPONSE']._serialized_end=2666
  _globals['_MARKUPDATEADD']._serialized_start=2669
  _globals['_MARKUPDATEADD']._serialized_end=2830
  _globals['_MARKUPDATEREMOVE']._serialized_start=2832
  _globals['_MARKUPDATEREMOVE']._serialized_end=2898
  _globals['_ADDCASE']._serialized_start=2901
  _globals['_ADDCASE']._serialized_end=3063
  _globals['_CASEUPDATE']._serialized_start=3066
  _globals['_CASEUPDATE']._serialized_end=3254
  _globals['_CASEADD']._serialized_start=3256
  _globals['_CASEADD']._serialized_end=3336
  _globals['_CASEREMOVE']._serialized_start=3338
  _globals['_CASEREMOVE']._serialized_end=3377
  _globals['_UDRPCASE']._serialized_start=3379
  _globals['_UDRPCASE']._serialized_end=3447
  _globals['_COURTCASE']._serialized_start=3449
  _globals['_COURTCASE']._serialized_end=3563
  _globals['_CASEDOCUMENT']._serialized_start=3566
  _globals['_CASEDOCUMENT']._serialized_end=3710
  _globals['_MARKRENEWREQUEST']._serialized_start=3713
  _globals['_MARKRENEWREQUEST']._serialized_end=3863
  _globals['_MARKRENEWRESPONSE']._serialized_start=3866
  _globals['_MARKRENEWRESPONSE']._serialized_end=4037
  _globals['_MARKTRANSFERREQUEST']._serialized_start=4039
  _globals['_MARKTRANSFERREQUEST']._serialized_end=4114
  _globals['_MARKTRANSFERRESPONSE']._serialized_start=4117
  _globals['_MARKTRANSFERRESPONSE']._serialized_end=4289
  _globals['_MARKTRANSFERINITIATEREQUEST']._serialized_start=4291
  _globals['_MARKTRANSFERINITIATEREQUEST']._serialized_end=4355
  _globals['_MARKTRANSFERINITIATERESPONSE']._serialized_start=4357
  _globals['_MARKTRANSFERINITIATERESPONSE']._serialized_end=4465
  _globals['_MARKTREXACTIVATEREQUEST']._serialized_start=4467
  _globals['_MARKTREXACTIVATEREQUEST']._serialized_end=4572
  _globals['_TREXACTIVATELABEL']._serialized_start=4574
  _globals['_TREXACTIVATELABEL']._serialized_end=4644
  _globals['_MARKTREXACTIVATERESPONSE']._serialized_start=4646
  _globals['_MARKTREXACTIVATERESPONSE']._serialized_end=4719
  _globals['_MARKTREXRENEWREQUEST']._serialized_start=4721
  _globals['_MARKTREXRENEWREQUEST']._serialized_end=4820
  _globals['_TREXRENEWLABEL']._serialized_start=4823
  _globals['_TREXRENEWLABEL']._serialized_end=4951
  _globals['_MARKTREXRENEWRESPONSE']._serialized_start=4953
  _globals['_MARKTREXRENEWRESPONSE']._serialized_end=5023
# @@protoc_insertion_point(module_scope)
