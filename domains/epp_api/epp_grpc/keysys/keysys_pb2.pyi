from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

AboriginalPeoples: CALegalType
Annually: DETrustee
Austria: EUCountry
AutoApprove: TransferMode
AutoDelete: RenewalMode
AutoDeny: TransferMode
AutoExpire: RenewalMode
AutoRenew: RenewalMode
AutoRenewMonthly: RenewalMode
AutoRenewQuarterly: RenewalMode
Belgium: EUCountry
Bulgaria: EUCountry
Bulgarian: EULanguage
Business: USPurpose
CanadianCitizen: CALegalType
CanadianCorporation: CALegalType
CanadianEducationalInstitution: CALegalType
CanadianGovernment: CALegalType
CanadianHospital: CALegalType
CanadianLibraryArchiveMuseum: CALegalType
CanadianPermanentResident: CALegalType
CanadianPoliticalParty: CALegalType
CanadianUnincorporatedAssociation: CALegalType
Croatia: EUCountry
Croatian: EULanguage
Cyprus: EUCountry
Czech: EULanguage
CzechRepublic: EUCountry
DESCRIPTOR: _descriptor.FileDescriptor
Danish: EULanguage
DefaultDelete: DomainDeleteAction
DefaultRenew: RenewalMode
DefaultTransfer: TransferMode
Denmark: EUCountry
Disable: DETrustee
DutchFlemish: EULanguage
Educational: USPurpose
English: EULanguage
Estonia: EUCountry
Estonian: EULanguage
ExpireAuction: RenewalMode
Finland: EUCountry
Finnish: EULanguage
France: EUCountry
French: EULanguage
Gaelic: EULanguage
German: EULanguage
Germany: EUCountry
Greece: EUCountry
Hungarian: EULanguage
Hungary: EUCountry
IndianBand: CALegalType
Instant: DomainDeleteAction
Ireland: EUCountry
Italian: EULanguage
Italy: EUCountry
Latvia: EUCountry
Latvian: EULanguage
LegalRepOfCanadianCitizenOrPermanentResident: CALegalType
Liechtenstein: EUCountry
Lithuania: EUCountry
Lithuanian: EULanguage
Luxembourg: EUCountry
Malta: EUCountry
Maltese: EULanguage
ModernGreek: EULanguage
Monthly: DETrustee
Netherlands: EUCountry
NonProfit: USPurpose
None: DETrustee
OfficeOrFacility: USCategory
OfficialMark: CALegalType
Partnership: CALegalType
Personal: USPurpose
Poland: EUCountry
Polish: EULanguage
Portugal: EUCountry
Portuguese: EULanguage
Push: DomainDeleteAction
RegularActivity: USCategory
Romania: EUCountry
Romanian: EULanguage
SetAutoDelete: DomainDeleteAction
SetAutoExpire: DomainDeleteAction
Slovak: EULanguage
Slovakia: EUCountry
Slovene: EULanguage
Slovenia: EUCountry
Spain: EUCountry
Spanish: EULanguage
Sweden: EUCountry
Swedish: EULanguage
TheQueen: CALegalType
TradeMark: CALegalType
TradeUnion: CALegalType
Trust: CALegalType
USCitizen: USCategory
USGovernment: USPurpose
USOrganisation: USCategory
USPermanentResident: USCategory
UnknownCALegalType: CALegalType
UnknownCategory: USCategory
UnknownCountry: EUCountry
UnknownLanguage: EULanguage
UnknownPurpose: USPurpose

class ContactCreate(_message.Message):
    __slots__ = ["check_only", "force_duplication", "pre_verify"]
    CHECK_ONLY_FIELD_NUMBER: _ClassVar[int]
    FORCE_DUPLICATION_FIELD_NUMBER: _ClassVar[int]
    PRE_VERIFY_FIELD_NUMBER: _ClassVar[int]
    check_only: bool
    force_duplication: bool
    pre_verify: bool
    def __init__(self, check_only: bool = ..., force_duplication: bool = ..., pre_verify: bool = ...) -> None: ...

