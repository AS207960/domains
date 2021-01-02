from django.apps import AppConfig
from django.conf import settings
import grpc
import ipaddress
import as207960_utils.rpc
import django_keycloak_auth.clients
from . import epp_api


def get_call_creds(_context, callback):
    token = django_keycloak_auth.clients.get_access_token()
    metadata = (('authorization', 'Bearer {}'.format(token)),)
    callback(metadata, None)


def get_ip(request):
    net64_net = ipaddress.IPv6Network("2a0d:1a40:7900:6::/80")
    addr = ipaddress.ip_address(request.META['REMOTE_ADDR'])
    if isinstance(addr, ipaddress.IPv6Address):
        if addr.ipv4_mapped:
            addr = addr.ipv4_mapped
        if addr in net64_net:

            addr = ipaddress.IPv4Address(addr._ip & 0xFFFFFFFF)
    return addr


epp_creds = grpc.metadata_call_credentials(get_call_creds)
epp_client = epp_api.EPPClient(settings.EPP_PROXY_ADDR, settings.EPP_PROXY_CA, epp_creds)
rpc_client = as207960_utils.rpc.RpcClient()


class DomainsConfig(AppConfig):
    name = 'domains'
