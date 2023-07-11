import grpc
import google.protobuf.wrappers_pb2
import google.protobuf.timestamp_pb2
import re
import django.core.exceptions
import datetime
import concurrent.futures
import traceback
import sys
from django.db.models import Q
from .rdap_grpc import rdap_pb2
from .rdap_grpc import rdap_pb2_grpc
from . import models, apps, zone_info


def grpc_hook(server):
    rdap_pb2_grpc.add_RDAPServicer_to_server(RDAPServicer(), server)


class RDAPServicer(rdap_pb2_grpc.RDAPServicer):
    def contact_to_card(self, roles, contact: models.Contact) -> rdap_pb2.Entity:
        created_date = google.protobuf.timestamp_pb2.Timestamp()
        created_date.FromDatetime(contact.created_date)

        entity = rdap_pb2.Entity(
            handle=contact.handle,
            roles=roles,
            port43=google.protobuf.wrappers_pb2.StringValue(value="whois.as207960.net"),
            js_card=rdap_pb2.JSCard(
                uid=contact.handle,
                name=rdap_pb2.JSCard.Name(
                    full_name=google.protobuf.wrappers_pb2.StringValue(
                        value=contact.local_address.name if contact.local_address.disclose_name else "REDACTED",
                    )
                ),
                addresses={
                    "a": rdap_pb2.JSCard.Address(
                        country_code=google.protobuf.wrappers_pb2.StringValue(
                            value=contact.local_address.country_code.code
                        ),
                        default_seperator=google.protobuf.wrappers_pb2.StringValue(
                            value="\n"
                        ),
                    )
                },
                emails={
                    "e": rdap_pb2.JSCard.Email(
                        email=contact.get_public_email()
                    )
                }
            ),
        )

        if contact.local_address.organisation:
            entity.js_card.organisations["o"].CopyFrom(rdap_pb2.JSCard.Organisation(
                name=google.protobuf.wrappers_pb2.StringValue(
                    value=contact.local_address.organisation if contact.local_address.disclose_organisation else "REDACTED",
                )
            ))

        if contact.local_address.disclose_address:
            entity.js_card.addresses["a"].components.append(
                rdap_pb2.JSCard.Address.AddressComponent(
                    kind=rdap_pb2.JSCard.Address.AddressComponent.Name,
                    value=contact.local_address.street_1
                )
            )
            if contact.local_address.street_2:
                entity.js_card.addresses["a"].components.append(
                    rdap_pb2.JSCard.Address.AddressComponent(
                        kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                        value="\n"
                    )
                )
                entity.js_card.addresses["a"].components.append(
                    rdap_pb2.JSCard.Address.AddressComponent(
                        kind=rdap_pb2.JSCard.Address.AddressComponent.Name,
                        value=contact.local_address.street_2
                    )
                )
            if contact.local_address.street_3:
                entity.js_card.addresses["a"].components.append(
                    rdap_pb2.JSCard.Address.AddressComponent(
                        kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                        value="\n"
                    )
                )
                entity.js_card.addresses["a"].components.append(
                    rdap_pb2.JSCard.Address.AddressComponent(
                        kind=rdap_pb2.JSCard.Address.AddressComponent.Name,
                        value=contact.local_address.street_3
                    )
                )
        else:
            entity.js_card.addresses["a"].components.append(
                rdap_pb2.JSCard.Address.AddressComponent(
                    kind=rdap_pb2.JSCard.Address.AddressComponent.Name,
                    value="REDACTED"
                )
            )

        entity.js_card.addresses["a"].components.append(
            rdap_pb2.JSCard.Address.AddressComponent(
                kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                value="\n"
            )
        )
        entity.js_card.addresses["a"].components.append(
            rdap_pb2.JSCard.Address.AddressComponent(
                kind=rdap_pb2.JSCard.Address.AddressComponent.Locality,
                value=contact.local_address.city
            )
        )
        if contact.local_address.province:
            entity.js_card.addresses["a"].components.append(
                rdap_pb2.JSCard.Address.AddressComponent(
                    kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                    value="\n"
                )
            )
            entity.js_card.addresses["a"].components.append(
                rdap_pb2.JSCard.Address.AddressComponent(
                    kind=rdap_pb2.JSCard.Address.AddressComponent.Region,
                    value=contact.local_address.province
                )
            )
        if contact.local_address.postal_code:
            entity.js_card.addresses["a"].components.append(
                rdap_pb2.JSCard.Address.AddressComponent(
                    kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                    value="\n"
                )
            )
            entity.js_card.addresses["a"].components.append(
                rdap_pb2.JSCard.Address.AddressComponent(
                    kind=rdap_pb2.JSCard.Address.AddressComponent.Postcode,
                    value=contact.local_address.postal_code
                )
            )

        entity.js_card.addresses["a"].components.append(
            rdap_pb2.JSCard.Address.AddressComponent(
                kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                value="\n"
            )
        )
        entity.js_card.addresses["a"].components.append(
            rdap_pb2.JSCard.Address.AddressComponent(
                kind=rdap_pb2.JSCard.Address.AddressComponent.Country,
                value=contact.local_address.country_code.name
            )
        )

        if contact.disclose_phone:
            contact.phone.extension = contact.phone_ext
            entity.js_card.phones["p"].CopyFrom(rdap_pb2.JSCard.Phone(
                number=contact.phone.as_rfc3966,
                features=[rdap_pb2.JSCard.Phone.Voice]
            ))
        else:
            entity.js_card.phones["p"].CopyFrom(rdap_pb2.JSCard.Phone(
                number="REDACTED",
                features=[rdap_pb2.JSCard.Phone.Voice]
            ))
        if contact.disclose_fax:
            if contact.fax:
                contact.fax.extension = contact.fax_ext
                entity.js_card.phones["f"].CopyFrom(rdap_pb2.JSCard.Phone(
                    number=contact.phone.as_rfc3966,
                    features=[rdap_pb2.JSCard.Phone.Fax]
                ))
        else:
            entity.js_card.phones["f"].CopyFrom(rdap_pb2.JSCard.Phone(
                number="REDACTED",
                features=[rdap_pb2.JSCard.Phone.Fax]
            ))

        if contact.trading_name:
            entity.js_card.notes["tn"].CopyFrom(rdap_pb2.JSCard.Note(
                note=f"Trading name: {contact.trading_name}"
            ))

        if contact.company_number:
            entity.js_card.notes["cn"].CopyFrom(rdap_pb2.JSCard.Note(
                note=f"Company number: {contact.company_number}"
            ))

        if contact.created_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(contact.created_date)
            entity.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventRegistration,
                date=date
            ))
            entity.js_card.created.MergeFrom(date)

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
                contact.local_address.disclose_name and contact.local_address.disclose_organisation
                and contact.local_address.disclose_address and contact.disclose_email and contact.disclose_phone
                and contact.disclose_fax
        ):
            entity.remarks.append(rdap_pb2.Remark(
                title=google.protobuf.wrappers_pb2.StringValue(value="REDACTED FOR PRIVACY"),
                description="some of the data in this object has been removed",
                type=google.protobuf.wrappers_pb2.StringValue(value="object redacted due to authorization")
            ))

        return entity

    def domain_status_to_rdap(self, status: apps.epp_api.DomainStatus):
        if status == apps.epp_api.domain_common_pb2.DomainStatus.Ok:
            return rdap_pb2.StatusActive
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.Inactive:
            return rdap_pb2.StatusInactive
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.ClientDeleteProhibited:
            return rdap_pb2.StatusClientDeleteProhibited
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.ClientHold:
            return rdap_pb2.StatusClientHold
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.ClientRenewProhibited:
            return rdap_pb2.StatusClientRenewProhibited
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.ClientTransferProhibited:
            return rdap_pb2.StatusClientTransferProhibited
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.ClientUpdateProhibited:
            return rdap_pb2.StatusClientUpdateProhibited
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.PendingCreate:
            return rdap_pb2.StatusPendingCreate
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.PendingDelete:
            return rdap_pb2.StatusPendingDelete
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.PendingRenew:
            return rdap_pb2.StatusPendingRenew
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.PendingTransfer:
            return rdap_pb2.StatusPendingTransfer
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.PendingUpdate:
            return rdap_pb2.StatusPendingUpdate
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.ServerDeleteProhibited:
            return rdap_pb2.StatusServerDeleteProhibited
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.ServerHold:
            return rdap_pb2.StatusServerHold
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.ServerRenewProhibited:
            return rdap_pb2.StatusServerRenewProhibited
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.ServerTransferProhibited:
            return rdap_pb2.StatusServerTransferProhibited
        elif status == apps.epp_api.domain_common_pb2.DomainStatus.ServerUpdateProhibited:
            return rdap_pb2.StatusServerUpdateProhibited

    def rgp_status_to_rdap(self, status: apps.epp_api.RGPState):
        if status == apps.epp_api.rgp_pb2.RGPState.AddPeriod:
            return rdap_pb2.StatusAddPeriod
        elif status == apps.epp_api.rgp_pb2.RGPState.AutoRenewPeriod:
            return rdap_pb2.StatusAutoRenewPeriod
        elif status == apps.epp_api.rgp_pb2.RGPState.RenewPeriod:
            return rdap_pb2.StatusRenewPeriod
        elif status == apps.epp_api.rgp_pb2.RGPState.TransferPeriod:
            return rdap_pb2.StatusTransferPeriod
        elif status == apps.epp_api.rgp_pb2.RGPState.RedemptionPeriod:
            return rdap_pb2.StatusRedemptionPeriod
        elif status == apps.epp_api.rgp_pb2.RGPState.PendingRestore:
            return rdap_pb2.StatusPendingRestore
        elif status == apps.epp_api.rgp_pb2.RGPState.PendingDelete:
            return rdap_pb2.StatusPendingDelete

    def domain_to_proto(self, domain_obj: models.DomainRegistration) -> rdap_pb2.Domain:
        domain_data = apps.epp_client.get_domain(domain_obj.domain)
        zone_data = zone_info.get_domain_info(domain_data.name.lower())[0]

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
            port43=google.protobuf.wrappers_pb2.StringValue(value="whois.as207960.net"),
            js_card=rdap_pb2.JSCard(
                uid=domain_data.client_id,
                kind=rdap_pb2.JSCard.Kind.Org,
                organisations={
                    "o": rdap_pb2.JSCard.Organisation(
                        name=google.protobuf.wrappers_pb2.StringValue(value="AS207960 Cyfyngedig"),
                    )
                },
                addresses={
                    "a": rdap_pb2.JSCard.Address(
                        components=[rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Number,
                            value="13"
                        ), rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                            value=" "
                        ), rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Name,
                            value="Pen-y-lan Terrace"
                        ), rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                            value="\n"
                        ), rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Locality,
                            value="Caerdydd"
                        ), rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                            value="\n"
                        ), rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Region,
                            value="Cymru"
                        ), rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                            value="\n"
                        ), rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Postcode,
                            value="CF23 9EU"
                        ), rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Separator,
                            value="\n"
                        ), rdap_pb2.JSCard.Address.AddressComponent(
                            kind=rdap_pb2.JSCard.Address.AddressComponent.Country,
                            value="United Kingdom"
                        )],
                        country_code=google.protobuf.wrappers_pb2.StringValue(value="GB"),
                        timezone=google.protobuf.wrappers_pb2.StringValue(value="Europe/London"),
                    )
                },
                phones={
                    "p": rdap_pb2.JSCard.Phone(
                        number="tel:+44-33-33-408418",
                        features=[rdap_pb2.JSCard.Phone.Voice, rdap_pb2.JSCard.Phone.Fax]
                    )
                },
                emails={
                    "e": rdap_pb2.JSCard.Email(
                        email="hello@glauca.digital"
                    )
                },
                online_services={
                    "w": rdap_pb2.JSCard.OnlineService(
                        service=google.protobuf.wrappers_pb2.StringValue(value="Website"),
                        uri=google.protobuf.wrappers_pb2.StringValue(value="https://glauca.digital"),
                    ),
                    "m": rdap_pb2.JSCard.OnlineService(
                        service=google.protobuf.wrappers_pb2.StringValue(value="Mastodon"),
                        uri=google.protobuf.wrappers_pb2.StringValue(value="https://glauca.space/@glauca"),
                        user=google.protobuf.wrappers_pb2.StringValue(value="@glauca@glauca.space"),
                    )
                }
            ),
            entities=[rdap_pb2.Entity(
                handle=domain_data.client_id,
                roles=[rdap_pb2.RoleAbuse],
                js_card=rdap_pb2.JSCard(
                    uid=domain_data.client_id,
                    kind=rdap_pb2.JSCard.Kind.Org,
                    organisations={
                        "o": rdap_pb2.JSCard.Organisation(
                            name=google.protobuf.wrappers_pb2.StringValue(value="AS207960 Cyfyngedig"),
                            units=[rdap_pb2.JSCard.Organisation.OrganisationUnit(
                                name="Abuse Department"
                            )]
                        )
                    },
                    emails={
                        "e": rdap_pb2.JSCard.Email(
                            email="abuse@as207960.net"
                        )
                    },
                    links={
                        "c": rdap_pb2.JSCard.Link(
                            resource=rdap_pb2.JSCard.Resource(
                                uri="https://as207960.net/contact"
                            ),
                            kind=rdap_pb2.JSCard.Link.Kind.Contact,
                        )
                    }
                ),
            )]
        ))

        entities = {}

        def add_entity(obj, role):
            obj_id = str(obj.id)
            if obj_id not in entities:
                entities[obj_id] = {
                    "contact": obj,
                    "roles": [role]
                }
            else:
                entities[obj_id]["roles"].append(role)

        if domain_obj.registrant_contact:
            add_entity(domain_obj.registrant_contact, rdap_pb2.RoleRegistrant)

        if domain_obj.admin_contact:
            add_entity(domain_obj.admin_contact, rdap_pb2.RoleAdministrative)

        if domain_obj.billing_contact:
            add_entity(domain_obj.billing_contact, rdap_pb2.RoleBilling)

        if domain_obj.tech_contact:
            add_entity(domain_obj.tech_contact, rdap_pb2.RoleTechnical)

        for c in entities.values():
            resp_data.entities.append(self.contact_to_card(c["roles"], c["contact"]))

        if domain_data.creation_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(domain_data.creation_date)
            resp_data.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventRegistration,
                date=date
            ))
        if domain_data.expiry_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(domain_data.expiry_date + zone_data.expiry_offset)
            resp_data.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventExpiration,
                date=date
            ))
        if domain_data.paid_until_date:
            date = google.protobuf.timestamp_pb2.Timestamp()
            date.FromDatetime(domain_data.paid_until_date)
            resp_data.events.append(rdap_pb2.Event(
                action=rdap_pb2.EventRegistrarExpiration,
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
            domain__iexact=request.query,
            former_domain=False
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
        except Exception as e:
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=500,
                title="Internal Server Error"
            ))
            return response

        response = rdap_pb2.DomainResponse(success=resp_data)
        return response

    def DomainSearch(self, request: rdap_pb2.DomainSearchRequest, context):
        if request.WhichOneof("query") == "name":
            regex = re.sub(r"[-[\]{}()+?.,\\^$|#\s]", r'\\\g<0>', request.name).replace("*", ".*")
            domain_objs = models.DomainRegistration.objects.filter(
                domain__iregex=f"^{regex}$",
                former_domain=False
            )
        else:
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=400,
                title="Not provided",
                description="Service not provided"
            ))
            return response

        try:
            with concurrent.futures.ThreadPoolExecutor() as p:
                resp_data = list(p.map(self.domain_to_proto, domain_objs))
        except grpc.RpcError as e:
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=500,
                title="Internal Server Error",
                description=e.details()
            ))
            return response
        except Exception as e:
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=500,
                title="Internal Server Error"
            ))
            return response

        response = rdap_pb2.DomainSearchResponse(success=rdap_pb2.DomainSearchResponse.Domains(
            data=resp_data
        ))
        return response

    def EntityLookup(self, request: rdap_pb2.LookupRequest, context):
        try:
            contact_obj = models.Contact.objects.filter(
                handle__iexact=request.query
            ).first()  # type: models.Contact
        except django.core.exceptions.ValidationError:
            contact_obj = None

        if not contact_obj:
            registry_contact_obj = models.ContactRegistry.objects.filter(
                registry_contact_id__iexact=request.query
            ).first()  # type: models.ContactRegistry
            if not registry_contact_obj:
                response = rdap_pb2.EntityResponse(error=rdap_pb2.ErrorResponse(
                    error_code=404,
                    title="Not found",
                    description="No such entity"
                ))
                return response
            contact_obj = registry_contact_obj.contact

        try:
            entity = self.contact_to_card([], contact_obj)
        except Exception as e:
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=500,
                title="Internal Server Error"
            ))
            return response

        response = rdap_pb2.EntityResponse(success=entity)
        return response

    def EntitySearch(self, request: rdap_pb2.EntitySearchRequest, context):
        entities = {}

        if request.WhichOneof("query") == "name":
            regex = re.sub(r"[-[\]{}()+?.,\\^$|#\s]", r'\\\g<0>', request.name).replace("*", ".*")
            contact_objs = models.Contact.objects.filter(
                Q(local_address__name__iregex=f"^{regex}$", local_address__disclose_name=True) |
                Q(int_address__name__iregex=f"^{regex}$", int_address__disclose_name=True) |
                Q(local_address__organisation__iregex=f"^{regex}$", local_address__disclose_organisation=True) |
                Q(int_address__name__iregex=f"^{regex}$", int_address__disclose_organisation=True) |
                Q(trading_name__iregex=f"^{regex}$")
            )
            for contact_obj in contact_objs:
                if contact_obj.id not in entities:
                    entities[contact_obj.id] = contact_obj
        elif request.WhichOneof("query") == "handle":
            regex = re.sub(r"[-[\]{}()+?.,\\^$|#\s]", r'\\\g<0>', request.handle).replace("*", ".*")
            try:
                contact_objs = list(models.Contact.objects.filter(
                    handle__iregex=f"^{regex}$"
                ))
                for contact_obj in contact_objs:
                    if contact_obj.id not in entities:
                        entities[contact_obj.id] = contact_obj
            except django.core.exceptions.ValidationError:
                pass
            registry_contact_objs = models.ContactRegistry.objects.filter(
                registry_contact_id__iregex=f"^{regex}$"
            )
            for registry_contact_obj in registry_contact_objs:
                if registry_contact_obj.contact_id not in entities:
                    entities[registry_contact_obj.contact_id] = registry_contact_obj.contact
        else:
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=400,
                title="Not provided",
                description="Service not provided"
            ))
            return response

        resp_data = []
        try:
            for contact_obj in entities.values():
                resp_data.append(self.contact_to_card([], contact_obj))
        except Exception as e:
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=500,
                title="Internal Server Error"
            ))
            return response

        response = rdap_pb2.EntitySearchResponse(success=rdap_pb2.EntitySearchResponse.Entities(
            data=resp_data
        ))
        return response

    def NameServerLookup(self, request: rdap_pb2.LookupRequest, context):
        name_server_obj = models.NameServer.objects.filter(
            name_server__iexact=request.query
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
        except Exception as e:
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=500,
                title="Internal Server Error"
            ))
            return response

        response = rdap_pb2.NameServerResponse(success=resp_data)
        return response

    def NameServerSearch(self, request: rdap_pb2.NameServerSearchRequest, context):
        if request.WhichOneof("query") == "name":
            regex = re.sub(r"[-[\]{}()+?.,\\^$|#\s]", r'\\\g<0>', request.name).replace("*", ".*")
            name_server_objs = models.NameServer.objects.filter(
                name_server__iregex=f"^{regex}$"
            )
        else:
            response = rdap_pb2.NameServerResponse(error=rdap_pb2.ErrorResponse(
                error_code=400,
                title="Not provided",
                description="Service not provided"
            ))
            return response

        try:
            with concurrent.futures.ThreadPoolExecutor() as p:
                resp_data = list(p.map(self.name_server_to_proto, name_server_objs))
        except grpc.RpcError as e:
            response = rdap_pb2.NameServerResponse(error=rdap_pb2.ErrorResponse(
                error_code=500,
                title="Internal Server Error",
                description=e.details()
            ))
            return response
        except Exception as e:
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
            response = rdap_pb2.DomainResponse(error=rdap_pb2.ErrorResponse(
                error_code=500,
                title="Internal Server Error"
            ))
            return response

        response = rdap_pb2.NameServerSearchResponse(success=rdap_pb2.NameServerSearchResponse.NameServers(
            data=resp_data
        ))
        return response
