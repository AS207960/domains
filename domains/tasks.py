from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.shortcuts import reverse
from . import models, zone_info, apps
from .views import billing, gchat_bot, emails
import time
import grpc

logger = get_task_logger(__name__)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def update_contact(contact_registry_id):
    contact_obj = models.ContactRegistry.objects.get(id=contact_registry_id)  # type: models.ContactRegistry
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
        logger.warn(f"Failed to update contact: {error}")


def handle_charge(order: models.AbstractOrder, username, descriptor, charge_id, return_uri) -> bool:
    if order.state == order.STATE_PENDING:
        logger.info(f"{descriptor} not yet ready to charge")
        return False
    if order.state == order.STATE_FAILED:
        logger.info(f"{descriptor} failed")
        return True
    elif order.state in (order.STATE_COMPLETED, order.STATE_PENDING_APPROVAL):
        logger.info(f"{descriptor} already complete")
        return True

    if not order.charge_state_id:
        charge_state = billing.charge_account(
            username,
            order.price,
            descriptor,
            charge_id,
            off_session=order.off_session,
            return_uri=return_uri
        )
        order.charge_state_id = charge_state.charge_state_id
        order.save()
        if not charge_state.success:
            if charge_state.redirect_uri:
                order.state = order.STATE_NEEDS_PAYMENT
                order.redirect_uri = charge_state.redirect_uri
            else:
                order.state = order.STATE_FAILED
                order.last_error = charge_state.error
                order.redirect_uri = None
                order.save()
                logger.warn(f"Payment for {descriptor} failed with error {charge_state.error}")
                return True
        else:
            order.state = order.STATE_PROCESSING
            order.redirect_uri = None

        order.save()
    else:
        charge_state = billing.get_charge_state(order.charge_state_id)
        if charge_state.status == "pending":
            order.state = order.STATE_NEEDS_PAYMENT
            order.redirect_uri = charge_state.redirect_uri
        elif charge_state.status == "completed":
            order.state = order.STATE_PROCESSING
            order.redirect_uri = None
        elif charge_state.status == "failed":
            order.state = order.STATE_FAILED
            order.last_error = charge_state.last_error
            order.redirect_uri = None
            order.save()
            logger.warn(f"Payment for {descriptor} failed with error {charge_state.last_error}")
            return True

    order.save()
    return False


