from django.urls import include, path
from rest_framework import routers, schemas
from . import views, admin_views

router = routers.DefaultRouter()
router.register(r'contact_addresses', views.ContactAddressViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'domains', views.Domain, basename='domain')
router.register(r'domain_registration_orders', views.DomainRegistrationOrderViewSet, basename='domainregistrationorder')
router.register(r'domain_transfer_orders', views.DomainTransferOrderViewSet, basename='domaintransferorder')
router.register(r'domain_renew_orders', views.DomainRenewOrderViewSet, basename='domainreneworder')
router.register(r'domain_restore_orders', views.DomainRestoreOrderViewSet, basename='domainrestoreorder')
router.register(r'name_servers', views.NameServer, basename='nameserver')
router.register(r'internal/balance', admin_views.EPPBalanceViewSet, basename='balance')
router.register(r'internal/domains', admin_views.UserDomainsViewSet, basename='user-domains')
router.register(r'internal/domain_locking', admin_views.DomainLockingViewSet)
router.register(r'internal/orders/pending', admin_views.PendingOrderViewSet)
router.register(r'internal/orders/in_progress', admin_views.InProgressOrderViewSet)
router.register(r'internal/pending_locks', admin_views.PendingLockViewSet),
router.register(r'internal/registration_order', admin_views.DomainRegistrationAdminOrderViewSet)
router.register(r'internal/transfer_order', admin_views.DomainTransferAdminOrderViewSet)
router.register(r'internal/renew_order', admin_views.DomainRenewAdminOrderViewSet)
router.register(r'internal/auto_renew_order', admin_views.DomainAutoRenewAdminOrderViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('openapi', schemas.get_schema_view(
        title="Glauca Domains",
        version="0.0.1"
    ), name='openapi-schema'),
]
