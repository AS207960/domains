from django.db.models.signals import post_save, pre_delete
from django.db import InternalError
from django.dispatch import receiver
from concurrent.futures import ThreadPoolExecutor
from . import models, apps
import grpc


def update_contact(contact_obj: models.ContactRegistry):
    instance = contact_obj.contact
    try:
        contact = apps.epp_client.get_contact(contact_obj.registry_contact_id, contact_obj.registry_id)
        contact.update(
            local_address=instance.local_address.as_api_obj(),
            int_address=instance.int_address.as_api_obj() if instance.int_address else None,
            phone=apps.epp_api.Phone(
                number=f"+{instance.phone.country_code}.{instance.phone.national_number}",
                ext=instance.phone_ext
            ) if instance.phone else None,
            fax=apps.epp_api.Phone(
                number=f"+{instance.fax.country_code}.{instance.fax.national_number}",
                ext=instance.fax_ext
            ) if instance.fax else None,
            email=instance.email,
            entity_type=instance.entity_type,
            trading_name=instance.trading_name,
            company_number=instance.company_number,
            auth_info=None
        )
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        raise InternalError(error)


@receiver(post_save, sender=models.Contact)
def contact_save(instance: models.Contact, **kwargs):
    with ThreadPoolExecutor() as executor:
        for i in instance.contactregistry_set.all():
            executor.submit(update_contact, i)


@receiver(post_save, sender=models.ContactAddress)
def contact_address_save(instance: models.ContactAddress, **kwargs):
    with ThreadPoolExecutor() as executor:
        for contact in instance.local_contacts.all():
            for i in contact.contactregistry_set.all():
                executor.submit(update_contact, i)

        for contact in instance.int_contacts.all():
            for i in contact.contactregistry_set.all():
                executor.submit(update_contact, i)
