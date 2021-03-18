from django.contrib import admin
from . import models, hooks

admin.site.register(models.NameServer)


@admin.register(models.ContactAddress)
class ContactAddressRegistrationAdmin(admin.ModelAdmin):
    list_display = ('description', 'name', 'organisation', 'disclose_name', 'disclose_organisation', 'disclose_address')


class ContactRegistryInline(admin.TabularInline):
    model = models.ContactRegistry


@admin.register(models.Contact)
class ContactRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'description', 'local_address', 'int_address', 'entity_type', 'disclose_phone', 'disclose_fax', 'disclose_email'
    )
    inlines = [ContactRegistryInline]


@admin.register(models.DomainRegistration)
class DomainRegistrationAdmin(admin.ModelAdmin):
    list_display = ('domain', 'deleted', 'last_billed', 'last_renew_notify')


@admin.register(models.DomainRegistrationOrder)
class DomainRegistrationOrderAdmin(admin.ModelAdmin):
    list_display = ('domain', 'period_unit', 'period_value', 'state', 'price', 'off_session')


@admin.register(models.DomainRenewOrder)
class DomainRenewOrderAdmin(admin.ModelAdmin):
    list_display = ('domain', 'period_unit', 'period_value', 'state', 'price', 'off_session')


@admin.register(models.DomainRestoreOrder)
class DomainRestoreOrderAdmin(admin.ModelAdmin):
    list_display = ('domain', 'state', 'price', 'off_session')


@admin.register(models.DomainTransferOrder)
class DomainTransferOrderAdmin(admin.ModelAdmin):
    list_display = ('domain', 'state', 'price', 'off_session')


admin.site.register(models.DomainPendingChange)
admin.site.register(models.DomainPendingChangeHostName)
admin.site.register(models.DomainPendingChangeDSData)
admin.site.register(models.DomainPendingChangeKeyData)