@shared_task(
    bind=True, autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None,
    default_retry_delay=3
)
def process_domain_registration(self, registration_order_id):
    domain_registration_order = \
        models.DomainRegistrationOrder.objects.get(id=registration_order_id)  # type: models.DomainRegistrationOrder
    user = domain_registration_order.get_user()

    period = apps.epp_api.Period(
        value=domain_registration_order.period_value,
        unit=domain_registration_order.period_unit
    )

    zone, sld = zone_info.get_domain_info(domain_registration_order.domain)
    if not zone:
        domain_registration_order.state = domain_registration_order.STATE_FAILED
        domain_registration_order.last_error = "You don't have permission to perform this action"
        logger.error(f"Failed to get zone info for {domain_registration_order.domain}")
        billing.reverse_charge(f"dm_{domain_registration_order.domain_id}")
        return

    try:
        available, _, registry_id = apps.epp_client.check_domain(domain_registration_order.domain)
    except grpc.RpcError as rpc_error:
        logger.warn(f"Failed to check availability of {domain_registration_order.domain}: {rpc_error.details()}")
        raise rpc_error

    if not available:
        domain_registration_order.state = domain_registration_order.STATE_FAILED
        domain_registration_order.last_error = "Domain no longer available to purchase."
        domain_registration_order.save()
        billing.reverse_charge(f"dm_{domain_registration_order.domain_id}")
        return

    should_return = handle_charge(
        domain_registration_order,
        user.username,
        f"{domain_registration_order.domain} domain registration",
        f"dm_{domain_registration_order.domain_id}",
        return_uri=settings.EXTERNAL_URL_BASE + reverse(
            'domain_register_confirm', args=(domain_registration_order.id, )
        )
    )

    if should_return:
        return

    if domain_registration_order.state == domain_registration_order.STATE_PROCESSING:
        if zone.direct_registration_supported:
            for host in ('ns1.as207960.net', 'ns2.as207960.net'):
                try:
                    host_available, _ = apps.epp_client.check_host(host, registry_id)
                except grpc.RpcError as rpc_error:
                    logger.error(f"Failed to setup hosts for {domain_registration_order.domain}: {rpc_error.details()}")
                    raise rpc_error

                if host_available:
                    try:
                        apps.epp_client.create_host(host, [], registry_id)
                    except grpc.RpcError as rpc_error:
                        logger.error(f"Failed to setup hosts for {domain_registration_order.domain}: "
                                     f"{rpc_error.details()}")
                        raise rpc_error

            try:
                contact_objs = []
                if zone.admin_supported and domain_registration_order.admin_contact:
                    contact_objs.append(apps.epp_api.DomainContact(
                        contact_type="admin",
                        contact_id=domain_registration_order.admin_contact.get_registry_id(
                            registry_id).registry_contact_id
                    ))
                if zone.billing_supported and domain_registration_order.billing_contact:
                    contact_objs.append(apps.epp_api.DomainContact(
                        contact_type="billing",
                        contact_id=domain_registration_order.billing_contact.get_registry_id(
                            registry_id).registry_contact_id
                    ))
                if zone.tech_supported and domain_registration_order.tech_contact:
                    contact_objs.append(apps.epp_api.DomainContact(
                        contact_type="tech",
                        contact_id=domain_registration_order.tech_contact.get_registry_id(
                            registry_id).registry_contact_id
                    ))

                pending, _, _, _ = apps.epp_client.create_domain(
                    domain=domain_registration_order.domain,
                    period=period,
                    registrant=domain_registration_order.registrant_contact.get_registry_id(
                        registry_id).registry_contact_id
                    if zone.registrant_supported else 'NONE',
                    contacts=contact_objs,
                    name_servers=[apps.epp_api.DomainNameServer(
                        host_obj='ns1.as207960.net',
                        host_name=None,
                        address=[]
                    ), apps.epp_api.DomainNameServer(
                        host_obj='ns2.as207960.net',
                        host_name=None,
                        address=[]
                    )],
                    auth_info=domain_registration_order.auth_info,
                )
            except grpc.RpcError as rpc_error:
                domain_registration_order.state = domain_registration_order.STATE_FAILED
                domain_registration_order.last_error = rpc_error.details()
                domain_registration_order.save()
                billing.reverse_charge(f"dm_{domain_registration_order.domain_id}")
                logger.error(f"Failed to register {domain_registration_order.domain}: {rpc_error.details()}")
                return
        else:
            pending = True

        if pending:
            domain_registration_order.state = domain_registration_order.STATE_PENDING_APPROVAL
            domain_registration_order.save()
            if not zone.direct_registration_supported:
                gchat_bot.request_registration.delay(domain_registration_order.id, registry_id, str(period))
                logger.info(f"{domain_registration_order.domain} registration successfully requested")
            else:
                gchat_bot.notify_registration.delay(domain_registration_order.id, str(period))
                logger.info(f"{domain_registration_order.domain} registration successfully submitted")
        else:
            process_domain_registration_complete.delay(domain_registration_order.id)
            logger.info(f"{domain_registration_order.domain} registered successfully")

        return

    raise self.retry(countdown=3)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def process_domain_registration_complete(registration_order_id):
    domain_registration_order = \
        models.DomainRegistrationOrder.objects.get(id=registration_order_id)  # type: models.DomainRegistrationOrder

    period = apps.epp_api.Period(
        value=domain_registration_order.period_value,
        unit=domain_registration_order.period_unit
    )

    emails.mail_registered.delay(domain_registration_order.id)

    domain_obj = models.DomainRegistration(
        id=domain_registration_order.domain_id,
        domain=domain_registration_order.domain,
        user=domain_registration_order.get_user(),
        auth_info=domain_registration_order.auth_info,
        registrant_contact=domain_registration_order.registrant_contact,
        admin_contact=domain_registration_order.admin_contact,
        tech_contact=domain_registration_order.tech_contact,
        billing_contact=domain_registration_order.billing_contact
    )
    domain_obj.save()

    domain_registration_order.domain_obj = domain_obj
    domain_registration_order.state = domain_registration_order.STATE_COMPLETED
    domain_registration_order.redirect_uri = None
    domain_registration_order.last_error = None
    domain_registration_order.save()
    gchat_bot.notify_registration.delay(domain_registration_order.id, str(period))


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def process_domain_registration_failed(registration_order_id):
    domain_registration_order = \
        models.DomainRegistrationOrder.objects.get(id=registration_order_id)  # type: models.DomainRegistrationOrder

    emails.mail_register_failed.delay(domain_registration_order.id)

    billing.reverse_charge(f"dm_{domain_registration_order.domain_id}")
    domain_registration_order.state = domain_registration_order.STATE_FAILED
    domain_registration_order.save()


