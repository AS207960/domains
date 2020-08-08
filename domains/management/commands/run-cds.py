from django.core.management.base import BaseCommand
from django.conf import settings
import dns.query
import dns.resolver
import dns.rdataclass
import dns.rdatatype
import dns.exception
import dns.rdtypes
from domains import models, zone_info


resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = [settings.RESOLVER_ADDR]
resolver.port = settings.RESOLVER_PORT


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
            # try:
            #     domain_data = apps.epp_client.get_domain(domain.domain)
            # except grpc.RpcError as rpc_error:
            #     print(f"Can't get data for {domain.domain}: {rpc_error.details()}")
            #     continue
            #
            # name_servers = list(map(lambda ns: ns.host_obj if ns.host_obj else ns.host_name, domain_data.name_servers))
            name_servers = ["ns1.as207960.net", "ns2.as207960.net"]
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
            except dns.exception.Timeout:
                print(f"Getting DS of {domain_name} timed out")
                continue

            if original_ds_msg.rcode() != 0:
                print(f"Getting DS of {domain.domain} returned error")
                continue

            original_ds = original_ds_msg.get_rrset(
                dns.message.ANSWER, domain_name, dns.rdataclass.IN, dns.rdatatype.DS
            )

            def validate_message(msg, dnskey_set, ds_set, covers=dns.rdatatype.DNSKEY):
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
                    domain_name: dnskey_set
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
                    except dns.exception.Timeout:
                        print(f"Getting IP of {ns} timed out")
                        return
                    ns_rrs = list(filter(lambda rr: isinstance(rr, dns.rdtypes.IN.AAAA.AAAA), ns_ip))
                    for ns_rr in ns_rrs:
                        ns_ip = ns_rr.address
                        if ns_ip in cds:
                            continue

                        try:
                            msg = dns.message.make_query(domain_name, dns.rdatatype.CDS)
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
                            dns.message.ANSWER, domain_name, dns.rdataclass.IN, dns.rdatatype.CDS
                        )
                        dnskey_rrs = dns_dnskey.get_rrset(
                            dns.message.ANSWER, domain_name, dns.rdataclass.IN, dns.rdatatype.DNSKEY
                        )

                        try:
                            if original_ds:
                                validate_message(dns_cds, dnskey_rrs, original_ds, dns.rdatatype.CDS)
                                validate_message(dns_dnskey, dnskey_rrs, original_ds)
                        except dns.dnssec.ValidationFailure as e:
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

            cds_set = cds_values[0]

            try:
                for res in dnskey_results.values():
                    dnskey = res.get_rrset(dns.message.ANSWER, domain_name, dns.rdataclass.IN, dns.rdatatype.DNSKEY)
                    validate_message(res, dnskey, cds_set)
            except dns.dnssec.ValidationFailure:
                print(f"{domain.domain} failed validation with presented CDS set")
                continue

            print(cds_set)
