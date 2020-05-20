from django.urls import path
from . import views

urlpatterns = [
    path('', views.domains, name='domains'),
    path('prices/', views.domain_prices, name='domain_prices'),
    path('domains/new/', views.domain_search, name='domain_search'),
    path('domains/register/<str:domain_name>/', views.domain_register, name='domain_register'),
    path('domains/<uuid:domain_id>/', views.domain, name='domain'),
    path('domains/<uuid:domain_id>/delete/', views.delete_domain, name='delete_domain'),
    path('domains/<uuid:domain_id>/restore/', views.restore_domain, name='restore_domain'),
    path('domains/<uuid:domain_id>/renew/', views.renew_domain, name='renew_domain'),
    path('domains/<uuid:domain_id>/update_contact/', views.update_domain_contact, name='update_domain_contact'),
    path('domains/<uuid:domain_id>/add_host_obj/', views.add_domain_host_obj, name='add_domain_host_obj'),
    path('domains/<uuid:domain_id>/add_host_addr/', views.add_domain_host_addr, name='add_domain_host_addr'),
    path('domains/<uuid:domain_id>/add_ds_data/', views.add_domain_ds_data, name='add_domain_ds_data'),
    path('domains/<uuid:domain_id>/add_dnskey_data/', views.add_domain_dnskey_data, name='add_domain_dnskey_data'),
    path('domains/<uuid:domain_id>/delete_ds_data/', views.delete_domain_ds_data, name='delete_domain_ds_data'),
    path('domains/<uuid:domain_id>/delete_dnskey_data/', views.delete_domain_dnskey_data, name='delete_domain_dnskey_data'),
    path('domains/<uuid:domain_id>/delete_sec_dns/', views.delete_domain_sec_dns, name='delete_domain_sec_dns'),
    path('domains/<uuid:domain_id>/del_host_obj/<str:host_name>/', views.delete_domain_host_obj, name='delete_domain_host_obj'),
    path('domains/<uuid:domain_id>/block_transfer/', views.domain_block_transfer, name='domain_block_transfer'),
    path('domains/<uuid:domain_id>/del_block_transfer/', views.domain_del_block_transfer, name='domain_del_block_transfer'),
    path('hosts/', views.hosts, name='hosts'),
    path('hosts/<uuid:host_id>/', views.host, name='host'),
    path('hosts/<uuid:host_id>/delete/', views.host_delete, name='host_delete'),
    path('hosts/<str:registry_name>/create/<str:host>/', views.host_create, name='host_create'),
    path('contacts/', views.contacts, name='contacts'),
    path('contacts/new/', views.new_contact, name='new_contact'),
    path('contacts/<uuid:contact_id>/', views.edit_contact, name='edit_contact'),
    path('contacts/<uuid:contact_id>/delete/', views.delete_contact, name='delete_contact'),
    path('addresses/', views.addresses, name='addresses'),
    path('addresses/new/', views.new_address, name='new_address'),
    path('addresses/<uuid:address_id>/delete/', views.delete_address, name='delete_address'),
    path('addresses/<uuid:address_id>/', views.edit_address, name='edit_address'),
]
