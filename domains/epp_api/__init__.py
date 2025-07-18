import enum
import typing
import datetime

import google.protobuf.wrappers_pb2
import grpc
import decimal
import dataclasses
import ipaddress
from google.protobuf.wrappers_pb2 import StringValue
from google.protobuf.timestamp_pb2 import Timestamp
from .epp_grpc.common import common_pb2
from .epp_grpc.contact import contact_pb2
from .epp_grpc.domain import domain_pb2
from .epp_grpc.host import host_pb2
from .epp_grpc.rgp import rgp_pb2
from .epp_grpc.fee import fee_pb2
from .epp_grpc.isnic import isnic_pb2
from .epp_grpc.domain_common import domain_common_pb2
from .epp_grpc.nominet import nominet_pb2
from .epp_grpc.nominet_ext import nominet_ext_pb2
from .epp_grpc.keysys import keysys_pb2
from .epp_grpc.eurid import eurid_pb2
from .epp_grpc import epp_pb2, epp_pb2_grpc


@dataclasses.dataclass
class IPAddress:
    address: str
    ip_type: int

    @classmethod
    def from_pb(cls, resp: common_pb2.IPAddress):
        return cls(
            address=resp.address,
            ip_type=resp.type
        )

    def to_pb(self) -> common_pb2.IPAddress:
        return common_pb2.IPAddress(
            address=self.address,
            type=self.ip_type
        )

    @property
    def address_obj(self) -> typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
        if self.ip_type == common_pb2.IPAddress.IPv4:
            return ipaddress.IPv4Address(self.address)
        elif self.ip_type == common_pb2.IPAddress.IPv6:
            return ipaddress.IPv6Address(self.address)
        else:
            raise Exception("Unknown IP address type")

    @property
    def ip_type_str(self) -> str:
        if self.ip_type == common_pb2.IPAddress.UNKNOWN:
            return "Unknown"
        elif self.ip_type == common_pb2.IPAddress.IPv4:
            return "IPv4"
        elif self.ip_type == common_pb2.IPAddress.IPv6:
            return "IPv6"

    def __str__(self):
        return self.address


@dataclasses.dataclass
class TransferStatus:
    status: int

    def __str__(self):
        if self.status == 0:
            return "Unknown status"
        elif self.status == 1:
            return "Client approved"
        elif self.status == 2:
            return "Client cancelled"
        elif self.status == 3:
            return "Client rejected"
        elif self.status == 4:
            return "Pending"
        elif self.status == 5:
            return "Server approved"
        elif self.status == 6:
            return "Server cancelled"

    def __eq__(self, other):
        if type(other) == int:
            return self.status == other
        elif type(other) == self.__class__:
            return other.status == self.status
        else:
            return False


@dataclasses.dataclass
class DomainContact:
    contact_id: str
    contact_type: str

    @classmethod
    def from_pb(cls, resp: domain_pb2.Contact):
        return cls(
            contact_id=resp.id,
            contact_type=resp.type
        )

    def to_pb(self) -> domain_pb2.Contact:
        return domain_pb2.Contact(
            id=self.contact_id,
            type=self.contact_type
        )


@dataclasses.dataclass
class DomainNameServer:
    host_obj: typing.Optional[str]
    host_name: typing.Optional[str]
    address: typing.List[IPAddress]

    def __str__(self):
        if self.host_obj:
            return self.unicode_host_obj
        else:
            return f"{self.unicode_host_name} ({', '.join(map(lambda a: str(a), self.address))})"

    @classmethod
    def from_pb(cls, resp: domain_pb2.NameServer):
        return cls(
            host_obj=resp.host_obj if resp.HasField("host_obj") else None,
            host_name=resp.host_name if resp.HasField("host_name") else None,
            address=list(map(IPAddress.from_pb, resp.addresses))
        )

    def to_pb(self) -> domain_pb2.NameServer:
        return domain_pb2.NameServer(
            host_obj=self.host_obj,
            host_name=self.host_name,
            addresses=list(map(lambda a: a.to_pb(), self.address))
        )

    @property
    def unicode_host_obj(self):
        if not self.host_obj:
            return None
        try:
            return self.host_obj.encode().decode('idna')
        except UnicodeError:
            return self.host_obj

    @property
    def unicode_host_name(self):
        if not self.host_name:
            return None
        try:
            return self.host_name.encode().decode('idna')
        except UnicodeError:
            return self.host_name


@dataclasses.dataclass
class RGPState:
    state: int

    @property
    def name(self):
        if self.state == 0:
            return "unknown"
        elif self.state == 1:
            return "add_grace_period"
        elif self.state == 2:
            return "auto_renew_grace_period"
        elif self.state == 3:
            return "renew_grace_period"
        elif self.state == 4:
            return "transfer_grace_period"
        elif self.state == 5:
            return "redemption_grace_period"
        elif self.state == 6:
            return "pending_restore_grace_period"
        elif self.state == 7:
            return "pending_delete_grace_period"

    def __str__(self):
        if self.state == 0:
            return "Unknown"
        elif self.state == 1:
            return "Add grace period"
        elif self.state == 2:
            return "Auto renew grace period"
        elif self.state == 3:
            return "Renew grace period"
        elif self.state == 4:
            return "Transfer grace period"
        elif self.state == 5:
            return "Redemption grace period"
        elif self.state == 6:
            return "Pending restore grace period"
        elif self.state == 7:
            return "Pending delete grace period"

    def __eq__(self, other):
        if type(other) == int:
            return self.state == other
        elif type(other) == self.__class__:
            return other.status == self.state
        else:
            return False

    def __bool__(self):
        return self.state != 0


@dataclasses.dataclass
class DomainStatus:
    status: int

    @property
    def name(self):
        if self.status == 0:
            return "client_delete_prohibited"
        elif self.status == 1:
            return "client_hold"
        elif self.status == 2:
            return "client_renew_prohibited"
        elif self.status == 3:
            return "client_transfer_prohibited"
        elif self.status == 4:
            return "client_update_prohibited"
        elif self.status == 5:
            return "inactive"
        elif self.status == 6:
            return "ok"
        elif self.status == 7:
            return "pending_create"
        elif self.status == 8:
            return "pending_delete"
        elif self.status == 9:
            return "pending_transfer"
        elif self.status == 10:
            return "pending_transfer"
        elif self.status == 11:
            return "pending_update"
        elif self.status == 12:
            return "server_delete_prohibited"
        elif self.status == 13:
            return "server_hold"
        elif self.status == 14:
            return "server_renew_prohibited"
        elif self.status == 15:
            return "server_transfer_prohibited"
        elif self.status == 16:
            return "server_update_prohibited"

    def __str__(self):
        if self.status == 0:
            return "Client delete prohibited"
        elif self.status == 1:
            return "Client hold"
        elif self.status == 2:
            return "Client renew prohibited"
        elif self.status == 3:
            return "Client transfer prohibited"
        elif self.status == 4:
            return "Client update prohibited"
        elif self.status == 5:
            return "Inactive"
        elif self.status == 6:
            return "OK"
        elif self.status == 7:
            return "Pending create"
        elif self.status == 8:
            return "Pending delete"
        elif self.status == 9:
            return "Pending renew"
        elif self.status == 10:
            return "Pending transfer"
        elif self.status == 11:
            return "Pending update"
        elif self.status == 12:
            return "Server delete prohibited"
        elif self.status == 13:
            return "Server hold"
        elif self.status == 14:
            return "Server renew prohibited"
        elif self.status == 15:
            return "Server transfer prohibited"
        elif self.status == 16:
            return "Server update prohibited"

    def __eq__(self, other):
        if type(other) == int:
            return self.status == other
        elif type(other) == self.__class__:
            return other.status == self.status
        else:
            return False


