from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import dns.query
import dns.resolver
import dns.rdataclass
import dns.rdatatype
import dns.exception
import dns.rdtypes
import base64
import grpc
from domains import models, zone_info, apps


resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = [settings.RESOLVER_ADDR]
resolver.port = settings.RESOLVER_PORT

ALGORITHMS = (5, 7, 8, 10, 13, 14, 15, 16, 0)
DIGEST_TYPES = (1, 2, 4, 0)


def mail_update(user, domain, add_cds, rem_cds, is_ds):
    context = {
        "name": user.first_name,
        "domain": domain,
        "add_cds": add_cds,
        "rem_cds": rem_cds,
        "is_ds": is_ds
    }
    html_content = render_to_string("domains_email/cds_update.html", context)
    txt_content = render_to_string("domains_email/cds_update.txt", context)

    email = EmailMultiAlternatives(
        subject='Domain CDS update',
        body=txt_content,
        to=[user.email],
        bcc=['q@as207960.net']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def mail_disabled(user, domain):
    context = {
        "name": user.first_name,
        "domain": domain,
    }
    html_content = render_to_string("domains_email/cds_disable.html", context)
    txt_content = render_to_string("domains_email/cds_disable.html", context)

    email = EmailMultiAlternatives(
        subject='Domain DNSSEC disabled',
        body=txt_content,
        to=[user.email],
        bcc=['q@as207960.net']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


class Command(BaseCommand):
    help = 'Runs updates to DS/DNSKEY based on CDS/CDNSKEY'

    def handle(self, *args, **options):
        domains = models.DomainRegistration.objects.filter(deleted=False)

        for domain in domains:
            domain_info, sld = zone_info.get_domain_info(domain.domain)

            if not domain_info:
                print(f"Can't renew {domain.domain}: unknown zone")
                continue

            # TODO: Use nameservers from EPP rather than hard coded for testing
            try:
                domain_data = apps.epp_client.get_domain(domain.domain)
            except grpc.RpcError as rpc_error:
                print(f"Can't get data for {domain.domain}: {rpc_error.details()}")
                continue

            name_servers = list(map(lambda ns: ns.host_obj if ns.host_obj else ns.host_name, domain_data.name_servers))
            # name_servers = ["ns1.as207960.net", "ns2.as207960.net"]
            domain_name = dns.name.from_text(domain.domain)

            if not name_servers:
                continue

            user = domain.get_user()

            try:
                original_ds_msg = resolver.resolve(
                    domain_name, dns.rdatatype.DS, raise_on_no_answer=False, tcp=True
                ).response
            except dns.resolver.NXDOMAIN:
                print(f"Getting DS of {domain_name} returned NXDOMAIN")
                continue
            except dns.resolver.NoNameservers:
                print(f"Getting DS of {domain} no nameservers")
                return
            except dns.exception.Timeout:
                print(f"Getting DS of {domain_name} timed out")
                continue

            if original_ds_msg.rcode() != 0:
                print(f"Getting DS of {domain.domain} returned error")
                continue

            original_ds = original_ds_msg.get_rrset(
                dns.message.ANSWER, domain_name, dns.rdataclass.IN, dns.rdatatype.DS
            )
            cds_type = dns.rdatatype.CDS if domain_info.ds_data_supported else dns.rdatatype.CDNSKEY

            def validate_message(msg, dnskey_set, ds_set, covers=dns.rdatatype.DNSKEY, exact=True):
                data_set = msg.get_rrset(
                    dns.message.ANSWER, domain_name, dns.rdataclass.IN, covers
                )
                rrsig = msg.get_rrset(
                    dns.message.ANSWER, domain_name, dns.rdataclass.IN, dns.rdatatype.RRSIG, covers
                )
                found_dnskeys = dns.rdataset.Rdataset(dns.rdataclass.IN, dns.rdatatype.DNSKEY)
                for cds in ds_set:
                    possible_dnskeys = filter(lambda rr: dns.dnssec.key_id(rr) == cds.key_tag, dnskey_set)
                    for key in possible_dnskeys:
                        ds = dns.dnssec.make_ds(domain_name, key, cds.digest_type)
                        if ds.digest == cds.digest:
                            found_dnskeys.add(key)

                if not found_dnskeys:
                    raise dns.dnssec.ValidationFailure("no suitable DNSKEYs")

                dns.dnssec.validate(data_set, rrsig, {
                    domain_name: dnskey_set if not exact else found_dnskeys
                })

            def get_cds():
                cds, dnskey = {}, {}

                for ns in name_servers:
                    try:
                        ns_ip = resolver.resolve(ns, dns.rdatatype.AAAA, raise_on_no_answer=True, tcp=True)
                    except dns.resolver.NXDOMAIN:
                        print(f"Getting IP of {ns} returned NXDOMAIN")
                        return
                    except dns.resolver.NoAnswer:
                        print(f"Getting IP of {ns} returned no answer")
                        return
                    except dns.resolver.NoNameservers:
                        print(f"Getting IP of {ns} no nameservers")
                        return
                    except dns.exception.Timeout:
                        print(f"Getting IP of {ns} timed out")
                        return
                    ns_rrs = list(filter(lambda rr: isinstance(rr, dns.rdtypes.IN.AAAA.AAAA), ns_ip))
                    for ns_rr in ns_rrs:
                        ns_ip = ns_rr.address
                        if ns_ip in cds:
                            continue

                        try:
                            msg = dns.message.make_query(domain_name, cds_type)
                            msg.use_edns(ednsflags=dns.flags.DO)
                            dns_cds = dns.query.tcp(msg, ns_ip, timeout=15)
                        except dns.exception.Timeout:
                            print(f"{domain.domain} timed out")
                            return

                        if dns_cds.rcode() == dns.rcode.NXDOMAIN:
                            print(f"{domain.domain} returned NXDOMAIN")
                            return

                        try:
                            msg = dns.message.make_query(domain_name, dns.rdatatype.DNSKEY)
                            msg.use_edns(ednsflags=dns.flags.DO)
                            dns_dnskey = dns.query.tcp(msg, ns_ip, timeout=15)
                        except dns.exception.Timeout:
                            print(f"{domain.domain} timed out")
                            return

                        cds_rrs = dns_cds.get_rrset(
                            dns.message.ANSWER, domain_name, dns.rdataclass.IN, cds_type
                        )
                        dnskey_rrs = dns_dnskey.get_rrset(
                            dns.message.ANSWER, domain_name, dns.rdataclass.IN, dns.rdatatype.DNSKEY
                        )

                        try:
                            if original_ds:
                                validate_message(dns_dnskey, dnskey_rrs, original_ds)
                                validate_message(dns_cds, dnskey_rrs, original_ds, cds_type, False)
                        except dns.dnssec.ValidationFailure:
                            print(f"{domain.domain} failed validation with current DS set")
                            return

                        cds[ns_ip] = cds_rrs
                        dnskey[ns_ip] = dns_dnskey

                return cds, dnskey

            results = get_cds()
            if results is None:
                continue
            cds_results, dnskey_results = results

            if not cds_results:
                continue

            cds_values = list(cds_results.values())
            if cds_values.count(cds_values[0]) != len(cds_values):
                print(f"{domain.domain} has differing CDS records")
                continue

            cds_data_set = cds_values[0]
            current_cds_set = []
            if domain_data.sec_dns:
                if domain_info.ds_data_supported:
                    current_cds_set = domain_data.sec_dns.ds_data
                else:
                    current_cds_set = domain_data.sec_dns.key_data

            if len(cds_data_set) == 1 and cds_data_set[0].algorithm == 0:
                try:
                    apps.epp_client.stub.DomainUpdate(apps.epp_api.domain_pb2.DomainUpdateRequest(
                        name=domain.domain,
                        sec_dns=apps.epp_api.domain_pb2.UpdateSecDNSData(
                            remove_all=True
                        )
                    ))
                except grpc.RpcError as rpc_error:
                    print(f"Can't remove DNSSEC for {domain.domain}: {rpc_error.details()}")
                    continue

                mail_disabled(user, domain)
            else:
                if not domain_info.ds_data_supported:
                    cds_set = list(map(lambda d: dns.dnssec.make_ds(domain_name, d, "SHA256"), cds_data_set))
                else:
                    cds_set = cds_data_set

                try:
                    for res in dnskey_results.values():
                        dnskey = res.get_rrset(dns.message.ANSWER, domain_name, dns.rdataclass.IN, dns.rdatatype.DNSKEY)
                        validate_message(res, dnskey, cds_set)
                except dns.dnssec.ValidationFailure:
                    print(f"{domain.domain} failed validation with presented CDS set")
                    continue

                for cds in cds_set:
                    if cds.algorithm not in ALGORITHMS or cds.digest_type not in DIGEST_TYPES:
                        print(f"{domain.domain} CDS uses invalid algorithm/digest")
                        continue

                if domain_info.ds_data_supported:
                    cds_data_set = list(map(lambda r: apps.epp_api.SecDNSDSData(
                        key_tag=r.key_tag,
                        algorithm=r.algorithm,
                        digest_type=r.digest_type,
                        digest=r.digest.hex(),
                        key_data=None
                    ), cds_data_set))
                else:
                    cds_data_set = list(map(lambda r: apps.epp_api.SecDNSKeyData(
                        flags=r.flags,
                        protocol=r.protocol,
                        algorithm=r.algorithm,
                        public_key=base64.b64encode(r.key).decode(),
                    ), cds_data_set))

                rem_cds_set = list(filter(lambda d: d not in cds_data_set, current_cds_set))
                add_cds_set = list(filter(lambda d: d not in current_cds_set, cds_data_set))

                if rem_cds_set or add_cds_set:
                    req = apps.epp_api.domain_pb2.DomainUpdateRequest(
                        name=domain.domain,
                    )
                    if domain_info.ds_data_supported:
                        if rem_cds_set:
                            req.sec_dns.remove_ds_data.data.extend(map(lambda d: d.to_pb(), rem_cds_set))
                        if add_cds_set:
                            req.sec_dns.add_ds_data.data.extend(map(lambda d: d.to_pb(), add_cds_set))
                    else:
                        if rem_cds_set:
                            req.sec_dns.remove_key_data.data.extend(map(lambda d: d.to_pb(), rem_cds_set))
                        if add_cds_set:
                            req.sec_dns.add_key_data.data.extend(map(lambda d: d.to_pb(), add_cds_set))

                    print(req)
                    # try:
                    #     apps.epp_client.stub.DomainUpdate(req)
                    # except grpc.RpcError as rpc_error:
                    #     print(f"Can't update DNSSEC for {domain.domain}: {rpc_error.details()}")
                    #     continue
                    #
                    # mail_update(user, domain, add_cds_set, rem_cds_set, domain_info.ds_data_supported)
