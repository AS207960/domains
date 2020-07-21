from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models, tasks


@receiver(post_save, sender=models.Contact)
def contact_save(instance: models.Contact, **kwargs):
    for i in instance.contactregistry_set.all():
        tasks.update_contact.delay(i.id)


@receiver(post_save, sender=models.ContactAddress)
def contact_address_save(instance: models.ContactAddress, **kwargs):
    for contact in instance.local_contacts.all():
        for i in contact.contactregistry_set.all():
            tasks.update_contact.delay(i.id)

    for contact in instance.int_contacts.all():
        for i in contact.contactregistry_set.all():
            tasks.update_contact.delay(i.id)
