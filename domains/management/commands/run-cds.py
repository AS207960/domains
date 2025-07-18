from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
import dns.query
import dns.resolver
import dns.rdataclass
import dns.rdatatype
import dns.exception
import dns.rdtypes
import dns.dnssec
import base64
import grpc
import socket
from domains import models, zone_info, apps
from domains.views import emails


resolver_addr = socket.getaddrinfo(settings.RESOLVER_ADDR, None)[0][4][0]
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = [socket.getaddrinfo(settings.RESOLVER_ADDR, None)[0][4][0]]
resolver.port = settings.RESOLVER_PORT


def mail_update(user, domain, add_cds, rem_cds, is_ds, is_own: bool = False):
    emails.send_email(user, {
        "subject": "Domain CDS update",
        "content": render_to_string("domains_email/cds_update.html", {
            "domain": domain,
            "add_cds": add_cds,
            "rem_cds": rem_cds,
            "is_ds": is_ds,
            "is_own_ns": is_own,
        })
    })


def mail_disabled(user, domain, is_own: bool = False):
    emails.send_email(user, {
        "subject": "Domain CDS disabled",
        "content": render_to_string("domains_email/cds_disable.html", {
            "domain": domain,
            "is_own_ns": is_own
        })
    })


class Command(BaseCommand):
    help = 'Runs updates to DS/DNSKEY based on CDS/CDNSKEY'

    def handle(self, *args, **options):
        domains = models.DomainRegistration.objects.filter(deleted=False, former_domain=False)

        for domain in domains:
            domain_info, sld = zone_info.get_domain_info(domain.domain, registry_id=domain.registry_id)

            if not domain_info:
                print(f"Can't run CDS on {domain.domain}: unknown zone")
                continue

            if domain_info.supports_cds:
                print(f"Ignoring CDS on {domain.domain}: handled by registry")
                continue

            try:
                domain_data = apps.epp_client.get_domain(
                    domain.domain, registry_id=domain.registry_id
                )
            except grpc.RpcError as rpc_error:
                print(f"Can't get data for {domain.domain}: {rpc_error.details()}")
                continue

            name_servers = list(map(lambda ns: ns.host_obj if ns.host_obj else ns.host_name, domain_data.name_servers))
            domain_name = dns.name.from_text(domain.domain)

            if not name_servers:
                continue

            is_own_ns = all([ns.lower().endswith(".as207960.net") for ns in name_servers])

            user = domain.get_user()

            try:
                original_ds_msg = resolver.resolve(
                    domain_name, dns.rdatatype.DS, raise_on_no_answer=False
                ).response
            except dns.resolver.NXDOMAIN:
                print(f"Getting DS of {domain.domain} returned NXDOMAIN")
                continue
            except dns.resolver.NoNameservers:
                print(f"Getting DS of {domain.domain} no nameservers")
                continue
            except dns.exception.Timeout:
                print(f"Getting DS of {domain.domain} timed out")
                continue
            except dns.exception.DNSException as e:
                print(f"Getting DS of {domain.domain}: {e}")
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
                if not data_set:
                    raise dns.dnssec.ValidationFailure("no suitable records")
                if not rrsig:
                    raise dns.dnssec.ValidationFailure("no suitable RRSIGs")

                found_dnskeys = dns.rdataset.Rdataset(dns.rdataclass.IN, dns.rdatatype.DNSKEY)
                for cds in ds_set:
                    possible_dnskeys = filter(lambda rr: dns.dnssec.key_id(rr) == cds.key_tag, dnskey_set)
                    for key in possible_dnskeys:
                        ds = dns.dnssec.make_ds(domain_name, key, cds.digest_type)
                        if ds.digest == cds.digest:
                            found_dnskeys.add(key)

                if not found_dnskeys or not data_set:
                    raise dns.dnssec.ValidationFailure("no suitable DNSKEYs")

                dns.dnssec.validate(data_set, rrsig, {
                    domain_name: dnskey_set if not exact else found_dnskeys
                })

            def get_cds():
                cds, dnskey = {}, {}

                for ns in name_servers:
                    try:
                        ns_ips = socket.getaddrinfo(ns, None, socket.AF_INET6)
                    except socket.gaierror as e:
                        print(f"Getting IP of {ns} for domain {domain.domain}: {e.args[1]}")
                        return

                    for ns_ip in ns_ips:
                        ns_ip = ns_ip[4][0]
                        if ns_ip in cds:
                            continue

                        try:
                            msg = dns.message.make_query(domain_name, cds_type)
                            msg.use_edns(ednsflags=dns.flags.DO)
                            dns_cds = dns.query.tcp(msg, ns_ip, timeout=15)
                        except dns.exception.Timeout:
                            print(f"NS {ns} (IP {ns_ip}) for domain {domain.domain} timed out")
                            return
                        except dns.exception.DNSException as e:
                            print(f"NS {ns} (IP {ns_ip}) for domain {domain.domain}: {e}")
                            return
                        except OSError as e:
                            print(f"Can't access NS {ns} (IP {ns_ip}) for domain {domain.domain}: {e}")
                            return

                        if dns_cds.rcode() == dns.rcode.NXDOMAIN:
                            print(f"NS {ns} (IP {ns_ip}) for domain {domain.domain} returned NXDOMAIN")
                            return

                        try:
                            msg = dns.message.make_query(domain_name, dns.rdatatype.DNSKEY)
                            msg.use_edns(ednsflags=dns.flags.DO)
                            dns_dnskey = dns.query.tcp(msg, ns_ip, timeout=15)
                        except dns.exception.Timeout:
                            print(f"NS {ns} (IP {ns_ip}) for domain {domain.domain} timed out")
                            return
                        except dns.exception.DNSException as e:
                            print(f"NS {ns} (IP {ns_ip}) for domain {domain.domain}: {e}")
                            return
                        except OSError as e:
                            print(f"Can't access NS {ns} (IP {ns_ip}) for domain {domain.domain}: {e}")
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

                        if cds_rrs:
                            cds[ns_ip] = cds_rrs
                        if dnskey_rrs:
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

            if not original_ds:
                ds_boot_data = {}
                for ns in name_servers:
                    ds_boot_domain_name = dns.name.from_text(f"_dsboot.{domain.domain}._signal.{ns}")
                    try:
                        ds_boot_msg = dns.message.make_query(ds_boot_domain_name, cds_type, want_dnssec=True)
                    except dns.resolver.NXDOMAIN:
                        print(f"Getting {ds_boot_domain_name} returned NXDOMAIN")
                        continue
                    except dns.resolver.NoNameservers:
                        print(f"Getting {ds_boot_domain_name} no nameservers")
                        continue
                    except dns.exception.Timeout:
                        print(f"Getting {ds_boot_domain_name} timed out")
                        continue
                    except dns.exception.DNSException as e:
                        print(f"Getting {ds_boot_domain_name}: {e}")
                        continue

                    if not bool(ds_boot_msg.flags & ds_boot_msg.flags.AD):
                        continue

                    ds_boot_rrs = ds_boot_msg.get_rrset(
                        dns.message.ANSWER, ds_boot_domain_name, dns.rdataclass.IN, cds_type
                    )

                    if not ds_boot_rrs:
                        continue

                    ds_boot_data[ns] = ds_boot_rrs

                if ds_boot_data:
                    ds_boot_values = list(ds_boot_data.values())
                    if ds_boot_values.count(ds_boot_values[0]) != len(ds_boot_values):
                        print(f"{domain.domain} has differing _dsboot records between NSes")
                        continue

                    if ds_boot_values.count(cds_data_set) != len(ds_boot_values):
                        print(f"{domain.domain} has differing _dsboot records between NSes and CDS")
                        continue

            if len(cds_data_set) == 1 and cds_data_set[0].algorithm == 0:
                if domain_data.sec_dns:
                    try:
                        apps.epp_client.stub.DomainUpdate(apps.epp_api.domain_pb2.DomainUpdateRequest(
                            name=domain.domain,
                            sec_dns=apps.epp_api.domain_pb2.UpdateSecDNSData(
                                all=True
                            )
                        ))
                    except grpc.RpcError as rpc_error:
                        print(f"Can't remove DNSSEC for {domain.domain}: {rpc_error.details()}")
                        continue

                    mail_disabled(user, domain, is_own_ns)
            else:
                current_cds_set = []
                if domain_data.sec_dns:
                    if domain_info.ds_data_supported:
                        current_cds_set = list(map(lambda r: apps.epp_api.SecDNSDSData(
                            key_tag=r.key_tag,
                            algorithm=r.algorithm,
                            digest_type=r.digest_type,
                            digest=r.digest.upper(),
                            key_data=None
                        ), domain_data.sec_dns.ds_data))
                    else:
                        current_cds_set = domain_data.sec_dns.key_data

                supported_algorithms = domain_info.supported_dnssec_algorithms
                cds_data_set = list(filter(lambda r: r.algorithm == 0 or r.algorithm in supported_algorithms, cds_data_set))

                if len(cds_data_set) == 0:
                    print(f"{domain.domain} CDS uses invalid algorithm/digest")
                    continue

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

                if domain_info.ds_data_supported:
                    cds_data_set = list(map(lambda r: apps.epp_api.SecDNSDSData(
                        key_tag=int(r.key_tag),
                        algorithm=int(r.algorithm),
                        digest_type=int(r.digest_type),
                        digest=r.digest.hex().upper(),
                        key_data=None
                    ), cds_data_set))
                else:
                    cds_data_set = list(map(lambda r: apps.epp_api.SecDNSKeyData(
                        flags=int(r.flags),
                        protocol=r.protocol,
                        algorithm=int(r.algorithm),
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
                            req.sec_dns.rem_ds_data.data.extend(map(lambda d: d.to_pb(), rem_cds_set))
                        if add_cds_set:
                            req.sec_dns.add_ds_data.data.extend(map(lambda d: d.to_pb(), add_cds_set))
                    else:
                        if rem_cds_set:
                            req.sec_dns.rem_key_data.data.extend(map(lambda d: d.to_pb(), rem_cds_set))
                        if add_cds_set:
                            req.sec_dns.add_key_data.data.extend(map(lambda d: d.to_pb(), add_cds_set))

                    try:
                        apps.epp_client.stub.DomainUpdate(req)
                    except grpc.RpcError as rpc_error:
                        print(f"Can't update DNSSEC for {domain.domain}: {rpc_error.details()}")
                        continue

                    mail_update(user, domain, add_cds_set, rem_cds_set, domain_info.ds_data_supported, is_own_ns)