@shared_task(
    bind=True, autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None,
    default_retry_delay=3
)
def process_domain_renewal(self, renewal_order_id):
    domain_renewal_order = \
        models.DomainRenewOrder.objects.get(id=renewal_order_id)  # type: models.DomainRenewOrder
    user = domain_renewal_order.get_user()

    period = apps.epp_api.Period(
        value=domain_renewal_order.period_value,
        unit=domain_renewal_order.period_unit
    )

    zone, sld = zone_info.get_domain_info(domain_renewal_order.domain)
    if not zone:
        domain_renewal_order.state = domain_renewal_order.STATE_FAILED
        domain_renewal_order.last_error = "You don't have permission to perform this action"
        logger.error(f"Failed to get zone info for {domain_renewal_order.domain}")
        billing.reverse_charge(f"dm_renew_{domain_renewal_order.domain_obj.id}")
        return

    try:
        domain_data = apps.epp_client.get_domain(domain_renewal_order.domain)
    except grpc.RpcError as rpc_error:
        logger.warn(f"Failed to load data of {domain_renewal_order.domain}: {rpc_error.details()}")
        raise rpc_error

    should_return = handle_charge(
        domain_renewal_order,
        user.username,
        f"{domain_renewal_order.domain} domain renewal",
        f"dm_renew_{domain_renewal_order.domain_obj.id}",
        return_uri=settings.EXTERNAL_URL_BASE + reverse(
            'renew_domain_confirm', args=(domain_renewal_order.id, )
        )
    )

    if should_return:
        return

    if domain_renewal_order.state == domain_renewal_order.STATE_PROCESSING:
        try:
            _pending, _new_expiry, registry_id = apps.epp_client.renew_domain(
                domain_renewal_order.domain, period, domain_data.expiry_date
            )
        except grpc.RpcError as rpc_error:
            domain_renewal_order.state = domain_renewal_order.STATE_FAILED
            domain_renewal_order.last_error = rpc_error.details()
            domain_renewal_order.save()
            billing.reverse_charge(f"dm_renew_{domain_renewal_order.domain_obj.id}")
            logger.error(f"Failed to renew {domain_renewal_order.domain}: {rpc_error.details()}")
            return

        gchat_bot.notify_renew.delay(domain_renewal_order.domain_obj.id, registry_id, str(period))

        domain_renewal_order.state = domain_renewal_order.STATE_COMPLETED
        domain_renewal_order.redirect_uri = None
        domain_renewal_order.last_error = None
        domain_renewal_order.save()

        logger.info(f"{domain_renewal_order.domain} successfully renewed")

        return

    raise self.retry(countdown=3)