@dataclasses.dataclass
class SecDNSKeyData:
    flags: int
    protocol: int
    algorithm: int
    public_key: str

    @classmethod
    def from_pb(cls, resp: domain_pb2.SecDNSKeyDatum):
        return cls(
            flags=resp.flags,
            protocol=resp.protocol,
            algorithm=resp.algorithm,
            public_key=resp.public_key
        )

    def to_pb(self):
        return domain_pb2.SecDNSKeyDatum(
            flags=self.flags,
            protocol=self.protocol,
            algorithm=self.algorithm,
            public_key=self.public_key
        )


@dataclasses.dataclass
class SecDNSDSData:
    key_tag: int
    algorithm: int
    digest_type: int
    digest: str
    key_data: typing.Optional[SecDNSKeyData]

    @classmethod
    def from_pb(cls, resp: domain_pb2.SecDNSDSDatum):
        return cls(
            key_tag=resp.key_tag,
            algorithm=resp.algorithm,
            digest_type=resp.digest_type,
            digest=resp.digest,
            key_data=SecDNSKeyData.from_pb(resp.key_data) if resp.HasField("key_data") else None
        )
    
    def to_pb(self):
        return domain_pb2.SecDNSDSDatum(
            key_tag=self.key_tag,
            algorithm=self.algorithm,
            digest_type=self.digest_type,
            digest=self.digest,
            key_data=self.key_data.to_pb() if self.key_data else None
        )


@dataclasses.dataclass
class SecDNSData:
    max_sig_life: typing.Optional[datetime.timedelta]
    ds_data: typing.Optional[typing.List[SecDNSDSData]]
    key_data: typing.Optional[typing.List[SecDNSKeyData]]

    @classmethod
    def from_pb(cls, resp: domain_pb2.SecDNSData):
        return cls(
            max_sig_life=datetime.timedelta(seconds=resp.max_sig_life.value) if resp.HasField("max_sig_life") else None,
            ds_data=list(map(SecDNSDSData.from_pb, resp.ds_data.data)) if resp.HasField("ds_data") else None,
            key_data=list(map(SecDNSKeyData.from_pb, resp.key_data.data)) if resp.HasField("key_data") else None,
        )


@dataclasses.dataclass
class DomainEURIDInfo:
    on_hold: bool
    quarantined: bool
    suspended: bool
    delayed: bool
    seized: bool
    on_site: typing.Optional[str]
    reseller: typing.Optional[str]

    @classmethod
    def from_pb(cls, resp: eurid_pb2.DomainInfo):
        return cls(
            on_hold=resp.on_hold,
            quarantined=resp.quarantined,
            suspended=resp.suspended,
            delayed=resp.delayed,
            seized=resp.seized,
            on_site=resp.on_site,
            reseller=resp.reseller,
        )


@dataclasses.dataclass
class DomainNominetInfo:
    renewal_not_required: bool
    notes: typing.List[str]
    reseller: typing.Optional[str]

    @classmethod
    def from_pb(cls, resp: nominet_ext_pb2.DomainInfo):
        return cls(
            renewal_not_required=resp.renewal_not_required,
            notes=resp.notes,
            reseller=resp.reseller,
        )


