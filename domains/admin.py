from django.contrib import admin
from . import models, hooks

admin.site.register(models.DomainRegistration)
admin.site.register(models.ContactAddress)
admin.site.register(models.Contact)
admin.site.register(models.ContactRegistry)
admin.site.register(models.NameServer)
admin.site.register(models.DomainRegistrationOrder)
admin.site.register(models.DomainRenewOrder)
admin.site.register(models.DomainRestoreOrder)
admin.site.register(models.DomainTransferOrder)
