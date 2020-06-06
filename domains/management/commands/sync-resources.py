from django.core.management.base import BaseCommand
from django.db.models.signals import post_save

from ... import models, hooks


class Command(BaseCommand):
    help = "Synchronises model instances to keylcloak resources"
    requires_migrations_checks = True

    def handle(self, *args, **options):
        post_save.disconnect(hooks.contact_address_save, sender=models.ContactAddress)
        post_save.disconnect(hooks.contact_save, sender=models.Contact)

        for address in models.ContactAddress.objects.all():
            address.save()
        for contact in models.Contact.objects.all():
            contact.save(skip_update_date=True)
        for ns in models.NameServer.objects.all():
            ns.save()
        for domain in models.DomainRegistration.objects.all():
            domain.save()
