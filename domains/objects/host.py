import dataclasses
import typing
import grpc
import ipaddress
import datetime
from .. import models, apps
from . import exceptions


@dataclasses.dataclass
class IPAddress:
    address: str
    ip_type: int

    @property
    def address_obj(self) -> typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
        if self.ip_type == 1:
            return ipaddress.IPv4Address(self.address)
        elif self.ip_type == 2:
            return ipaddress.IPv6Address(self.address)
        else:
            raise Exception("Unknown IP address type")

    @property
    def ip_type_str(self) -> str:
        if self.ip_type == 0:
            return "Unknown"
        elif self.ip_type == 1:
            return "IPv4"
        elif self.ip_type == 2:
            return "IPv6"


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


@dataclasses.dataclass
class NameServer:
    name_server: str
    statuses: [HostStatus]
    addresses: [IPAddress]
    created: typing.Optional[datetime.datetime]
    last_updated: typing.Optional[datetime.datetime]
    last_transferred: typing.Optional[datetime.datetime]
    _obj: models.NameServer

    @property
    def unicode_name(self):
        try:
            return self.name_server.encode().decode('idna')
        except UnicodeError:
            return self.name_server

    @classmethod
    def get_from_db_obj(cls, obj: models.NameServer):
        if obj.protocol == models.PROTOCOL_EPP:
            try:
                host = apps.epp_client.get_host(obj.name_server, obj.registry_id)
            except grpc.RpcError as rpc_error:
                raise exceptions.ObjectError(rpc_error.details())
            return cls(
                name_server=host.name,
                statuses=list(map(lambda s: HostStatus(s), host.statuses)),
                addresses=list(map(lambda a: IPAddress(address=a.address, ip_type=a.ip_type), host.addresses)),
                created=host.creation_date,
                last_updated=host.last_updated_date,
                last_transferred=host.last_transfer_date,
                _obj=obj
            )
        elif obj.protocol == models.PROTOCOL_MANUAL:
            return cls(
                name_server=obj.name_server,
                statuses=[],
                addresses=list(map(lambda a: IPAddress(address=a.address, ip_type=a.address_type), obj.addresses.all())),
                created=None,
                last_updated=None,
                last_transferred=None,
                _obj=obj
            )

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