class Domain:
    _app = None  # type: EPPClient
    name: str
    registry_id: str
    statuses: typing.List[DomainStatus]
    registrant: str
    contacts: typing.List[DomainContact]
    name_servers: typing.List[DomainNameServer]
    hosts: typing.List[str]
    client_id: str
    client_created_id: typing.Optional[str]
    creation_date: typing.Optional[datetime.datetime]
    expiry_date: typing.Optional[datetime.datetime]
    renewal_date: typing.Optional[datetime.datetime]
    paid_until_date: typing.Optional[datetime.datetime]
    last_updated_client: typing.Optional[str]
    last_updated_date: typing.Optional[datetime.datetime]
    last_transfer_date: typing.Optional[datetime.datetime]
    rgp_state: typing.List[RGPState]
    auth_info: typing.Optional[str]
    sec_dns: typing.Optional[SecDNSData]
    eurid: typing.Optional[DomainEURIDInfo]
    nominet: typing.Optional[DomainNominetInfo]
    registry_name: str

    @classmethod
    def from_pb(cls, resp: domain_pb2.DomainInfoReply, app):
        self = cls()
        self._app = app
        self.name = resp.name
        self.registry_id = (
            resp.keysys.roid.value if resp.keysys.HasField("roid") else resp.registry_id
        ) if resp.HasField("keysys") else resp.registry_id
        self.statuses = list(map(lambda s: DomainStatus(status=s), resp.statuses))
        self.registrant = resp.registrant
        self.contacts = list(map(DomainContact.from_pb, resp.contacts))
        self.name_servers = list(map(DomainNameServer.from_pb, resp.nameservers))
        self.hosts = resp.hosts
        self.client_id = resp.client_id
        self.client_created_id = resp.client_created_id.value if resp.HasField("client_created_id") else None
        self.creation_date = resp.creation_date.ToDatetime() if resp.HasField("creation_date") else None
        self.expiry_date = resp.expiry_date.ToDatetime() if resp.HasField("expiry_date") else None
        self.renewal_date = (
            resp.keysys.renewal_date.ToDatetime() if resp.keysys.HasField("renewal_date") else None
        ) if resp.HasField("keysys") else None
        self.paid_until_date = (
            resp.keysys.paid_until_date.ToDatetime() if resp.keysys.HasField("paid_until_date") else None
        ) if resp.HasField("keysys") else None
        self.last_updated_client = resp.last_updated_client.value if resp.HasField("last_updated_client") else None
        self.last_updated_date = resp.last_updated_date.ToDatetime() if resp.HasField("last_updated_date") else None
        self.last_transfer_date = resp.last_transfer_date.ToDatetime() if resp.HasField("last_transfer_date") else None
        self.rgp_state = list(map(lambda s: RGPState(state=s), resp.rgp_state))
        self.auth_info = resp.auth_info.value if resp.HasField("auth_info") else None
        self.sec_dns = SecDNSData.from_pb(resp.sec_dns) if resp.HasField("sec_dns") else None
        self.eurid = DomainEURIDInfo.from_pb(resp.eurid_data) if resp.HasField("eurid_data") else None
        self.nominet = DomainNominetInfo.from_pb(resp.nominet_ext) if resp.HasField("nominet_ext") else None
        self.registry_name = resp.registry_name
        return self

    @property
    def expired(self):
        return self.expiry_date <= datetime.datetime.now() if self.expiry_date else False

    @property
    def admin(self):
        return self.get_contact("admin")

    @property
    def billing(self):
        return self.get_contact("billing")

    @property
    def tech(self):
        return self.get_contact("tech")

    @property
    def unicode_domain(self):
        try:
            return self.name.encode().decode('idna')
        except UnicodeError:
            return self.name

    @property
    def can_update(self):
        return int(domain_common_pb2.ClientUpdateProhibited) not in self.statuses \
               and int(domain_common_pb2.ServerUpdateProhibited) not in self.statuses

    @property
    def can_renew(self):
        return int(domain_common_pb2.ClientRenewProhibited) not in self.statuses \
               and int(domain_common_pb2.ServerRenewProhibited) not in self.statuses

    @property
    def can_delete(self):
        return int(domain_common_pb2.ClientDeleteProhibited) not in self.statuses \
               and int(domain_common_pb2.ServerDeleteProhibited) not in self.statuses

    def set_auth_info(self, auth_info: str) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            new_auth_info=StringValue(value=auth_info)
        )).pending

    def get_contact(self, contact_type: str):
        return next(filter(lambda c: c.contact_type == contact_type, self.contacts), None)

    def set_contact(self, contact_type: str, contact_id: typing.Union[str, None]) -> bool:
        old_contact = next(filter(lambda c: c.contact_type == contact_type, self.contacts), None)

        rem = []
        add = []
        if old_contact:
            if old_contact.contact_id == contact_id:
                return False
            rem.append(domain_pb2.DomainUpdateRequest.Param(
                    contact=domain_pb2.Contact(
                        type=contact_type,
                        id=old_contact.contact_id
                    )
                ))
        if contact_id:
            add.append(domain_pb2.DomainUpdateRequest.Param(
                contact=domain_pb2.Contact(
                    type=contact_type,
                    id=contact_id
                )
            ))

        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            remove=rem,
            add=add,
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def set_registrant(self, contact_id: str) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            new_registrant=StringValue(value=contact_id),
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def set_admin(self, contact_id: typing.Union[str, None]) -> bool:
        return self.set_contact("admin", contact_id)

    def set_billing(self, contact_id: typing.Union[str, None]) -> bool:
        return self.set_contact("billing", contact_id)

    def set_tech(self, contact_id: typing.Union[str, None]) -> bool:
        return self.set_contact("tech", contact_id)

    def add_host_objs(self, hosts: typing.List[str], replace: bool = False) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            remove=[],
            add=list(map(lambda h: domain_pb2.DomainUpdateRequest.Param(
                nameserver=domain_pb2.NameServer(
                    host_obj=h
                )
            ), hosts)),
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def del_host_objs(self, hosts: typing.List[str], with_dnssec: bool = False) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            add=[],
            remove=list(map(lambda h: domain_pb2.DomainUpdateRequest.Param(
                nameserver=domain_pb2.NameServer(
                    host_obj=h
                )
            ), hosts)),
            sec_dns=domain_pb2.UpdateSecDNSData(
                all=True
            ) if with_dnssec else None,
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def add_host_addrs(self, hosts: typing.List[typing.Tuple[str, typing.List[IPAddress]]]) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            remove=[],
            add=list(map(lambda h: domain_pb2.DomainUpdateRequest.Param(
                nameserver=domain_pb2.NameServer(
                    host_name=h[0],
                    addresses=list(map(lambda a: a.to_pb(), h[1]))
                )
            ), hosts)),
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def del_host_name(self, hosts: typing.List[str], with_dnssec: bool = False) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            add=[],
            remove=list(map(lambda h: domain_pb2.DomainUpdateRequest.Param(
                nameserver=domain_pb2.NameServer(
                    host_name=h
                )
            ), hosts)),
            sec_dns=domain_pb2.UpdateSecDNSData(
                all=True
            ) if with_dnssec else None,
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def add_ds_data(self, data: typing.List[SecDNSDSData]) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            sec_dns=domain_pb2.UpdateSecDNSData(
                add_ds_data=domain_pb2.SecDNSDSData(data=list(map(lambda d: d.to_pb(), data)))
            ),
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def add_dnskey_data(self, data: typing.List[SecDNSKeyData]) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            sec_dns=domain_pb2.UpdateSecDNSData(
                add_key_data=domain_pb2.SecDNSKeyData(data=list(map(lambda d: d.to_pb(), data)))
            ),
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def del_secdns_all(self) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            sec_dns=domain_pb2.UpdateSecDNSData(
                all=True
            ),
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def del_ds_data(self, data: typing.List[SecDNSDSData]) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            sec_dns=domain_pb2.UpdateSecDNSData(
                rem_ds_data=domain_pb2.SecDNSDSData(data=list(map(lambda d: d.to_pb(), data)))
            ),
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def del_dnskey_data(self, data: typing.List[SecDNSKeyData]) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            sec_dns=domain_pb2.UpdateSecDNSData(
                rem_key_data=domain_pb2.SecDNSKeyData(data=list(map(lambda d: d.to_pb(), data)))
            ),
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def add_states(self, data: typing.List[DomainStatus]) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            add=list(map(lambda s: domain_pb2.DomainUpdateRequest.Param(
                state=s.status
            ), data)),
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending

    def del_states(self, data: typing.List[DomainStatus]) -> bool:
        return self._app.stub.DomainUpdate(domain_pb2.DomainUpdateRequest(
            name=self.name,
            remove=list(map(lambda s: domain_pb2.DomainUpdateRequest.Param(
                state=s.status
            ), data)),
            registry_name=google.protobuf.wrappers_pb2.StringValue(value=self.registry_name)
        )).pending


@dataclasses.dataclass
class Period:
    unit: int
    value: int

    @classmethod
    def from_pb(cls, resp: common_pb2.Period):
        return cls(
            unit=resp.unit,
            value=resp.value
        )

    def to_pb(self) -> common_pb2.Period:
        return common_pb2.Period(
            unit=self.unit,
            value=self.value
        )

    def __str__(self):
        if self.unit == common_pb2.Period.Years:
            if self.value == 1:
                unit = "year"
            else:
                unit = "years"
        elif self.unit == common_pb2.Period.Months:
            if self.value == 1:
                unit = "month"
            else:
                unit = "months"
        else:
            unit = f"unknown unit ({self.unit})"
        return f"{self.value} {unit}"


@dataclasses.dataclass
class DomainTransfer:
    pending: bool
    status: TransferStatus
    requested_client_id: str
    requested_date: datetime.datetime
    act_client_id: str
    act_date: datetime.datetime
    expiry_date: typing.Optional[datetime.datetime]
    registry_name: str

    @classmethod
    def from_pb(cls, resp: domain_pb2.DomainTransferReply):
        return cls(
            pending=resp.pending,
            status=TransferStatus(status=resp.status),
            requested_client_id=resp.requested_client_id,
            requested_date=resp.requested_date.ToDatetime(),
            act_client_id=resp.act_client_id,
            act_date=resp.act_date.ToDatetime(),
            expiry_date=resp.expiry_date.ToDatetime() if resp.HasField("expiry_date") else None,
            registry_name=resp.registry_name
        )


