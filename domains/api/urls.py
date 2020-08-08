from django.urls import include, path
from rest_framework import routers, schemas
from . import views

router = routers.DefaultRouter()
router.register(r'contact_addresses', views.ContactAddressViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'domains', views.Domain, basename='domain')
router.register(r'domain_registration_orders', views.DomainRegistrationOrderViewSet, basename='domainregistrationorder')
router.register(r'domain_transfer_orders', views.DomainTransferOrderViewSet, basename='domaintransferorder')
router.register(r'domain_renew_orders', views.DomainRenewOrderViewSet, basename='domainreneworder')
router.register(r'domain_restore_orders', views.DomainRestoreOrderViewSet, basename='domainrestoreorder')
router.register(r'name_servers', views.NameServer, basename='nameserver')
router.register(r'internal/balance', views.EPPBalanceViewSet, basename='balance')
router.register(r'internal/domains', views.UserDomainsViewSet, basename='user-domains')


urlpatterns = [
    path('', include(router.urls)),
    path('openapi', schemas.get_schema_view(
        title="Glauca Domains",
        version="0.0.1"
    ), name='openapi-schema'),
]