@shared_task(
    bind=True, autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None,
    default_retry_delay=3
)
def process_domain_restore(self, restore_order_id):
    domain_restore_order = \
        models.DomainRestoreOrder.objects.get(id=restore_order_id)  # type: models.DomainRestoreOrder
    user = domain_restore_order.get_user()

    zone, sld = zone_info.get_domain_info(domain_restore_order.domain)
    if not zone:
        domain_restore_order.state = domain_restore_order.STATE_FAILED
        domain_restore_order.last_error = "You don't have permission to perform this action"
        logger.error(f"Failed to get zone info for {domain_restore_order.domain}")
        billing.reverse_charge(f"dm_restore_{domain_restore_order.domain_obj.id}")
        return

    should_return = handle_charge(
        domain_restore_order,
        user.username,
        f"{domain_restore_order.domain} domain restore",
        f"dm_restore_{domain_restore_order.domain_obj.id}",
        return_uri=settings.EXTERNAL_URL_BASE + reverse(
            'restore_domain_confirm', args=(domain_restore_order.id, )
        )
    )

    if should_return:
        return

    if domain_restore_order.state == domain_restore_order.STATE_PROCESSING:
        if zone.direct_restore_supported:
            try:
                pending, registry_id = apps.epp_client.restore_domain(domain_restore_order.domain)
                domain_restore_order.domain_obj.deleted = pending
                domain_restore_order.domain_obj.pending = pending
                domain_restore_order.domain_obj.save()
                gchat_bot.notify_restore.delay(domain_restore_order.id)
            except grpc.RpcError as rpc_error:
                domain_restore_order.state = domain_restore_order.STATE_FAILED
                domain_restore_order.last_error = rpc_error.details()
                domain_restore_order.save()
                billing.reverse_charge(f"dm_restore_{domain_restore_order.domain_obj.id}")
                logger.error(f"Failed to restore {domain_restore_order.domain}: {rpc_error.details()}")
                return

        else:
            gchat_bot.request_restore.delay(domain_restore_order.id)
            pending = True

        if pending:
            domain_restore_order.state = domain_restore_order.STATE_PENDING_APPROVAL
        else:
            domain_restore_order.state = domain_restore_order.STATE_COMPLETED

        domain_restore_order.redirect_uri = None
        domain_restore_order.last_error = None
        domain_restore_order.save()

        logger.info(f"{domain_restore_order.domain} successfully restored")

        return

    raise self.retry(countdown=3)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def process_domain_restore_complete(restore_order_id):
    domain_restore_order = \
        models.DomainRestoreOrder.objects.get(id=restore_order_id)  # type: models.DomainRestoreOrder

    emails.mail_restored.delay(domain_restore_order.id)

    domain_restore_order.domain_obj.deleted = False
    domain_restore_order.domain_obj.pending = False
    domain_restore_order.domain_obj.save()

    domain_restore_order.state = domain_restore_order.STATE_COMPLETED
    domain_restore_order.redirect_uri = None
    domain_restore_order.last_error = None
    domain_restore_order.save()
    gchat_bot.notify_restore.delay(domain_restore_order.id)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def process_domain_restore_failed(restore_order_id):
    domain_restore_order = \
        models.DomainRestoreOrder.objects.get(id=restore_order_id)  # type: models.DomainRestoreOrder

    emails.mail_restore_failed.delay(domain_restore_order.id)

    billing.reverse_charge(f"dm_restore_{domain_restore_order.domain_obj.id}")
    domain_restore_order.state = domain_restore_order.STATE_FAILED
    domain_restore_order.save()