@dataclasses.dataclass
class HostStatus:
    status: int

    @property
    def name(self):
        if self.status == 0:
            return "client_delete_prohibited"
        elif self.status == 1:
            return "client_update_prohibited"
        elif self.status == 2:
            return "linked"
        elif self.status == 3:
            return "ok"
        elif self.status == 4:
            return "pending_create"
        elif self.status == 5:
            return "pending_delete"
        elif self.status == 6:
            return "pending_transfer"
        elif self.status == 7:
            return "pending_update"
        elif self.status == 8:
            return "server_delete_prohibited"
        elif self.status == 9:
            return "server_update_prohibited"

    def __str__(self):
        if self.status == 0:
            return "Client delete prohibited"
        elif self.status == 1:
            return "Client update prohibited"
        elif self.status == 2:
            return "Linked"
        elif self.status == 3:
            return "OK"
        elif self.status == 4:
            return "Pending create"
        elif self.status == 5:
            return "Pending delete"
        elif self.status == 6:
            return "Pending transfer"
        elif self.status == 7:
            return "Pending update"
        elif self.status == 8:
            return "Server delete prohibited"
        elif self.status == 9:
            return "Server update prohibited"

    def __eq__(self, other):
        if type(other) == int:
            return self.status == other
        elif type(other) == self.__class__:
            return other.status == self.status
        else:
            return False


class Host:
    _app = None  # type: EPPClient
    name: str
    registry_id: str
    statuses: typing.List[HostStatus]
    addresses: typing.List[IPAddress]
    client_id: str
    client_created_id: typing.Optional[str]
    creation_date: typing.Optional[datetime.datetime]
    last_updated_client: typing.Optional[str]
    last_updated_date: typing.Optional[datetime.datetime]
    last_transfer_date: typing.Optional[datetime.datetime]
    registry_name: str

    @classmethod
    def from_pb(cls, resp: host_pb2.HostInfoReply, app, registry_name):
        self = cls()
        self._app = app
        self.name = resp.name
        self.registry_id = resp.registry_id
        self.statuses = list(map(lambda s: HostStatus(status=s), resp.statuses))
        self.addresses = list(map(IPAddress.from_pb, resp.addresses))
        self.client_id = resp.client_id
        self.client_created_id = resp.client_created_id.value if resp.HasField("client_created_id") else None
        self.creation_date = resp.creation_date.ToDatetime() if resp.HasField("creation_date") else None
        self.last_updated_client = resp.last_updated_client.value if resp.HasField("last_updated_client") else None
        self.last_updated_date = resp.last_updated_date.ToDatetime() if resp.HasField("last_updated_date") else None
        self.last_transfer_date = resp.last_transfer_date.ToDatetime() if resp.HasField("last_transfer_date") else None
        self.registry_name = registry_name
        return self

    @property
    def unicode_name(self):
        try:
            return self.name.encode().decode('idna')
        except UnicodeError:
            return self.name

    def set_addresses(self, addresses: typing.List[IPAddress]) -> bool:
        rem_addrs = list(filter(lambda a: a not in addresses, self.addresses))
        add_addrs = list(filter(lambda a: a not in self.addresses, addresses))

        if not rem_addrs and not add_addrs:
            return False

        resp = self._app.stub.HostUpdate(host_pb2.HostUpdateRequest(
            name=self.name,
            add=list(map(lambda a: host_pb2.HostUpdateRequest.Param(
                address=a.to_pb()
            ), add_addrs)),
            remove=list(map(lambda a: host_pb2.HostUpdateRequest.Param(
                address=a.to_pb()
            ), rem_addrs)),
            new_name=None,
            registry_name=self.registry_name
        ))
        return resp.pending

    def add_addresses(self, addresses: typing.List[IPAddress]) -> bool:
        resp = self._app.stub.HostUpdate(host_pb2.HostUpdateRequest(
            name=self.name,
            add=list(map(lambda a: host_pb2.HostUpdateRequest.Param(
                address=a.to_pb()
            ), addresses)),
            remove=[],
            new_name=None,
            registry_name=self.registry_name
        ))
        return resp.pending

    def remove_addresses(self, addresses: typing.List[IPAddress]) -> bool:
        resp = self._app.stub.HostUpdate(host_pb2.HostUpdateRequest(
            name=self.name,
            remove=list(map(lambda a: host_pb2.HostUpdateRequest.Param(
                address=a.to_pb()
            ), addresses)),
            add=[],
            new_name=None,
            registry_name=self.registry_name
        ))
        return resp.pending

    def set_isnic_zone_contact(self, contact_id: str) -> bool:
        resp = self._app.stub.HostUpdate(host_pb2.HostUpdateRequest(
            name=self.name,
            remove=[],
            add=[],
            new_name=None,
            isnic_info=isnic_pb2.HostInfo(
                zone_contact=google.protobuf.wrappers_pb2.StringValue(value=contact_id)
            ),
            registry_name=self.registry_name
        ))
        return resp.pending


@dataclasses.dataclass
class Address:
    name: str
    organisation: typing.Optional[str]
    streets: typing.List[str]
    city: str
    province: typing.Optional[str]
    postal_code: typing.Optional[str]
    country_code: str
    identity_number: typing.Optional[str]
    birth_date: typing.Optional[datetime.date]

    @classmethod
    def from_pb(cls, resp: contact_pb2.PostalAddress):
        return cls(
            name=resp.name,
            organisation=resp.organisation.value if resp.HasField("organisation") else None,
            streets=resp.streets,
            city=resp.city,
            province=resp.province.value if resp.HasField("province") else None,
            postal_code=resp.postal_code.value if resp.HasField("postal_code") else None,
            country_code=resp.country_code,
            identity_number=resp.identity_number.value if resp.HasField("identity_number") else None,
            birth_date=resp.birth_date.ToDatetime().date() if resp.HasField("birth_date") else None
        )

    def to_pb(self) -> contact_pb2.PostalAddress:
        if self.birth_date:
            birth_date = Timestamp()
            birth_date.FromDatetime(datetime.datetime.combine(self.birth_date, datetime.datetime.min.time()))
        else:
            birth_date = None
        return contact_pb2.PostalAddress(
            name=self.name,
            organisation=StringValue(value=self.organisation) if self.organisation else None,
            streets=self.streets,
            city=self.city,
            province=StringValue(value=self.province) if self.province else None,
            postal_code=StringValue(value=self.postal_code) if self.postal_code else None,
            country_code=self.country_code,
            identity_number=StringValue(value=self.identity_number) if self.identity_number else None,
            birth_date=birth_date
        )


@dataclasses.dataclass
class Phone:
    number: str
    ext: typing.Optional[str]

    @classmethod
    def from_pb(cls, resp: common_pb2.Phone):
        return cls(
            number=resp.number,
            ext=resp.extension.value if resp.HasField("extension") else None
        )

    def to_pb(self) -> common_pb2.Phone:
        return common_pb2.Phone(
            number=self.number,
            extension=StringValue(value=self.ext) if self.ext else None
        )


@dataclasses.dataclass
class ContactStatus:
    status: int

    @property
    def name(self):
        if self.status == 0:
            return "client_delete_prohibited"
        elif self.status == 1:
            return "client_transfer_prohibited"
        elif self.status == 2:
            return "client_update_prohibited"
        elif self.status == 3:
            return "linked"
        elif self.status == 4:
            return "ok"
        elif self.status == 5:
            return "pending_create"
        elif self.status == 6:
            return "pending_delete"
        elif self.status == 7:
            return "pending_transfer"
        elif self.status == 8:
            return "pending_update"
        elif self.status == 9:
            return "server_delete_prohibited"
        elif self.status == 10:
            return "server_transfer_prohibited"
        elif self.status == 11:
            return "server_update_prohibited"

    def __str__(self):
        if self.status == 0:
            return "Client delete prohibited"
        elif self.status == 1:
            return "Client transfer prohibited"
        elif self.status == 2:
            return "Client update prohibited"
        elif self.status == 3:
            return "Linked"
        elif self.status == 4:
            return "OK"
        elif self.status == 5:
            return "Pending create"
        elif self.status == 6:
            return "Pending delete"
        elif self.status == 7:
            return "Pending transfer"
        elif self.status == 8:
            return "Pending update"
        elif self.status == 9:
            return "Server delete prohibited"
        elif self.status == 10:
            return "Server transfer prohibited"
        elif self.status == 11:
            return "Server update prohibited"

    def __eq__(self, other):
        if type(other) == int:
            return self.status == other
        elif type(other) == self.__class__:
            return other.status == self.status
        else:
            return False


