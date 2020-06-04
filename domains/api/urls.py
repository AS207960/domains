from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'contact_addresses', views.ContactAddressViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'domains', views.DomainSet, basename='domain')
router.register(r'name_servers', views.NameServer, basename='nameserver')


urlpatterns = [
    path('', include(router.urls)),
]