class ContactInfo(_message.Message):
    __slots__ = ["validated", "verification_requested", "verified"]
    VALIDATED_FIELD_NUMBER: _ClassVar[int]
    VERIFICATION_REQUESTED_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    validated: bool
    verification_requested: bool
    verified: bool
    def __init__(self, validated: bool = ..., verification_requested: bool = ..., verified: bool = ...) -> None: ...

class ContactUpdate(_message.Message):
    __slots__ = ["check_only", "pre_verify", "trigger_foa"]
    CHECK_ONLY_FIELD_NUMBER: _ClassVar[int]
    PRE_VERIFY_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FOA_FIELD_NUMBER: _ClassVar[int]
    check_only: bool
    pre_verify: bool
    trigger_foa: bool
    def __init__(self, check_only: bool = ..., pre_verify: bool = ..., trigger_foa: bool = ...) -> None: ...

class DomainCheck(_message.Message):
    __slots__ = ["allocation_token"]
    ALLOCATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    allocation_token: str
    def __init__(self, allocation_token: _Optional[str] = ...) -> None: ...

class DomainCreate(_message.Message):
    __slots__ = ["accept_premium_price", "accept_ssl_requirements", "allocation_token", "ca", "de", "eu", "fr", "gay", "name", "renewal_mode", "rs", "transfer_mode", "us", "whois_banner", "whois_rsp", "whois_url"]
    ACCEPT_PREMIUM_PRICE_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_SSL_REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    ALLOCATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    CA_FIELD_NUMBER: _ClassVar[int]
    DE_FIELD_NUMBER: _ClassVar[int]
    EU_FIELD_NUMBER: _ClassVar[int]
    FR_FIELD_NUMBER: _ClassVar[int]
    GAY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RENEWAL_MODE_FIELD_NUMBER: _ClassVar[int]
    RS_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_MODE_FIELD_NUMBER: _ClassVar[int]
    US_FIELD_NUMBER: _ClassVar[int]
    WHOIS_BANNER_FIELD_NUMBER: _ClassVar[int]
    WHOIS_RSP_FIELD_NUMBER: _ClassVar[int]
    WHOIS_URL_FIELD_NUMBER: _ClassVar[int]
    accept_premium_price: bool
    accept_ssl_requirements: bool
    allocation_token: str
    ca: DomainInfoCA
    de: DomainInfoDE
    eu: DomainInfoEU
    fr: DomainInfoFR
    gay: DomainCreateGay
    name: DomainInfoName
    renewal_mode: RenewalMode
    rs: DomainInfoRS
    transfer_mode: TransferMode
    us: DomainInfoUS
    whois_banner: _containers.RepeatedScalarFieldContainer[str]
    whois_rsp: str
    whois_url: str
    def __init__(self, accept_premium_price: bool = ..., accept_ssl_requirements: bool = ..., allocation_token: _Optional[str] = ..., renewal_mode: _Optional[_Union[RenewalMode, str]] = ..., transfer_mode: _Optional[_Union[TransferMode, str]] = ..., whois_banner: _Optional[_Iterable[str]] = ..., whois_rsp: _Optional[str] = ..., whois_url: _Optional[str] = ..., ca: _Optional[_Union[DomainInfoCA, _Mapping]] = ..., de: _Optional[_Union[DomainInfoDE, _Mapping]] = ..., eu: _Optional[_Union[DomainInfoEU, _Mapping]] = ..., fr: _Optional[_Union[DomainInfoFR, _Mapping]] = ..., gay: _Optional[_Union[DomainCreateGay, _Mapping]] = ..., name: _Optional[_Union[DomainInfoName, _Mapping]] = ..., rs: _Optional[_Union[DomainInfoRS, _Mapping]] = ..., us: _Optional[_Union[DomainInfoUS, _Mapping]] = ...) -> None: ...

class DomainCreateGay(_message.Message):
    __slots__ = ["accept_requirements"]
    ACCEPT_REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    accept_requirements: bool
    def __init__(self, accept_requirements: bool = ...) -> None: ...

class DomainDelete(_message.Message):
    __slots__ = ["action", "target"]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    action: DomainDeleteAction
    target: str
    def __init__(self, action: _Optional[_Union[DomainDeleteAction, str]] = ..., target: _Optional[str] = ...) -> None: ...