@dataclasses.dataclass
class DisclosureItem:
    item: int

    @property
    def name(self):
        if self.item == 0:
            return "local_name"
        elif self.item == 1:
            return "internationalised_name"
        elif self.item == 2:
            return "local_organisation"
        elif self.item == 3:
            return "internationalised_organisation"
        elif self.item == 4:
            return "local_address"
        elif self.item == 5:
            return "internationalised_address"
        elif self.item == 6:
            return "voice"
        elif self.item == 7:
            return "fax"
        elif self.item == 8:
            return "email"

    def __str__(self):
        if self.item == 0:
            return "Local name"
        elif self.item == 1:
            return "Internationalised name"
        elif self.item == 2:
            return "Local organisation"
        elif self.item == 3:
            return "Internationalised organisation"
        elif self.item == 4:
            return "Local address"
        elif self.item == 5:
            return "Internationalised address"
        elif self.item == 6:
            return "Voice"
        elif self.item == 7:
            return "Fax"
        elif self.item == 8:
            return "Email"

    def __eq__(self, other):
        if type(other) == int:
            return self.item == other
        elif type(other) == self.__class__:
            return other.status == self.item
        else:
            return False


@dataclasses.dataclass
class Disclosure:
    items: typing.List[DisclosureItem]

    @classmethod
    def from_pb(cls, resp: typing.Iterable[int]):
        return cls(
            items=list(map(lambda i: DisclosureItem(item=i), resp))
        )

    def to_pb(self) -> contact_pb2.Disclosure:
        return contact_pb2.Disclosure(
            disclosure=list(map(lambda i: i.item, self.items))
        )


@dataclasses.dataclass
class ISNICContactStatus:
    status: int

    @property
    def name(self):
        if self.status == isnic_pb2.ContactStatus.Ok:
            return "ok"
        elif self.status == isnic_pb2.ContactStatus.OkUnconfirmed:
            return "ok_unconfirmed"
        elif self.status == isnic_pb2.ContactStatus.PendingCreate:
            return "pending_create"
        elif self.status == isnic_pb2.ContactStatus.ServerExpired:
            return "server_expired"
        elif self.status == isnic_pb2.ContactStatus.ServerSuspended:
            return "server_suspended"

    def __str__(self):
        if self.status == isnic_pb2.ContactStatus.Ok:
            return "OK"
        elif self.status == isnic_pb2.ContactStatus.OkUnconfirmed:
            return "OK (unconfirmed)"
        elif self.status == isnic_pb2.ContactStatus.PendingCreate:
            return "Pending create"
        elif self.status == isnic_pb2.ContactStatus.ServerExpired:
            return "Server expired"
        elif self.status == isnic_pb2.ContactStatus.ServerSuspended:
            return "Server suspended"

    def __eq__(self, other):
        if type(other) == int:
            return self.status == other
        elif type(other) == self.__class__:
            return other.status == self.status
        else:
            return False


@dataclasses.dataclass
class ISNICContactInfo:
    statuses: typing.List[ISNICContactStatus]
    mobile: typing.Optional[Phone]
    sid: typing.Optional[str]
    auto_update_from_national_registry: bool
    paper_invoices: bool

    @classmethod
    def from_pb(cls, resp: isnic_pb2.ContactInfo):
        return cls(
            statuses=list(map(lambda s: ISNICContactStatus(status=s), resp.statuses)),
            mobile=Phone.from_pb(resp.mobile) if resp.HasField("mobile") else None,
            sid=resp.sid.value if resp.HasField("sid") else None,
            auto_update_from_national_registry=resp.auto_update_from_national_registry,
            paper_invoices=resp.paper_invoices
        )


class ContactRole(enum.Enum):
    Registrant = "registrant"
    Admin = "admin"
    Billing = "billing"
    Tech = "tech"
    OnSite = "on-site"
    Reseller = "reseller"

    @classmethod
    def from_eurid_pb(cls, resp: eurid_pb2.ContactType):
        if resp == eurid_pb2.ContactType.Registrant:
            return cls.Registrant
        elif resp == eurid_pb2.ContactType.Billing:
            return cls.Billing
        elif resp == eurid_pb2.ContactType.Tech:
            return cls.Tech
        elif resp == eurid_pb2.ContactType.OnSite:
            return cls.OnSite
        elif resp == eurid_pb2.ContactType.Reseller:
            return cls.Reseller

    def to_eurid_pb(self) -> eurid_pb2.ContactType:
        if self == self.Registrant:
            return eurid_pb2.ContactType.Registrant
        elif self == self.Admin:
            raise ValueError("Admin contact is not supported by EURid")
        elif self == self.Billing:
            return eurid_pb2.ContactType.Billing
        elif self == self.Tech:
            return eurid_pb2.ContactType.Tech
        elif self == self.OnSite:
            return eurid_pb2.ContactType.OnSite
        elif self == self.Reseller:
            return eurid_pb2.ContactType.Reseller


@dataclasses.dataclass
class EURIDContact:
    contact_type: ContactRole
    whois_email: typing.Optional[str]
    vat_number: typing.Optional[str]
    language: str
    country_of_citizenship: typing.Optional[str]

    @classmethod
    def from_pb(cls, resp: eurid_pb2.ContactExtension):
        return cls(
            contact_type=ContactRole.from_eurid_pb(resp.contact_type),
            whois_email=resp.whois_email.value if resp.HasField("whois_email") else None,
            language=resp.language,
            country_of_citizenship=resp.citizenship_country.value if resp.HasField("citizenship_country") else None,
            vat_number=resp.vat.value if resp.HasField("vat") else None,
        )

    def to_pb(self) -> eurid_pb2.ContactExtension:
        return eurid_pb2.ContactExtension(
            contact_type=self.contact_type.to_eurid_pb(),
            whois_email=google.protobuf.wrappers_pb2.StringValue(
                value=self.whois_email
            ) if self.whois_email else None,
            language=self.language,
            citizenship_country=google.protobuf.wrappers_pb2.StringValue(
                value=self.country_of_citizenship
            ) if self.country_of_citizenship else None,
            vat=google.protobuf.wrappers_pb2.StringValue(
                value=self.vat_number
            ) if self.vat_number else None,
        )


