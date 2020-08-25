import grpc
import google.protobuf.wrappers_pb2
import google.protobuf.timestamp_pb2
import re
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
            js_card=rdap_pb2.JSCard(
                uid=str(contact.id),
                full_name=rdap_pb2.JSCard.LocalisedString(
                    value=contact.local_address.name if contact.local_address.disclose_name else "REDACTED",
                )
            )
        )
        if contact.local_address.organisation:
            entity.js_card.organisation.append(rdap_pb2.JSCard.LocalisedString(
                value=contact.local_address.organisation if contact.local_address.disclose_organisation else "REDACTED",
            ))
        entity.js_card.addresses.append(rdap_pb2.JSCard.Address(
            street=google.protobuf.wrappers_pb2.StringValue(
                value=(
                    contact.local_address.street_1
                    + (("\n" + contact.local_address.street_2) if contact.local_address.street_2 else "")
                    + (("\n" + contact.local_address.street_3) if contact.local_address.street_3 else "")
                ) if contact.local_address.disclose_address else "REDACTED",
            ),
            locality=google.protobuf.wrappers_pb2.StringValue(value=contact.local_address.city),
            region=google.protobuf.wrappers_pb2.StringValue(
                value=contact.local_address.province
            ) if contact.local_address.province else None,
            post_code=google.protobuf.wrappers_pb2.StringValue(
                value=contact.local_address.postal_code if contact.local_address.disclose_address else "REDACTED"
            ),
            country=google.protobuf.wrappers_pb2.StringValue(
                value=contact.local_address.country_code.name
            ),
            country_code=google.protobuf.wrappers_pb2.StringValue(
                value=contact.local_address.country_code.code
            )
        ))
        if contact.disclose_phone:
            contact.phone.extension = contact.phone_ext
            entity.js_card.phones.append(rdap_pb2.JSCard.Resource(
                type=google.protobuf.wrappers_pb2.StringValue(value="voice"),
                value=contact.phone.as_rfc3966
            ))
            if contact.fax:
                contact.fax.extension = contact.fax_ext
                entity.js_card.phones.append(rdap_pb2.JSCard.Resource(
                    type=google.protobuf.wrappers_pb2.StringValue(value="fax"),
                    value=contact.fax.as_rfc3966
                ))
        else:
            entity.js_card.phones.extend([rdap_pb2.JSCard.Resource(
                type=google.protobuf.wrappers_pb2.StringValue(value="voice"),
                value="REDACTED"
            ), rdap_pb2.JSCard.Resource(
                type=google.protobuf.wrappers_pb2.StringValue(value="fax"),
                value="REDACTED"
            )])

        entity.js_card.emails.append(rdap_pb2.JSCard.Resource(
            value=contact.email if contact.disclose_email else "REDACTED",
        ))

        if contact.trading_name:
            entity.js_card.notes.append(rdap_pb2.JSCard.LocalisedString(
                value=f"Trading name: {contact.trading_name}"
            ))

        if contact.company_number:
            entity.js_card.notes.append(rdap_pb2.JSCard.LocalisedString(
                value=f"Company number: {contact.company_number}"
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
            entity.js_card.updated.MergeFrom(date)

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
            js_card=rdap_pb2.JSCard(
                uid=domain_data.client_id,
                kind=google.protobuf.wrappers_pb2.StringValue(value="org"),
                full_name=rdap_pb2.JSCard.LocalisedString(value="AS207960 Cyfyngedig"),
                addresses=[rdap_pb2.JSCard.Address(
                    street=google.protobuf.wrappers_pb2.StringValue(value="13 Pen-y-lan Terrace"),
                    locality=google.protobuf.wrappers_pb2.StringValue(value="Caerdydd"),
                    region=google.protobuf.wrappers_pb2.StringValue(value="Cymru"),
                    post_code=google.protobuf.wrappers_pb2.StringValue(value="CF23 9EU"),
                    country=google.protobuf.wrappers_pb2.StringValue(value="United Kingdom"),
                    country_code=google.protobuf.wrappers_pb2.StringValue(value="GB"),
                )],
                phones=[rdap_pb2.JSCard.Resource(
                    type=google.protobuf.wrappers_pb2.StringValue(value="voice"),
                    value="tel:+44-29-2010-2455"
                ), rdap_pb2.JSCard.Resource(
                    type=google.protobuf.wrappers_pb2.StringValue(value="fax"),
                    value="tel:+44-29-2010-2455"
                )],
                emails=[rdap_pb2.JSCard.Resource(
                    value="info@as207960.net"
                )],
                online=[rdap_pb2.JSCard.Resource(
                    type=google.protobuf.wrappers_pb2.StringValue(value="uri"),
                    value="https://as207960.net"
                )]
            ),
            entities=[rdap_pb2.Entity(
                handle=domain_data.client_id,
                roles=[rdap_pb2.RoleAbuse],
                js_card=rdap_pb2.JSCard(
                    uid=domain_data.client_id,
                    kind=google.protobuf.wrappers_pb2.StringValue(value="org"),
                    full_name=rdap_pb2.JSCard.LocalisedString(value="AS207960 Cyfyngedig Abuse Department"),
                    organisation=[rdap_pb2.JSCard.LocalisedString(
                        value="AS207960 Cyfyngedig"
                    )],
                    emails=[rdap_pb2.JSCard.Resource(
                        value="abuse@as207960.net"
                    )],
                    online=[rdap_pb2.JSCard.Resource(
                        type=google.protobuf.wrappers_pb2.StringValue(value="uri"),
                        value="https://as207960.net/contact"
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
            regex = re.sub(r"[-[\]{}()+?.,\\^$|#\s]", r'\\\g<0>', request.name).replace("*", ".*")
            domain_objs = models.DomainRegistration.objects.filter(
                domain__regex=f"^{regex}$"
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
            regex = re.sub(r"[-[\]{}()+?.,\\^$|#\s]", r'\\\g<0>', request.name).replace("*", ".*")
            contact_objs = models.Contact.objects.filter(
                Q(local_address__name__regex=f"^{regex}$", local_address__disclose_name=True) |
                Q(int_address__name__regex=f"^{regex}$", int_address__disclose_name=True) |
                Q(local_address__organisation__regex=f"^{regex}$", local_address__disclose_organisation=True) |
                Q(int_address__name__regex=f"^{regex}$", int_address__disclose_organisation=True) |
                Q(trading_name__regex=f"^{regex}$")
            )
            for contact_obj in contact_objs:
                if contact_obj.id not in entities:
                    entities[contact_obj.id] = contact_obj
        elif request.WhichOneof("query") == "handle":
            regex = re.sub(r"[-[\]{}()+?.,\\^$|#\s]", r'\\\g<0>', request.handle).replace("*", ".*")
            try:
                contact_objs = list(models.Contact.objects.filter(
                    id__regex=f"^{regex}$"
                ))
                for contact_obj in contact_objs:
                    if contact_obj.id not in entities:
                        entities[contact_obj.id] = contact_obj
            except django.core.exceptions.ValidationError:
                pass
            registry_contact_objs = models.ContactRegistry.objects.filter(
                registry_contact_id__regex=f"^{regex}$"
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
            regex = re.sub(r"[-[\]{}()+?.,\\^$|#\s]", r'\\\g<0>', request.name).replace("*", ".*")
            name_server_objs = models.NameServer.objects.filter(
                name_server__regex=f"^{regex}$"
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