class DomainInfo(_message.Message):
    __slots__ = ["ca", "de", "eu", "fr", "name", "paid_until_date", "renewal_date", "renewal_mode", "roid", "rs", "transfer_mode", "us", "whois_banner", "whois_rsp", "whois_url"]
    CA_FIELD_NUMBER: _ClassVar[int]
    DE_FIELD_NUMBER: _ClassVar[int]
    EU_FIELD_NUMBER: _ClassVar[int]
    FR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PAID_UNTIL_DATE_FIELD_NUMBER: _ClassVar[int]
    RENEWAL_DATE_FIELD_NUMBER: _ClassVar[int]
    RENEWAL_MODE_FIELD_NUMBER: _ClassVar[int]
    ROID_FIELD_NUMBER: _ClassVar[int]
    RS_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_MODE_FIELD_NUMBER: _ClassVar[int]
    US_FIELD_NUMBER: _ClassVar[int]
    WHOIS_BANNER_FIELD_NUMBER: _ClassVar[int]
    WHOIS_RSP_FIELD_NUMBER: _ClassVar[int]
    WHOIS_URL_FIELD_NUMBER: _ClassVar[int]
    ca: DomainInfoCA
    de: DomainInfoDE
    eu: DomainInfoEU
    fr: DomainInfoFR
    name: DomainInfoName
    paid_until_date: _timestamp_pb2.Timestamp
    renewal_date: _timestamp_pb2.Timestamp
    renewal_mode: RenewalMode
    roid: _wrappers_pb2.StringValue
    rs: DomainInfoRS
    transfer_mode: TransferMode
    us: DomainInfoUS
    whois_banner: _containers.RepeatedScalarFieldContainer[str]
    whois_rsp: _wrappers_pb2.StringValue
    whois_url: _wrappers_pb2.StringValue
    def __init__(self, renewal_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., paid_until_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., roid: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., renewal_mode: _Optional[_Union[RenewalMode, str]] = ..., transfer_mode: _Optional[_Union[TransferMode, str]] = ..., whois_banner: _Optional[_Iterable[str]] = ..., whois_rsp: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., whois_url: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., ca: _Optional[_Union[DomainInfoCA, _Mapping]] = ..., de: _Optional[_Union[DomainInfoDE, _Mapping]] = ..., eu: _Optional[_Union[DomainInfoEU, _Mapping]] = ..., fr: _Optional[_Union[DomainInfoFR, _Mapping]] = ..., name: _Optional[_Union[DomainInfoName, _Mapping]] = ..., rs: _Optional[_Union[DomainInfoRS, _Mapping]] = ..., us: _Optional[_Union[DomainInfoUS, _Mapping]] = ...) -> None: ...

class DomainInfoCA(_message.Message):
    __slots__ = ["legal_type", "trademark"]
    LEGAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRADEMARK_FIELD_NUMBER: _ClassVar[int]
    legal_type: CALegalType
    trademark: bool
    def __init__(self, legal_type: _Optional[_Union[CALegalType, str]] = ..., trademark: bool = ...) -> None: ...

class DomainInfoDE(_message.Message):
    __slots__ = ["abuse_contact", "general_contact", "holder_person", "trustee"]
    ABUSE_CONTACT_FIELD_NUMBER: _ClassVar[int]
    GENERAL_CONTACT_FIELD_NUMBER: _ClassVar[int]
    HOLDER_PERSON_FIELD_NUMBER: _ClassVar[int]
    TRUSTEE_FIELD_NUMBER: _ClassVar[int]
    abuse_contact: _wrappers_pb2.StringValue
    general_contact: _wrappers_pb2.StringValue
    holder_person: bool
    trustee: DETrustee
    def __init__(self, abuse_contact: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., general_contact: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., trustee: _Optional[_Union[DETrustee, str]] = ..., holder_person: bool = ...) -> None: ...

