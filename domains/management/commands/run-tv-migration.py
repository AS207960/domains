from django.core.management.base import BaseCommand
from domains import models, apps, zone_info


class Command(BaseCommand):
    help = 'Handles migration of .TV from thin to thick registry'

    def handle(self, *args, **options):
        domains = models.DomainRegistration.objects.filter(former_domain=False, domain__endswith='.tv')

        for domain in domains:
            domain_data = apps.epp_client.get_domain(domain.domain)

            domain_info = zone_info.get_domain_info(domain.domain)[0]

            if not domain_data.can_update:
                print(f"Domain {domain_data.name} is not updatable, skipping")

            new_auth_info = models.make_secret()
            domain_data.set_auth_info(new_auth_info)
            domain.auth_info = new_auth_info
            domain.save()

            contact_id = domain.registrant_contact.get_registry_id(domain_data.registry_name, domain_info)
            domain_data.set_registrant(contact_id.registry_contact_id)

            if domain.admin_contact:
                contact_id = domain.admin_contact.get_registry_id(domain_data.registry_name, domain_info)
                domain_data.set_contact("admin", contact_id.registry_contact_id)

            if domain.tech_contact:
                contact_id = domain.admin_contact.get_registry_id(domain_data.registry_name, domain_info)
                domain_data.set_contact("tech", contact_id.registry_contact_id)

            if domain.billing_contact:
                contact_id = domain.admin_contact.get_registry_id(domain_data.registry_name, domain_info)
                domain_data.set_contact("billing", contact_id.registry_contact_id)

            print(f"Updated domain {domain_data.name}")