@dataclasses.dataclass
class EURIDContactUpdate:
    whois_email: typing.Optional[str]
    vat_number: typing.Optional[str]
    language: typing.Optional[str]
    country_of_citizenship: typing.Optional[str]

    def to_pb(self) -> eurid_pb2.ContactUpdateExtension:
        return eurid_pb2.ContactUpdateExtension(
            new_whois_email=google.protobuf.wrappers_pb2.StringValue(
                value=self.whois_email
            ) if self.whois_email else None,
            new_language=google.protobuf.wrappers_pb2.StringValue(
                value=self.language,
            ) if self.language else None,
            new_citizenship_country=google.protobuf.wrappers_pb2.StringValue(
                value=self.country_of_citizenship
            ) if self.country_of_citizenship else None,
            new_vat=google.protobuf.wrappers_pb2.StringValue(
                value=self.vat_number
            ) if self.vat_number else None,
        )


class Contact:
    _app = None  # type: EPPClient
    id: str
    registry_id: str
    statuses: typing.List[ContactStatus]
    local_address: Address
    int_address: typing.Optional[Address]
    phone: typing.Optional[Phone]
    fax: typing.Optional[Phone]
    email: str
    entity_type: int
    trading_name: typing.Optional[str]
    company_number: typing.Optional[str]
    client_id: str
    client_created_id: typing.Optional[str]
    creation_date: typing.Optional[datetime.datetime]
    last_updated_client: typing.Optional[str]
    last_updated_date: typing.Optional[datetime.datetime]
    last_transfer_date: typing.Optional[datetime.datetime]
    auth_info: typing.Optional[str]
    disclosure: typing.Optional[Disclosure]
    isnic_info: typing.Optional[ISNICContactInfo]
    eurid: typing.Optional[EURIDContact]
    registry_name: str

    @classmethod
    def from_pb(cls, resp: contact_pb2.ContactInfoReply, app, registry_name):
        self = cls()
        self._app = app
        self.id = resp.id
        self.registry_id = resp.registry_id
        self.statuses = list(map(lambda s: ContactStatus(status=s), resp.statuses))
        self.local_address = Address.from_pb(resp.local_address) if resp.HasField("local_address") else None
        self.int_address = Address.from_pb(resp.internationalised_address) if\
            resp.HasField("internationalised_address") else None
        self.phone = Phone.from_pb(resp.phone) if resp.HasField("phone") else None
        self.fax = Phone.from_pb(resp.fax) if resp.HasField("fax") else None
        self.email = resp.email
        self.entity_type = resp.entity_type
        self.trading_name = resp.trading_name.value if resp.HasField("trading_name") else None
        self.company_number = resp.company_number.value if resp.HasField("company_number") else None
        self.client_id = resp.client_id
        self.client_created_id = resp.client_created_id.value if resp.HasField("client_created_id") else None
        self.creation_date = resp.creation_date.ToDatetime() if resp.HasField("creation_date") else None
        self.last_updated_date = resp.last_updated_date.ToDatetime() if resp.HasField("last_updated_date") else None
        self.last_transfer_date = resp.last_transfer_date.ToDatetime() if resp.HasField("last_transfer_date") else None
        self.auth_info = resp.auth_info.value if resp.HasField("auth_info") else None
        self.disclosure = Disclosure.from_pb(resp.disclosure)
        self.isnic_info = ISNICContactInfo.from_pb(resp.isnic_info) if resp.HasField("isnic_info") else None
        self.eurid = EURIDContact.from_pb(resp.eurid_info) if resp.HasField("eurid_info") else None
        self.registry_name = registry_name
        return self

    def update(
            self,
            local_address: typing.Optional[Address] = None,
            int_address: typing.Optional[Address] = None,
            phone: typing.Optional[Phone] = None,
            fax: typing.Optional[Phone] = None,
            email: typing.Optional[str] = None,
            entity_type: typing.Optional[int] = None,
            trading_name: typing.Optional[str] = None,
            company_number: typing.Optional[str] = None,
            auth_info: typing.Optional[str] = None,
            disclosure: typing.Optional[Disclosure] = None,
            eurid: typing.Optional[EURIDContactUpdate] = None,
    ) -> bool:
        resp = self._app.stub.ContactUpdate(contact_pb2.ContactUpdateRequest(
            id=self.id,
            new_local_address=local_address.to_pb() if local_address else None,
            new_internationalised_address=int_address.to_pb() if int_address else None,
            new_phone=phone.to_pb() if phone else None,
            new_fax=fax.to_pb() if fax else None,
            new_email=StringValue(value=email) if email and email != self.email else None,
            new_entity_type=entity_type if entity_type and entity_type != self.entity_type else None,
            new_trading_name=StringValue(value=trading_name)
            if trading_name and trading_name != self.trading_name else None,
            new_company_number=StringValue(value=company_number)
            if company_number and company_number != self.company_number else None,
            new_auth_info=StringValue(value=auth_info) if auth_info and auth_info != self.auth_info else None,
            disclosure=disclosure.to_pb() if disclosure else None,
            new_eurid_info=eurid.to_pb() if eurid else None,
            registry_name=self.registry_name
        ))
        return resp.pending


@dataclasses.dataclass
class Fee:
    value: decimal.Decimal
    description: typing.Optional[str]
    refundable: typing.Optional[bool]
    grace_period: typing.Optional[str]

    @classmethod
    def from_pb(cls, resp: fee_pb2.Fee):
        return cls(
            value=decimal.Decimal(resp.value),
            description=resp.description.value if resp.HasField("description") else None,
            refundable=resp.refundable.value if resp.HasField("refundable") else None,
            grace_period=resp.description.value if resp.HasField("grace_period") else None,
        )


@dataclasses.dataclass
class Credit:
    value: decimal.Decimal
    description: typing.Optional[str]

    @classmethod
    def from_pb(cls, resp: fee_pb2.Credit):
        return cls(
            value=decimal.Decimal(resp.value),
            description=resp.description.value if resp.HasField("description") else None
        )


@dataclasses.dataclass
class FeeData:
    currency: str
    period: typing.Optional[Period]
    fees: typing.List[Fee]
    credits: typing.List[Credit]
    balance: typing.Optional[str]
    credit_limit: typing.Optional[str]

    @classmethod
    def from_pb(cls, resp: fee_pb2.FeeData):
        return cls(
            currency=resp.currency,
            period=Period.from_pb(resp.period) if resp.HasField("period") else None,
            fees=list(map(Fee.from_pb, resp.fees)),
            credits=list(map(Credit.from_pb, resp.credits)),
            balance=resp.balance.value if resp.HasField("balance") else None,
            credit_limit=resp.credit_limit.value if resp.HasField("credit_limit") else None,
        )

    @property
    def total_fee(self):
        return sum(map(lambda f: f.value, self.fees)) + sum(map(lambda c: c.value, self.credits))


@dataclasses.dataclass
class ChangeState:
    item: int

    @property
    def name(self):
        if self.item == epp_pb2.ChangeData.ChangeState.AFTER:
            return "after"
        elif self.item == epp_pb2.ChangeData.ChangeState.BEFORE:
            return "before"
        else:
            return "unknown"

    def __str__(self):
        if self.item == epp_pb2.ChangeData.ChangeState.AFTER:
            return "after"
        elif self.item == epp_pb2.ChangeData.ChangeState.BEFORE:
            return "before"
        else:
            return f"unknown ({self.item})"

    def __eq__(self, other):
        if type(other) == int:
            return self.item == other
        elif type(other) == self.__class__:
            return other.status == self.item
        else:
            return False


