from django.apps import AppConfig
from django.conf import settings
import grpc
import django_keycloak_auth.clients
from . import epp_api


def get_call_creds(_context, callback):
    token = django_keycloak_auth.clients.get_access_token()
    metadata = (('authorization', 'Bearer {}'.format(token)),)
    callback(metadata, None)


epp_creds = grpc.metadata_call_credentials(get_call_creds)
epp_client = epp_api.EPPClient(settings.EPP_PROXY_ADDR, settings.EPP_PROXY_CA, epp_creds)


class DomainsConfig(AppConfig):
    name = 'domains'