@shared_task(
    bind=True, autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None,
    default_retry_delay=3
)
def process_domain_transfer(self, transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder
    user = domain_transfer_order.get_user()

    zone, sld = zone_info.get_domain_info(domain_transfer_order.domain)
    if not zone:
        domain_transfer_order.state = domain_transfer_order.STATE_FAILED
        domain_transfer_order.last_error = "You don't have permission to perform this action"
        logger.error(f"Failed to get zone info for {domain_transfer_order.domain}")
        billing.reverse_charge(f"dm_transfer_{domain_transfer_order.domain_id}")
        return

    should_return = handle_charge(
        domain_transfer_order,
        user.username,
        f"{domain_transfer_order.domain} domain transfer",
        f"dm_{domain_transfer_order.domain_id}",
        return_uri=settings.EXTERNAL_URL_BASE + reverse(
            'domain_transfer_confirm', args=(domain_transfer_order.id, )
        )
    )

    if should_return:
        return

    if domain_transfer_order.state == domain_transfer_order.STATE_PROCESSING:
        if zone.direct_transfer_supported:
            try:
                transfer_data = apps.epp_client.transfer_request_domain(
                    domain_transfer_order.domain,
                    domain_transfer_order.auth_code
                )
            except grpc.RpcError as rpc_error:
                billing.reverse_charge(f"dm_transfer_{domain_transfer_order.domain_id}")
                domain_transfer_order.state = domain_transfer_order.STATE_FAILED
                domain_transfer_order.last_error = rpc_error.details()
                logger.error(f"Failed to transfer {domain_transfer_order.domain}: {rpc_error.details()}")
                return
            else:
                if transfer_data.status == 5:
                    gchat_bot.notify_transfer.delay(domain_transfer_order.id, transfer_data.registry_name)
                    logger.info(f"{domain_transfer_order.domain} successfully transferred")
                    return
                else:
                    gchat_bot.notify_transfer_pending.delay(domain_transfer_order.id, transfer_data.registry_name)

                    domain_transfer_order.state = domain_transfer_order.STATE_PENDING_APPROVAL
                    domain_transfer_order.redirect_uri = None
                    domain_transfer_order.last_error = None
                    domain_transfer_order.save()

                    logger.info(f"{domain_transfer_order.domain} transfer successfully submitted")
                    return
        else:
            try:
                _, _, registry_id = apps.epp_client.check_domain(domain_transfer_order.domain)
            except grpc.RpcError as rpc_error:
                billing.reverse_charge(f"dm_transfer_{domain_transfer_order.domain_id}")
                domain_transfer_order.state = domain_transfer_order.STATE_FAILED
                domain_transfer_order.last_error = rpc_error.details()
                domain_transfer_order.save()
                logger.error(f"Failed to transfer {domain_transfer_order.domain}: {rpc_error.details()}")
                return

            gchat_bot.request_transfer.delay(domain_transfer_order.id, registry_id)

            domain_transfer_order.state = domain_transfer_order.STATE_PENDING_APPROVAL
            domain_transfer_order.redirect_uri = None
            domain_transfer_order.last_error = None
            domain_transfer_order.save()

            logger.info(f"{domain_transfer_order.domain} transfer successfully requested")
            return

    raise self.retry(countdown=3)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def process_domain_transfer_contacts(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder

    zone, sld = zone_info.get_domain_info(domain_transfer_order.domain)
    if not zone:
        logger.error(f"Failed to get zone info for {domain_transfer_order.domain}")
        return

    domain_data = apps.epp_client.get_domain(domain_transfer_order.domain)
    registrant_id = process_domain_transfer.registrant_contact.get_registry_id(domain_data.registry_name)
    domain_data.set_registrant(registrant_id.registry_contact_id)
    if domain_transfer_order.tech_contact and zone.tech_supported:
        tech_contact_id = domain_transfer_order.tech_contact.get_registry_id(domain_data.registry_name)
        domain_data.set_tech(tech_contact_id.registry_contact_id)
    if domain_transfer_order.admin_contact and zone.admin_supported:
        admin_contact_id = domain_transfer_order.admin_contact.get_registry_id(domain_data.registry_name)
        domain_data.set_admin(admin_contact_id.registry_contact_id)
    if domain_transfer_order.billing_contact and zone.billing_supported:
        billing_contact_id = domain_transfer_order.billing_contact.get_registry_id(domain_data.registry_name)
        domain_data.set_billing(billing_contact_id.registry_contact_id)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def process_domain_transfer_complete(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder

    emails.mail_transferred.delay(domain_transfer_order.id)

    domain_obj = models.DomainRegistration(
        id=domain_transfer_order.domain_id,
        domain=domain_transfer_order.domain,
        user=domain_transfer_order.get_user(),
        auth_info=domain_transfer_order.auth_code,
        registrant_contact=domain_transfer_order.registrant_contact,
        admin_contact=domain_transfer_order.admin_contact,
        tech_contact=domain_transfer_order.tech_contact,
        billing_contact=domain_transfer_order.billing_contact
    )
    domain_obj.save()
    process_domain_transfer_contacts.delay(domain_transfer_order.id)

    domain_transfer_order.state = domain_transfer_order.STATE_COMPLETED
    domain_transfer_order.domain_obj = domain_obj
    domain_transfer_order.redirect_uri = None
    domain_transfer_order.last_error = None
    domain_transfer_order.save()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def process_domain_transfer_failed(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder

    emails.mail_transfer_failed.delay(domain_transfer_order.id)

    billing.reverse_charge(f"dm_transfer_{domain_transfer_order.domain_id}")
    domain_transfer_order.state = domain_transfer_order.STATE_FAILED
    domain_transfer_order.save()