@dataclasses.dataclass
class ChangeOperationType:
    item: int

    @property
    def name(self):
        if self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Custom:
            return "custom"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Create:
            return "create"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Delete:
            return "delete"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Renew:
            return "renew"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Transfer:
            return "transfer"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Update:
            return "update"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Restore:
            return "restore"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.AutoRenew:
            return "auto_renew"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.AutoDelete:
            return "auto_delete"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.AutoPurge:
            return "auto_purge"
        else:
            return "unknown"

    def __str__(self):
        if self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Custom:
            return "Custom"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Create:
            return "Create"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Delete:
            return "Delete"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Renew:
            return "Renew"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Transfer:
            return "Transfer"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Update:
            return "Update"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Restore:
            return "Restore"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.AutoRenew:
            return "Automatic renew"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.AutoDelete:
            return "Automatic delete"
        elif self.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.AutoPurge:
            return "Automatic purge"
        else:
            return f"Unknown operation {self.item}"

    def __eq__(self, other):
        if type(other) == int:
            return self.item == other
        elif type(other) == self.__class__:
            return other.status == self.item
        else:
            return False


@dataclasses.dataclass
class ChangeOperation:
    type: ChangeOperationType
    operation: typing.Optional[str]

    @classmethod
    def from_pb(cls, resp: epp_pb2.ChangeData.ChangeOperation):
        return cls(
            type=ChangeOperationType(item=resp.operation_type),
            operation=resp.operation.value if resp.HasField("operation") else None,
        )

    def __str__(self):
        if self.type.item == epp_pb2.ChangeData.ChangeOperation.ChangeOperationType.Custom:
            return str(self.operation)
        else:
            if self.operation:
                return f"{self.type} ({self.operation})"
            else:
                return str(self.type)


@dataclasses.dataclass
class ChangeCaseIDType:
    item: int

    @property
    def name(self):
        if self.item == epp_pb2.ChangeData.CaseID.CaseIDType.Custom:
            return "custom"
        elif self.item == epp_pb2.ChangeData.CaseID.CaseIDType.UDRP:
            return "udrp"
        elif self.item == epp_pb2.ChangeData.CaseID.CaseIDType.URS:
            return "urs"
        else:
            return "unknown"

    def __str__(self):
        if self.item == epp_pb2.ChangeData.CaseID.CaseIDType.Custom:
            return "Custom"
        elif self.item == epp_pb2.ChangeData.CaseID.CaseIDType.UDRP:
            return "UDRP"
        elif self.item == epp_pb2.ChangeData.CaseID.CaseIDType.URS:
            return "URS"
        else:
            return f"Unknown Case Type ({self.item})"

    def __eq__(self, other):
        if type(other) == int:
            return self.item == other
        elif type(other) == self.__class__:
            return other.status == self.item
        else:
            return False


@dataclasses.dataclass
class ChangeCaseID:
    type: ChangeCaseIDType
    type_name: typing.Optional[str]
    case_id: str

    @classmethod
    def from_pb(cls, resp: epp_pb2.ChangeData.CaseID):
        return cls(
            type=ChangeCaseIDType(item=resp.case_id_type),
            type_name=resp.name.value if resp.HasField("name") else None,
            case_id=resp.case_id
        )

    def __str__(self):
        if self.type.item == 0:
            return f"{self.type_name}: {self.case_id}"
        else:
            if self.type_name:
                return f"{self.type} ({self.type_name}): {self.case_id}"
            else:
                return f"{self.type}: {self.case_id}"


@dataclasses.dataclass
class ChangeData:
    change_state: ChangeState
    change_operation: ChangeOperation
    date: datetime.datetime
    server_transaction_id: str
    who: str
    reason: typing.Optional[str]
    case_id: typing.Optional[ChangeCaseID]

    @classmethod
    def from_pb(cls, resp: epp_pb2.ChangeData):
        return cls(
            change_state=ChangeState(item=resp.change_state),
            change_operation=ChangeOperation.from_pb(resp.operation),
            date=resp.date.ToDatetime(),
            server_transaction_id=resp.server_transaction_id,
            who=resp.who,
            case_id=ChangeCaseID.from_pb(resp.case_id) if resp.HasField("case_id") else None,
            reason=resp.reason.value if resp.HasField("reason") else None
        )


