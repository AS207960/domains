import grpc
import google.protobuf.wrappers_pb2
import google.protobuf.timestamp_pb2
import ipaddress
import django.core.exceptions
import datetime
from django.db.models import Q
from .rdap_grpc import rdap_pb2
from .rdap_grpc import rdap_pb2_grpc
from . import models
from . import apps


def grpc_hook(server):
    rdap_pb2_grpc.add_RDAPServicer_to_server(RDAPServicer(), server)


class RDAPServicer(rdap_pb2_grpc.RDAPServicer):
    def contact_to_card(self, handle: str, roles, contact: models.Contact) -> rdap_pb2.Entity:
        entity = rdap_pb2.Entity(
            handle=handle,
            roles=roles,
            card=rdap_pb2.jCard(
                properties=[rdap_pb2.jCard.Property(
                    name="fn",
                    text=contact.local_address.name if contact.local_address.disclose_name else "REDACTED",
                )]
            )
        )
        if contact.local_address.organisation:
            entity.card.properties.append(rdap_pb2.jCard.Property(
                name="org",
                text=contact.local_address.organisation if contact.local_address.disclose_organisation else "REDACTED",
            ))
        entity.card.properties.append(rdap_pb2.jCard.Property(
            name="adr",
            properties={
                "cc": contact.local_address.country_code.code
            },
            text_array=rdap_pb2.jCard.Property.TextArray(
                data=[
                    contact.local_address.street_1 if contact.local_address.disclose_address else "REDACTED",
                    (contact.local_address.street_2 if contact.local_address.disclose_address else "REDACTED")
                    if contact.local_address.street_2 else "",
                    (contact.local_address.street_3 if contact.local_address.disclose_address else "REDACTED")
                    if contact.local_address.street_3 else "",
                    contact.local_address.city,
                    contact.local_address.province if contact.local_address.province else "",
                    contact.local_address.postal_code if contact.local_address.disclose_address else "",
                    contact.local_address.country_code.name
                ]
            )
        ))
        if contact.disclose_phone:
            contact.phone.extension = contact.phone_ext
            entity.card.properties.append(rdap_pb2.jCard.Property(
                name="tel",
                properties={
                    "type": "voice"
                },
                uri=contact.phone.as_rfc3966
            ))
            if contact.fax:
                contact.fax.extension = contact.fax_ext
                entity.card.properties.append(rdap_pb2.jCard.Property(
                    name="tel",
                    properties={
                        "type": "fax"
                    },
                    uri=contact.fax.as_rfc3966
                ))
        else:
            entity.card.properties.extend([rdap_pb2.jCard.Property(
                name="tel",
                properties={
                    "type": "voice"
                },
                text="REDACTED"
            ), rdap_pb2.jCard.Property(
                name="tel",
                properties={
                    "type": "fax"
                },
                text="REDACTED"
            )])

        entity.card.properties.append(rdap_pb2.jCard.Property(
            name="email",
            text=contact.email if contact.disclose_email else "REDACTED",
        ))

        if contact.trading_name:
            entity.remarks.append(rdap_pb2.Remark(
                title=google.protobuf.wrappers_pb2.StringValue(value="Trading name"),
                description=contact.trading_name
            ))

        if contact.company_number:
            entity.remarks.append(rdap_pb2.Remark(
                title=google.protobuf.wrappers_pb2.StringValue(value="Company number"),
                description=contact.company_number
            ))

        if contact.created_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(contact.created_date)
            entity.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventRegistration,
                date=date
            ))

        if contact.updated_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(contact.created_date)
            entity.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventLastChanged,
                date=date
            ))

        date = google.protobuf.timestamp_pb2.Timestamp()
        date.FromDatetime(datetime.datetime.utcnow())
        entity.events.append(rdap_pb2.Event(
            action=rdap_pb2.EventLastUpdateOfRDAP,
            date=date
        ))

        if not (
                contact.local_address.disclose_name or contact.local_address.disclose_organisation
                or contact.local_address.disclose_address or contact.disclose_email or contact.disclose_phone
                or contact.disclose_fax
        ):
            entity.remarks.append(rdap_pb2.Remark(
                title=google.protobuf.wrappers_pb2.StringValue(value="REDACTED FOR PRIVACY"),
                description="some of the data in this object has been removed",
                type=google.protobuf.wrappers_pb2.StringValue(value="object redacted due to authorization")
            ))

        return entity

    def domain_status_to_rdap(self, status: apps.epp_api.DomainStatus):
        if status == apps.epp_api.domain_pb2.Ok:
            return rdap_pb2.StatusActive
        elif status == apps.epp_api.domain_pb2.Inactive:
            return rdap_pb2.StatusInactive
        elif status == apps.epp_api.domain_pb2.ClientDeleteProhibited:
            return rdap_pb2.StatusClientDeleteProhibited
        elif status == apps.epp_api.domain_pb2.ClientHold:
            return rdap_pb2.StatusClientHold
        elif status == apps.epp_api.domain_pb2.ClientRenewProhibited:
            return rdap_pb2.StatusClientRenewProhibited
        elif status == apps.epp_api.domain_pb2.ClientTransferProhibited:
            return rdap_pb2.StatusClientTransferProhibited
        elif status == apps.epp_api.domain_pb2.ClientUpdateProhibited:
            return rdap_pb2.StatusClientUpdateProhibited
        elif status == apps.epp_api.domain_pb2.PendingCreate:
            return rdap_pb2.StatusPendingCreate
        elif status == apps.epp_api.domain_pb2.PendingDelete:
            return rdap_pb2.StatusPendingDelete
        elif status == apps.epp_api.domain_pb2.PendingRenew:
            return rdap_pb2.StatusPendingRenew
        elif status == apps.epp_api.domain_pb2.PendingTransfer:
            return rdap_pb2.StatusPendingTransfer
        elif status == apps.epp_api.domain_pb2.PendingUpdate:
            return rdap_pb2.StatusPendingUpdate
        elif status == apps.epp_api.domain_pb2.ServerDeleteProhibited:
            return rdap_pb2.StatusServerDeleteProhibited
        elif status == apps.epp_api.domain_pb2.ServerHold:
            return rdap_pb2.StatusServerHold
        elif status == apps.epp_api.domain_pb2.ServerRenewProhibited:
            return rdap_pb2.StatusServerRenewProhibited
        elif status == apps.epp_api.domain_pb2.ServerTransferProhibited:
            return rdap_pb2.StatusServerTransferProhibited
        elif status == apps.epp_api.domain_pb2.ServerUpdateProhibited:
            return rdap_pb2.StatusServerUpdateProhibited

    def rgp_status_to_rdap(self, status: apps.epp_api.RGPState):
        if status == apps.epp_api.rgp_pb2.AddPeriod:
            return rdap_pb2.StatusAddPeriod
        elif status == apps.epp_api.rgp_pb2.AutoRenewPeriod:
            return rdap_pb2.StatusAutoRenewPeriod
        elif status == apps.epp_api.rgp_pb2.RenewPeriod:
            return rdap_pb2.StatusRenewPeriod
        elif status == apps.epp_api.rgp_pb2.TransferPeriod:
            return rdap_pb2.StatusTransferPeriod
        elif status == apps.epp_api.rgp_pb2.RedemptionPeriod:
            return rdap_pb2.StatusRedemptionPeriod
        elif status == apps.epp_api.rgp_pb2.PendingRestore:
            return rdap_pb2.StatusPendingRestore
        elif status == apps.epp_api.rgp_pb2.PendingDelete:
            return rdap_pb2.StatusPendingDelete

    def domain_to_proto(self, domain_obj: models.DomainRegistration) -> rdap_pb2.Domain:
        domain_data = apps.epp_client.get_domain(domain_obj.domain)

        resp_data = rdap_pb2.Domain(
            handle=domain_data.registry_id,
            name=domain_data.name,
            port43=google.protobuf.wrappers_pb2.StringValue(value="whois.as207960.net")
        )

        for status in domain_data.statuses:
            resp_data.statuses.append(self.domain_status_to_rdap(status))
        for status in domain_data.rgp_state:
            resp_data.statuses.append(self.rgp_status_to_rdap(status))

        resp_data.entities.append(rdap_pb2.Entity(
            handle=domain_data.client_id,
            roles=[rdap_pb2.RoleRegistrar],
            card=rdap_pb2.jCard(
                properties=[rdap_pb2.jCard.Property(
                    name="kind",
                    text="org"
                ), rdap_pb2.jCard.Property(
                    name="fn",
                    text="AS207960 Cyfyngedig"
                ), rdap_pb2.jCard.Property(
                    name="adr",
                    properties={
                        "cc": "gb"
                    },
                    text_array=rdap_pb2.jCard.Property.TextArray(
                        data=["", "", "13 Pen-y-lan Terrace", "Caerdydd", "Cymru", "CF23 9EU", "United Kingdom"]
                    )
                ), rdap_pb2.jCard.Property(
                    name="tel",
                    uri="tel:+442920102455",
                    properties={
                        "type": "voice"
                    }
                ), rdap_pb2.jCard.Property(
                    name="tel",
                    uri="tel:+442920102455",
                    properties={
                        "type": "fax"
                    }
                ), rdap_pb2.jCard.Property(
                    name="email",
                    text="info@as207960.net",
                ), rdap_pb2.jCard.Property(
                    name="lang",
                    language="en"
                ), rdap_pb2.jCard.Property(
                    name="logo",
                    uri="https://as207960.net/assets/img/logo.svg"
                ), rdap_pb2.jCard.Property(
                    name="url",
                    uri="https://as207960.net"
                )]
            ),
            entities=[rdap_pb2.Entity(
                handle=domain_data.client_id,
                roles=[rdap_pb2.RoleAbuse],
                card=rdap_pb2.jCard(
                    properties=[rdap_pb2.jCard.Property(
                        name="fn",
                        text="AS207960 Cyfyngedig Abuse Department"
                    ),  rdap_pb2.jCard.Property(
                        name="email",
                        text="abuse@as207960.net",
                    ), rdap_pb2.jCard.Property(
                        name="lang",
                        language="en"
                    )]
                ),
            )]
        ))

        entities = {}

        def add_entity(handle, obj, role):
            obj_id = str(obj.id)
            if obj_id not in entities:
                entities[obj_id] = {
                    "handle": handle,
                    "contact": obj,
                    "roles": [role]
                }
            else:
                entities[obj_id]["roles"].append(role)
                if not entities[obj_id]["handle"]:
                    entities[obj_id]["handle"] = handle

        user = domain_obj.get_user()
        if domain_data.registrant:
            contact = models.Contact.get_contact(domain_data.registrant, domain_data.registry_name, user)
            add_entity(domain_data.registrant, contact, rdap_pb2.RoleRegistrant)
        elif domain_obj.registrant_contact:
            add_entity(None, domain_obj.registrant_contact, rdap_pb2.RoleRegistrant)

        if domain_data.admin:
            contact = models.Contact.get_contact(domain_data.admin.contact_id, domain_data.registry_name, user)
            add_entity(domain_data.admin.contact_id, contact, rdap_pb2.RoleAdministrative)
        elif domain_obj.admin_contact:
            add_entity(None, domain_obj.admin_contact, rdap_pb2.RoleAdministrative)

        if domain_data.billing:
            contact = models.Contact.get_contact(domain_data.billing.contact_id, domain_data.registry_name, user)
            add_entity(domain_data.billing.contact_id, contact, rdap_pb2.RoleBilling)
        elif domain_obj.billing_contact:
            add_entity(None, domain_obj.billing_contact, rdap_pb2.RoleBilling)

        if domain_data.tech:
            contact = models.Contact.get_contact(domain_data.tech.contact_id, domain_data.registry_name, user)
            add_entity(domain_data.tech.contact_id, contact, rdap_pb2.RoleTechnical)
        elif domain_obj.tech_contact:
            add_entity(None, domain_obj.tech_contact, rdap_pb2.RoleTechnical)

        for c in entities.values():
            resp_data.entities.append(self.contact_to_card(c["handle"], c["roles"], c["contact"]))

        if domain_data.creation_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(domain_data.creation_date)
            resp_data.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventRegistration,
                date=date
            ))
        if domain_data.expiry_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(domain_data.expiry_date)
            resp_data.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventExpiration,
                date=date
            ))
        if domain_data.last_updated_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(domain_data.last_updated_date)
            resp_data.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventLastChanged,
                date=date
            ))
        if domain_data.last_transfer_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(domain_data.last_transfer_date)
            resp_data.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventTransfer,
                date=date
            ))

        date = google.protobuf.timestamp_pb2.Timestamp()
        date.FromDatetime(datetime.datetime.utcnow())
        resp_data.events.append(rdap_pb2.Event(
            action=rdap_pb2.EventLastUpdateOfRDAP,
            date=date
        ))

        for ns in domain_data.name_servers:
            try:
                resp_data.name_servers.append(self.name_server_to_proto(models.NameServer(
                    name_server=ns.host_obj,
                    registry_id=domain_data.registry_name
                )))
            except grpc.RpcError:
                resp_data.name_servers.append(rdap_pb2.NameServer(
                    name=ns.host_obj,
                    port43=google.protobuf.wrappers_pb2.StringValue(value="whois.as207960.net")
                ))

        if domain_data.sec_dns:
            resp_data.sec_dns.delegation_signed.value = True
            if domain_data.sec_dns.max_sig_life:
                resp_data.sec_dns.max_sig_life.value = domain_data.sec_dns.max_sig_life
            if domain_data.sec_dns.ds_data:
                resp_data.sec_dns.ds_data.extend(map(lambda d: rdap_pb2.Domain.SecDNS.DSData(
                    key_tag=d.key_tag,
                    algorithm=d.algorithm,
                    digest_type=d.digest_type,
                    digest=d.digest
                ), domain_data.sec_dns.ds_data))
            if domain_data.sec_dns.key_data:
                resp_data.sec_dns.key_data.extend(map(lambda d: rdap_pb2.Domain.SecDNS.KeyData(
                    flags=d.flags,
                    protocol=d.protocol,
                    algorithm=d.algorithm,
                    public_key=d.public_key
                ), domain_data.sec_dns.key_data))
        else:
            resp_data.sec_dns.delegation_signed.value = False

        return resp_data

    def name_server_status_to_rdap(self, status: apps.epp_api.HostStatus):
        if status == apps.epp_api.host_pb2.Ok:
            return rdap_pb2.StatusActive
        if status == apps.epp_api.host_pb2.Linked:
            return rdap_pb2.StatusAssociated
        elif status == apps.epp_api.host_pb2.ClientDeleteProhibited:
            return rdap_pb2.StatusClientDeleteProhibited
        elif status == apps.epp_api.host_pb2.ClientUpdateProhibited:
            return rdap_pb2.StatusClientUpdateProhibited
        elif status == apps.epp_api.host_pb2.PendingCreate:
            return rdap_pb2.StatusPendingCreate
        elif status == apps.epp_api.host_pb2.PendingDelete:
            return rdap_pb2.StatusPendingDelete
        elif status == apps.epp_api.host_pb2.PendingTransfer:
            return rdap_pb2.StatusPendingTransfer
        elif status == apps.epp_api.host_pb2.PendingUpdate:
            return rdap_pb2.StatusPendingUpdate
        elif status == apps.epp_api.host_pb2.ServerDeleteProhibited:
            return rdap_pb2.StatusServerDeleteProhibited
        elif status == apps.epp_api.host_pb2.ServerUpdateProhibited:
            return rdap_pb2.StatusServerUpdateProhibited

    def name_server_to_proto(self, name_server_obj: models.NameServer) -> rdap_pb2.NameServer:
        name_server_data = apps.epp_client.get_host(name_server_obj.name_server, name_server_obj.registry_id)

        resp_data = rdap_pb2.NameServer(
            handle=name_server_data.registry_id,
            name=name_server_data.name,
            port43=google.protobuf.wrappers_pb2.StringValue(value="whois.as207960.net")
        )

        for status in name_server_data.statuses:
            resp_data.statuses.append(self.name_server_status_to_rdap(status))

        if name_server_data.creation_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(name_server_data.creation_date)
            resp_data.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventRegistration,
                date=date
            ))
        if name_server_data.last_updated_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(name_server_data.last_updated_date)
            resp_data.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventLastChanged,
                date=date
            ))
        if name_server_data.last_transfer_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(name_server_data.last_transfer_date)
            resp_data.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventTransfer,
                date=date
            ))

        for address in name_server_data.addresses:
            if address.ip_type == apps.epp_api.common_pb2.IPAddress.IPv4:
                resp_data.ip_addresses.v4.append(address.address)
            elif address.ip_type == apps.epp_api.common_pb2.IPAddress.IPv6:
                resp_data.ip_addresses.v6.append(address.address)

        return resp_data

    def DomainLookup(self, request: rdap_pb2.LookupRequest, context):
        domain_obj = models.DomainRegistration.objects.filter(
            domain=request.query
        ).first()  # type: models.DomainRegistration
        if not domain_obj:
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=404,
                title="Not found",
                description="No such domain"
            ))
            return response

        try:
            resp_data = self.domain_to_proto(domain_obj)
        except grpc.RpcError as e:
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=500,
                title="Internal Server Error",
                description=e.details()
            ))
            return response

        response = rdap_pb2.DomainResponse(success=resp_data)
        return response

    def DomainSearch(self, request: rdap_pb2.DomainSearchRequest, context):
        if request.WhichOneof("query") == "name":
            domain_objs = models.DomainRegistration.objects.filter(
                domain__search=request.name
            )
        else:
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=400,
                title="Not provided",
                description="Service not provided"
            ))
            return response

        resp_data = []
        for domain_obj in domain_objs:
            try:
                resp_data.append(self.domain_to_proto(domain_obj))
            except grpc.RpcError as e:
                response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                    error_code=500,
                    title="Internal Server Error",
                    description=e.details()
                ))
                return response

        response = rdap_pb2.DomainSearchResponse(success=rdap_pb2.DomainSearchResponse.Domains(
            data=resp_data
        ))
        return response

    def EntityLookup(self, request: rdap_pb2.LookupRequest, context):
        try:
            contact_obj = models.Contact.objects.filter(
                id=request.query
            ).first()  # type: models.Contact
        except django.core.exceptions.ValidationError:
            contact_obj = None

        if not contact_obj:
            registry_contact_obj = models.ContactRegistry.objects.filter(
                registry_contact_id=request.query
            ).first()  # type: models.ContactRegistry
            if not registry_contact_obj:
                response = rdap_pb2.EntityResponse(error=rdap_pb2.ErrorResponse(
                    error_code=404,
                    title="Not found",
                    description="No such entity"
                ))
                return response
            contact_obj = registry_contact_obj.contact

        entity = self.contact_to_card(request.query, [], contact_obj)
        response = rdap_pb2.EntityResponse(success=entity)
        return response

    def EntitySearch(self, request: rdap_pb2.EntitySearchRequest, context):
        entities = {}

        if request.WhichOneof("query") == "name":
            contact_objs = models.Contact.objects.filter(
                Q(local_address__name__search=request.name, local_address__disclose_name=True) |
                Q(int_address__name__search=request.name, int_address__disclose_name=True) |
                Q(local_address__organisation__search=request.name, local_address__disclose_organisation=True) |
                Q(int_address__name__search=request.name, int_address__disclose_organisation=True) |
                Q(trading_name__search=request.name)
            )
            for contact_obj in contact_objs:
                if contact_obj.id not in entities:
                    entities[contact_obj.id] = contact_obj
        elif request.WhichOneof("query") == "handle":
            try:
                contact_objs = list(models.Contact.objects.filter(
                    id__search=request.handle
                ))
                for contact_obj in contact_objs:
                    if contact_obj.id not in entities:
                        entities[contact_obj.id] = contact_obj
            except django.core.exceptions.ValidationError:
                pass
            registry_contact_objs = models.ContactRegistry.objects.filter(
                registry_contact_id__search=request.handle
            )
            for registry_contact_obj in registry_contact_objs:
                if registry_contact_obj.registry_contact_id not in entities:
                    entities[registry_contact_obj.registry_contact_id] = registry_contact_obj.contact
        else:
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=400,
                title="Not provided",
                description="Service not provided"
            ))
            return response

        resp_data = []
        for handle, contact_obj in entities.items():
            resp_data.append(self.contact_to_card(handle, [], contact_obj))

        response = rdap_pb2.EntitySearchResponse(success=rdap_pb2.EntitySearchResponse.Entities(
            data=resp_data
        ))
        return response

    def NameServerLookup(self, request: rdap_pb2.LookupRequest, context):
        name_server_obj = models.NameServer.objects.filter(
            name_server=request.query
        ).first()  # type: models.NameServer
        if not name_server_obj:
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=404,
                title="Not found",
                description="No such name server"
            ))
            return response

        try:
            resp_data = self.name_server_to_proto(name_server_obj)
        except grpc.RpcError as e:
            response = rdap_pb2.NameServerResponse(error=rdap_pb2.ErrorResponse(
                error_code=500,
                title="Internal Server Error",
                description=e.details()
            ))
            return response

        response = rdap_pb2.NameServerResponse(success=resp_data)
        return response

    def NameServerSearch(self, request: rdap_pb2.NameServerSearchRequest, context):
        if request.WhichOneof("query") == "name":
            name_server_objs = models.NameServer.objects.filter(
                name_server__search=request.name
            )
        else:
            response = rdap_pb2.NameServerResponse(error=rdap_pb2.ErrorResponse(
                error_code=400,
                title="Not provided",
                description="Service not provided"
            ))
            return response

        resp_data = []
        for name_server_obj in name_server_objs:
            try:
                resp_data.append(self.name_server_to_proto(name_server_obj))
            except grpc.RpcError as e:
                response = rdap_pb2.NameServerResponse(error=rdap_pb2.ErrorResponse(
                    error_code=500,
                    title="Internal Server Error",
                    description=e.details()
                ))
                return response

        response = rdap_pb2.NameServerSearchResponse(success=rdap_pb2.NameServerSearchResponse.NameServers(
            data=resp_data
        ))
        return response
