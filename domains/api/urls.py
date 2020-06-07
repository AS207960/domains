from django.urls import include, path
from rest_framework import routers, schemas
from . import views

router = routers.DefaultRouter()
router.register(r'contact_addresses', views.ContactAddressViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'domains', views.Domain, basename='domain')
router.register(r'name_servers', views.NameServer, basename='nameserver')


urlpatterns = [
    path('', include(router.urls)),
    path('openapi', schemas.get_schema_view(
        title="AS207960 Domains",
        version="0.0.1"
    ), name='openapi-schema'),
]