class EPPClient:
    def __init__(self, server, ca, creds=None):
        with open(ca, 'rb') as f:
            cert = f.read()
        ssl_creds = grpc.ssl_channel_credentials(root_certificates=cert)
        if creds:
            channel_creds = grpc.composite_channel_credentials(ssl_creds, creds)
        else:
            channel_creds = grpc.composite_channel_credentials(ssl_creds)
        channel = grpc.secure_channel(server, channel_creds)
            
        self.stub = epp_pb2_grpc.EPPProxyStub(channel)

    def check_domain(self, domain: str, registry_id: typing.Optional[str] = None) -> typing.Tuple[bool, typing.Optional[str], str]:
        resp = self.stub.DomainCheck(domain_pb2.DomainCheckRequest(
            name=domain,
            registry_name=google.protobuf.wrappers_pb2.StringValue(
                value=registry_id
            ) if registry_id else None
        ))
        reason = resp.reason.value if resp.HasField("reason") else None
        return resp.available, reason, resp.registry_name

    def get_domain(
            self,
            domain: str,
            auth_info: typing.Optional[str] = None,
            registry_id: typing.Optional[str] = None,
    ) -> Domain:
        resp = self.stub.DomainInfo(domain_pb2.DomainInfoRequest(
            name=domain,
            registry_name=google.protobuf.wrappers_pb2.StringValue(
                value=registry_id
            ) if registry_id else None
        ))
        return Domain.from_pb(resp, self)

    def create_domain(
            self,
            domain: str,
            period: Period,
            registrant: str,
            contacts: typing.List[DomainContact],
            name_servers: typing.List[DomainNameServer],
            auth_info: str,
            keysys: typing.Optional[keysys_pb2.DomainCreate] = None,
            eurid: typing.Optional[eurid_pb2.DomainCreateExtension] = None,
            registry_id: typing.Optional[str] = None,
    ) -> typing.Tuple[bool, datetime.datetime, datetime.datetime, str]:
        resp = self.stub.DomainCreate(domain_pb2.DomainCreateRequest(
            name=domain,
            period=period.to_pb(),
            registrant=registrant,
            contacts=list(map(lambda c: c.to_pb(), contacts)),
            nameservers=list(map(lambda n: n.to_pb(), name_servers)),
            auth_info=auth_info,
            keysys=keysys,
            eurid_data=eurid,
            registry_name=google.protobuf.wrappers_pb2.StringValue(
                value=registry_id
            ) if registry_id else None
        ))
        return resp.pending, resp.creation_date.ToDatetime(), resp.expiry_date.ToDatetime(), resp.registry_name

    def delete_domain(
            self,
            domain: str,
            keysys_target: typing.Optional[str] = None,
            registry_id: typing.Optional[str] = None,
    ) -> typing.Tuple[bool, str, str, typing.Optional[FeeData]]:
        resp = self.stub.DomainDelete(domain_pb2.DomainDeleteRequest(
            name=domain,
            registry_name=google.protobuf.wrappers_pb2.StringValue(
                value=registry_id
            ) if registry_id else None
        ))

        if keysys_target:
            resp.keysys.CopyFrom(keysys_pb2.DomainDelete(
                target=keysys_target,
                action=keysys_pb2.Push
            ))

        return resp.pending, resp.registry_name, resp.cmd_resp.transaction_id.server,\
               FeeData.from_pb(resp.fee_data) if resp.HasField("fee_data") else None

    def restore_domain(
            self,
            domain: str,
            registry_id: typing.Optional[str] = None,
    ) -> typing.Tuple[bool, str]:
        resp = self.stub.DomainRestoreRequest(rgp_pb2.RequestRequest(
            name=domain,
            registry_name=google.protobuf.wrappers_pb2.StringValue(
                value=registry_id
            ) if registry_id else None
        ))
        return resp.pending, resp.registry_name

    def renew_domain(
            self,
            domain: str,
            period: Period,
            cur_expiry: datetime.datetime,
            registry_id: typing.Optional[str] = None,
    ) -> typing.Tuple[bool, datetime.datetime, str]:
        exp = Timestamp()
        exp.FromDatetime(cur_expiry)
        resp = self.stub.DomainRenew(domain_pb2.DomainRenewRequest(
            name=domain,
            period=period.to_pb(),
            current_expiry_date=exp,
            registry_name=google.protobuf.wrappers_pb2.StringValue(
                value=registry_id
            ) if registry_id else None
        ))
        return resp.pending, resp.expiry_date.ToDatetime(), resp.registry_name

    def transfer_query_domain(
            self,
            domain: str,
            auth_info: typing.Optional[str] = None,
            registry_id: typing.Optional[str] = None,
    ) -> DomainTransfer:
        resp = self.stub.DomainTransferQuery(domain_pb2.DomainTransferQueryRequest(
            name=domain,
            auth_info=StringValue(value=auth_info) if auth_info else None,
            registry_name=google.protobuf.wrappers_pb2.StringValue(
                value=registry_id
            ) if registry_id else None
        ))
        return DomainTransfer.from_pb(resp)

    def transfer_request_domain(
            self,
            domain: str,
            auth_info: str,
            period: typing.Optional[Period] = None,
            eurid: typing.Optional[eurid_pb2.DomainTransferExtension] = None,
            keysys: typing.Optional[keysys_pb2.DomainTransfer] = None,
            registry_id: typing.Optional[str] = None,
    ) -> DomainTransfer:
        resp = self.stub.DomainTransferRequest(domain_pb2.DomainTransferRequestRequest(
            name=domain,
            period=period.to_pb() if period else None,
            auth_info=auth_info,
            eurid_data=eurid,
            keysys=keysys,
            registry_name=google.protobuf.wrappers_pb2.StringValue(
                value=registry_id
            ) if registry_id else None
        ))
        return DomainTransfer.from_pb(resp)

    def transfer_accept_domain(
            self,
            domain: str,
            auth_info: str,
            registry_id: typing.Optional[str] = None,
    ) -> DomainTransfer:
        resp = self.stub.DomainTransferAccept(domain_pb2.DomainTransferAcceptRejectRequest(
            name=domain,
            auth_info=auth_info,
            registry_name=google.protobuf.wrappers_pb2.StringValue(
                value=registry_id
            ) if registry_id else None
        ))
        return DomainTransfer.from_pb(resp)

    def transfer_reject_domain(
            self,
            domain: str,
            auth_info: str,
            registry_id: typing.Optional[str] = None,
    ) -> DomainTransfer:
        resp = self.stub.DomainTransferReject(domain_pb2.DomainTransferAcceptRejectRequest(
            name=domain,
            auth_info=auth_info,
            registry_name=google.protobuf.wrappers_pb2.StringValue(
                value=registry_id
            ) if registry_id else None
        ))
        return DomainTransfer.from_pb(resp)

    def check_host(self, host_name: str, registry_name: str) -> typing.Tuple[bool, typing.Optional[str]]:
        resp = self.stub.HostCheck(host_pb2.HostCheckRequest(
            name=host_name,
            registry_name=registry_name
        ))
        reason = resp.reason.value if resp.HasField("reason") else None
        return resp.available, reason

    def get_host(self, host_name: str, registry_name: str) -> Host:
        resp = self.stub.HostInfo(host_pb2.HostInfoRequest(name=host_name, registry_name=registry_name))
        return Host.from_pb(resp, self, registry_name)

    def create_host(
            self, host_name: str, addresses: typing.List[IPAddress], registry_name: str,
            isnic_zone_contact: typing.Optional[str]
    ) -> typing.Tuple[bool, datetime.datetime]:
        resp = self.stub.HostCreate(host_pb2.HostCreateRequest(
            name=host_name,
            addresses=list(map(lambda a: a.to_pb(), addresses)),
            registry_name=registry_name,
            isnic_info=isnic_pb2.HostInfo(
                zone_contact=google.protobuf.wrappers_pb2.StringValue(value=isnic_zone_contact)
            ) if isnic_zone_contact else None,
        ))
        return resp.pending, resp.creation_date.ToDatetime()

    def delete_host(self, host_name: str, registry_name: str) -> bool:
        resp = self.stub.HostDelete(host_pb2.HostDeleteRequest(name=host_name, registry_name=registry_name))
        return resp.pending

    def check_contact(self, contact_id: str, registry_name: str) -> typing.Tuple[bool, typing.Optional[str]]:
        resp = self.stub.ContactCheck(contact_pb2.ContactCheckRequest(
            id=contact_id,
            registry_name=registry_name
        ))
        reason = resp.reason.value if resp.HasField("reason") else None
        return resp.available, reason

    def get_contact(
        self,
        contact_id: str,
        registry_name: str,
    ) -> Contact:
        resp = self.stub.ContactInfo(contact_pb2.ContactInfoRequest(
            id=contact_id,
            registry_name=registry_name
        ))
        return Contact.from_pb(resp, self, registry_name)

    def create_contact(
        self,
        contact_id: str,
        local_address: typing.Optional[Address],
        int_address: typing.Optional[Address],
        phone: typing.Optional[Phone],
        fax: typing.Optional[Phone],
        email: str,
        entity_type: int,
        trading_name: typing.Optional[str],
        company_number: typing.Optional[str],
        auth_info: str,
        disclosure: typing.Optional[Disclosure],
        eurid: typing.Optional[EURIDContact],
        registry_name: str,
    ) -> typing.Tuple[str, bool, datetime.datetime]:
        resp = self.stub.ContactCreate(contact_pb2.ContactCreateRequest(
            id=contact_id,
            local_address=local_address.to_pb() if local_address else None,
            internationalised_address=int_address.to_pb() if int_address else None,
            phone=phone.to_pb() if phone else None,
            fax=fax.to_pb() if fax else None,
            email=email,
            entity_type=entity_type,
            trading_name=StringValue(value=trading_name) if trading_name else None,
            company_number=StringValue(value=company_number) if company_number else None,
            auth_info=auth_info,
            disclosure=disclosure.to_pb() if disclosure else None,
            eurid_info=eurid.to_pb() if eurid else None,
            registry_name=registry_name
        ))
        return resp.id, resp.pending, resp.creation_date.ToDatetime()

    def delete_contact(self, contact_id: str, registry: str) -> bool:
        resp = self.stub.ContactDelete(contact_pb2.ContactDeleteRequest(id=contact_id, registry_name=registry))
        return resp.pending