class DomainInfoEU(_message.Message):
    __slots__ = ["registrant_citizenship", "registrant_language", "trustee"]
    REGISTRANT_CITIZENSHIP_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    TRUSTEE_FIELD_NUMBER: _ClassVar[int]
    registrant_citizenship: EUCountry
    registrant_language: EULanguage
    trustee: bool
    def __init__(self, trustee: bool = ..., registrant_language: _Optional[_Union[EULanguage, str]] = ..., registrant_citizenship: _Optional[_Union[EUCountry, str]] = ...) -> None: ...

class DomainInfoFR(_message.Message):
    __slots__ = ["trustee"]
    TRUSTEE_FIELD_NUMBER: _ClassVar[int]
    trustee: bool
    def __init__(self, trustee: bool = ...) -> None: ...

class DomainInfoName(_message.Message):
    __slots__ = ["email_forward"]
    EMAIL_FORWARD_FIELD_NUMBER: _ClassVar[int]
    email_forward: _wrappers_pb2.StringValue
    def __init__(self, email_forward: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainInfoRS(_message.Message):
    __slots__ = ["admin_company_number", "admin_id_card", "owner_company_number", "owner_id_card", "tech_company_number", "tech_id_card"]
    ADMIN_COMPANY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ADMIN_ID_CARD_FIELD_NUMBER: _ClassVar[int]
    OWNER_COMPANY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_CARD_FIELD_NUMBER: _ClassVar[int]
    TECH_COMPANY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TECH_ID_CARD_FIELD_NUMBER: _ClassVar[int]
    admin_company_number: str
    admin_id_card: str
    owner_company_number: str
    owner_id_card: str
    tech_company_number: str
    tech_id_card: str
    def __init__(self, owner_id_card: _Optional[str] = ..., owner_company_number: _Optional[str] = ..., admin_id_card: _Optional[str] = ..., admin_company_number: _Optional[str] = ..., tech_id_card: _Optional[str] = ..., tech_company_number: _Optional[str] = ...) -> None: ...

class DomainInfoUS(_message.Message):
    __slots__ = ["category", "purpose", "validator"]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_FIELD_NUMBER: _ClassVar[int]
    category: USCategory
    purpose: USPurpose
    validator: _wrappers_pb2.StringValue
    def __init__(self, purpose: _Optional[_Union[USPurpose, str]] = ..., category: _Optional[_Union[USCategory, str]] = ..., validator: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class DomainRenew(_message.Message):
    __slots__ = ["accept_premium_price", "promotion_code"]
    ACCEPT_PREMIUM_PRICE_FIELD_NUMBER: _ClassVar[int]
    PROMOTION_CODE_FIELD_NUMBER: _ClassVar[int]
    accept_premium_price: bool
    promotion_code: str
    def __init__(self, accept_premium_price: bool = ..., promotion_code: _Optional[str] = ...) -> None: ...

class DomainTransfer(_message.Message):
    __slots__ = ["accept_premium_price", "accept_quarantine", "accept_trade", "allocation_token", "at_request_authcode", "be_request_authcode", "promotion_code"]
    ACCEPT_PREMIUM_PRICE_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_QUARANTINE_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_TRADE_FIELD_NUMBER: _ClassVar[int]
    ALLOCATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    AT_REQUEST_AUTHCODE_FIELD_NUMBER: _ClassVar[int]
    BE_REQUEST_AUTHCODE_FIELD_NUMBER: _ClassVar[int]
    PROMOTION_CODE_FIELD_NUMBER: _ClassVar[int]
    accept_premium_price: bool
    accept_quarantine: bool
    accept_trade: bool
    allocation_token: str
    at_request_authcode: bool
    be_request_authcode: bool
    promotion_code: str
    def __init__(self, accept_premium_price: bool = ..., accept_quarantine: bool = ..., accept_trade: bool = ..., allocation_token: _Optional[str] = ..., at_request_authcode: bool = ..., be_request_authcode: bool = ..., promotion_code: _Optional[str] = ...) -> None: ...

class DomainUpdate(_message.Message):
    __slots__ = ["ca", "de", "eu", "fr", "name", "renewal_mode", "rs", "transfer_mode", "us", "whois_banner", "whois_rsp", "whois_url"]
    CA_FIELD_NUMBER: _ClassVar[int]
    DE_FIELD_NUMBER: _ClassVar[int]
    EU_FIELD_NUMBER: _ClassVar[int]
    FR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RENEWAL_MODE_FIELD_NUMBER: _ClassVar[int]
    RS_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_MODE_FIELD_NUMBER: _ClassVar[int]
    US_FIELD_NUMBER: _ClassVar[int]
    WHOIS_BANNER_FIELD_NUMBER: _ClassVar[int]
    WHOIS_RSP_FIELD_NUMBER: _ClassVar[int]
    WHOIS_URL_FIELD_NUMBER: _ClassVar[int]
    ca: DomainUpdateCA
    de: DomainUpdateDE
    eu: DomainUpdateEU
    fr: DomainUpdateFR
    name: DomainInfoName
    renewal_mode: RenewalMode
    rs: DomainInfoRS
    transfer_mode: TransferMode
    us: DomainInfoUS
    whois_banner: _containers.RepeatedScalarFieldContainer[str]
    whois_rsp: _wrappers_pb2.StringValue
    whois_url: _wrappers_pb2.StringValue
    def __init__(self, renewal_mode: _Optional[_Union[RenewalMode, str]] = ..., transfer_mode: _Optional[_Union[TransferMode, str]] = ..., whois_banner: _Optional[_Iterable[str]] = ..., whois_rsp: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., whois_url: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., ca: _Optional[_Union[DomainUpdateCA, _Mapping]] = ..., de: _Optional[_Union[DomainUpdateDE, _Mapping]] = ..., eu: _Optional[_Union[DomainUpdateEU, _Mapping]] = ..., fr: _Optional[_Union[DomainUpdateFR, _Mapping]] = ..., name: _Optional[_Union[DomainInfoName, _Mapping]] = ..., rs: _Optional[_Union[DomainInfoRS, _Mapping]] = ..., us: _Optional[_Union[DomainInfoUS, _Mapping]] = ...) -> None: ...

class DomainUpdateCA(_message.Message):
    __slots__ = ["legal_type", "trademark"]
    LEGAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRADEMARK_FIELD_NUMBER: _ClassVar[int]
    legal_type: CALegalType
    trademark: _wrappers_pb2.BoolValue
    def __init__(self, legal_type: _Optional[_Union[CALegalType, str]] = ..., trademark: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class DomainUpdateDE(_message.Message):
    __slots__ = ["abuse_contact", "general_contact", "holder_person", "trustee"]
    ABUSE_CONTACT_FIELD_NUMBER: _ClassVar[int]
    GENERAL_CONTACT_FIELD_NUMBER: _ClassVar[int]
    HOLDER_PERSON_FIELD_NUMBER: _ClassVar[int]
    TRUSTEE_FIELD_NUMBER: _ClassVar[int]
    abuse_contact: _wrappers_pb2.StringValue
    general_contact: _wrappers_pb2.StringValue
    holder_person: _wrappers_pb2.BoolValue
    trustee: DETrustee
    def __init__(self, abuse_contact: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., general_contact: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., trustee: _Optional[_Union[DETrustee, str]] = ..., holder_person: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class DomainUpdateEU(_message.Message):
    __slots__ = ["registrant_citizenship", "registrant_language", "trustee"]
    REGISTRANT_CITIZENSHIP_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    TRUSTEE_FIELD_NUMBER: _ClassVar[int]
    registrant_citizenship: EUCountry
    registrant_language: EULanguage
    trustee: _wrappers_pb2.BoolValue
    def __init__(self, trustee: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., registrant_language: _Optional[_Union[EULanguage, str]] = ..., registrant_citizenship: _Optional[_Union[EUCountry, str]] = ...) -> None: ...

class DomainUpdateFR(_message.Message):
    __slots__ = ["trustee"]
    TRUSTEE_FIELD_NUMBER: _ClassVar[int]
    trustee: _wrappers_pb2.BoolValue
    def __init__(self, trustee: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class DomainDeleteAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class RenewalMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class TransferMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class CALegalType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DETrustee(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class EULanguage(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class EUCountry(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class USPurpose(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class USCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
