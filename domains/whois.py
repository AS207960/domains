import grpc
import ipaddress
from django.db.models import Q
from .whois_proto import whois_pb2
from .whois_proto import whois_pb2_grpc
from . import models
from . import apps


def grpc_hook(server):
    whois_pb2_grpc.add_WHOISServicer_to_server(WHOISServicer(), server)


class WHOISServicer(whois_pb2_grpc.WHOISServicer):
    def insert_contact(self, contact_type, contact, elements):
        elements.append(whois_pb2.WHOISReply.Element(
            key=f"{contact_type} Name",
            value=contact.local_address.name if contact.local_address.disclose_name else "REDACTED",
        ))
        if contact.local_address.organisation:
            elements.append(whois_pb2.WHOISReply.Element(
                key=f"{contact_type} Organisation",
                value=contact.local_address.organisation if contact.local_address.disclose_organisation else "REDACTED",
            ))
        if contact.local_address.disclose_address:
            elements.append(whois_pb2.WHOISReply.Element(
                key=f"{contact_type} Street",
                value=contact.local_address.street_1,
            ))
            if contact.local_address.street_2:
                elements.append(whois_pb2.WHOISReply.Element(
                    key=f"{contact_type} Street",
                    value=contact.local_address.street_2,
                ))
            if contact.local_address.street_3:
                elements.append(whois_pb2.WHOISReply.Element(
                    key=f"{contact_type} Street",
                    value=contact.local_address.street_3,
                ))
        else:
            elements.append(whois_pb2.WHOISReply.Element(
                key=f"{contact_type} Street",
                value="REDACTED",
            ))
        elements.append(whois_pb2.WHOISReply.Element(
            key=f"{contact_type} City",
            value=contact.local_address.city,
        ))
        if contact.local_address.province:
            elements.append(whois_pb2.WHOISReply.Element(
                key=f"{contact_type} Province",
                value=contact.local_address.province,
            ))
        elements.append(whois_pb2.WHOISReply.Element(
            key=f"{contact_type} Country",
            value=contact.local_address.country_code.code,
        ))
        elements.append(whois_pb2.WHOISReply.Element(
            key=f"{contact_type} Phone",
            value=f"+{contact.phone.country_code}.{contact.phone.national_number}" if contact.disclose_phone else "REDACTED",
        ))
        if contact.phone_ext and contact.disclose_phone:
            elements.append(whois_pb2.WHOISReply.Element(
                key=f"{contact_type} Phone Ext",
                value=contact.phone_ext,
            ))
        if contact.fax:
            elements.append(whois_pb2.WHOISReply.Element(
                key=f"{contact_type} Fax",
                value=f"+{contact.fax.country_code}.{contact.fax.national_number}" if contact.disclose_phone else "REDACTED",
            ))
            if contact.fax_ext and contact.disclose_fax:
                elements.append(whois_pb2.WHOISReply.Element(
                    key=f"{contact_type} Fax Ext",
                    value=contact.fax_ext,
                ))
        elements.append(whois_pb2.WHOISReply.Element(
            key=f"{contact_type} Email",
            value=contact.email if contact.disclose_email else "abuse@as207960.net",
        ))
        elements.append(whois_pb2.WHOISReply.Element(
            key=f"{contact_type} Entity Type",
            value=next(
                map(lambda t: t[1], filter(lambda t: t[0] == contact.entity_type, contact.ENTITY_TYPES)),
                None
            ) or "Unknown",
        ))
        if contact.trading_name:
            elements.append(whois_pb2.WHOISReply.Element(
                key=f"{contact_type} Trading Name",
                value=contact.trading_name,
            ))
        if contact.company_number:
            elements.append(whois_pb2.WHOISReply.Element(
                key=f"{contact_type} Company Number",
                value=contact.company_number,
            ))
        if contact.created_date:
            elements.append(whois_pb2.WHOISReply.Element(
                key=f"{contact_type} Created Date",
                value=contact.created_date.isoformat(),
            ))
        if contact.updated_date:
            elements.append(whois_pb2.WHOISReply.Element(
                key=f"{contact_type} Last Updated Date",
                value=contact.updated_date.isoformat(),
            ))

    def WHOISQuery(self, request, context):
        query_str = request.query
        objects = []
        
        domain_objs = models.DomainRegistration.objects.filter(
            domain__search=query_str
        )
        for domain_obj in domain_objs:
            try:
                domain_data = apps.epp_client.get_domain(domain_obj.domain)
            except grpc.RpcError as e:
                context.set_code(e.code())
                context.set_details(e.details())
                return

            elements = [whois_pb2.WHOISReply.Element(
                key="Domain Name",
                value=domain_obj.domain
            ), whois_pb2.WHOISReply.Element(
                key="Registry Domain ID",
                value=domain_data.registry_id
            ), whois_pb2.WHOISReply.Element(
                key="Registrar",
                value="AS207960 Cyfyngedig"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar Abuse Contact Email",
                value="abuse@as207960.net"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar Abuse Contact Phone",
                value="+44.2920102455"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar WHOIS Server",
                value="whois.as207960.net"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar URL",
                value="https://as207960.net"
            )]

            if domain_data.last_updated_date:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="Updated Date",
                    value=domain_data.last_updated_date.isoformat()
                ))
            if domain_data.creation_date:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="Creation Date",
                    value=domain_data.creation_date.isoformat()
                ))
            if domain_data.expiry_date:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="Expiration Date",
                    value=domain_data.expiry_date.isoformat()
                ))

            for status in domain_data.statuses:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="Domain Status",
                    value=str(status)
                ))

            if domain_obj.registrant_contact:
                self.insert_contact("Registrant", domain_obj.registrant_contact, elements)
            if domain_obj.admin_contact:
                self.insert_contact("Admin", domain_obj.admin_contact, elements)
            if domain_obj.billing_contact:
                self.insert_contact("Billing", domain_obj.billing_contact, elements)
            if domain_obj.tech_contact:
                self.insert_contact("Tech", domain_obj.tech_contact, elements)

            for ns in domain_data.name_servers:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="Name Server",
                    value=ns.host_obj
                ))

            if domain_data.sec_dns:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="DNSSEC",
                    value="signedDelegation"
                ))
            else:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="DNSSEC",
                    value="unsigned"
                ))

            elements.append(whois_pb2.WHOISReply.Element(
                key="URL of the ICANN Whois Inaccuracy Complaint Form",
                value="http://wdprs.internic.net/"
            ))
            objects.append(whois_pb2.WHOISReply.Object(elements=elements))

        contact_objs = models.Contact.objects.filter(
            Q(local_address__name__search=query_str, local_address__disclose_name=True) |
            Q(int_address__name__search=query_str, int_address__disclose_name=True) |
            Q(local_address__organisation__search=query_str, local_address__disclose_organisation=True) |
            Q(int_address__name__search=query_str, int_address__disclose_organisation=True) |
            Q(trading_name__search=query_str) |
            Q(email__iexact=query_str, disclose_email=True)
        )
        for contact_obj in contact_objs:
            elements = [whois_pb2.WHOISReply.Element(
                key="Registrar",
                value="AS207960 Cyfyngedig"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar Abuse Contact Email",
                value="abuse@as207960.net"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar Abuse Contact Phone",
                value="+44.2920102455"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar WHOIS Server",
                value="whois.as207960.net"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar URL",
                value="https://as207960.net"
            )]
            self.insert_contact("Contact", contact_obj, elements)
            elements.append(whois_pb2.WHOISReply.Element(
                key="URL of the ICANN Whois Inaccuracy Complaint Form",
                value="http://wdprs.internic.net/"
            ))

            objects.append(whois_pb2.WHOISReply.Object(elements=elements))

        name_server_objs = models.NameServer.objects.filter(
            name_server__search=query_str
        )
        for name_server in name_server_objs:
            try:
                name_server_data = apps.epp_client.get_host(name_server.name_server, name_server.registry_id)
            except grpc.RpcError as e:
                context.set_code(e.code())
                context.set_details(e.details())
                return

            elements = [whois_pb2.WHOISReply.Element(
                key="Server Name",
                value=name_server_data.name
            ), whois_pb2.WHOISReply.Element(
                key="Registry Server ID",
                value=name_server_data.registry_id
            ), whois_pb2.WHOISReply.Element(
                key="Registrar",
                value="AS207960 Cyfyngedig"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar Abuse Contact Email",
                value="abuse@as207960.net"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar Abuse Contact Phone",
                value="+44.2920102455"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar WHOIS Server",
                value="whois.as207960.net"
            ), whois_pb2.WHOISReply.Element(
                key="Registrar URL",
                value="https://as207960.net"
            )]
            for status in name_server_data.statuses:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="Status",
                    value=str(status)
                ))
            for address in name_server_data.addresses:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="IP Address",
                    value=ipaddress.ip_address(address.address).compressed
                ))

            if name_server_data.last_updated_date:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="Updated Date",
                    value=name_server_data.last_updated_date.isoformat()
                ))
            if name_server_data.creation_date:
                elements.append(whois_pb2.WHOISReply.Element(
                    key="Creation Date",
                    value=name_server_data.creation_date.isoformat()
                ))

            objects.append(whois_pb2.WHOISReply.Object(elements=elements))

        if objects:
            response = whois_pb2.WHOISReply(objects=objects)
            return response
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('No objects not found')
