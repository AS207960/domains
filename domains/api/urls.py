from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'contact_addresses', views.ContactAddressViewSet, basename='contactaddress')
router.register(r'contacts', views.ContactViewSet, basename='contact')
router.register(r'domains', views.DomainSet, basename='domain')


urlpatterns = [
    path('', include(router.urls)),
]
