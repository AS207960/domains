from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.shortcuts import reverse
from . import models, zone_info, apps
from .views import billing, gchat_bot, emails
import grpc
from .proto import billing_pb2

logger = get_task_logger(__name__)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def update_contact(contact_registry_id):
    contact_obj = models.ContactRegistry.objects.filter(id=contact_registry_id).first()  # type: models.ContactRegistry
    if not contact_obj:
        return

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
            email=instance.get_public_email(),
            entity_type=instance.entity_type,
            trading_name=instance.trading_name,
            company_number=instance.company_number,
            disclosure=instance.get_disclosure(),
            auth_info=None
        )
    except grpc.RpcError as rpc_error:
        error = rpc_error.details()
        logger.warn(f"Failed to update contact: {error}")


# def handle_charge(
#         order: models.AbstractOrder,
#         username: str,
#         descriptor: str,
#         charge_id: str,
#         return_uri: str,
# ) -> bool:
#     if order.state == order.STATE_PENDING:
#         logger.info(f"{descriptor} not yet ready to charge")
#         return False
#     if order.state == order.STATE_FAILED:
#         logger.info(f"{descriptor} failed")
#         return True
#     elif order.state in (order.STATE_COMPLETED, order.STATE_PENDING_APPROVAL):
#         logger.info(f"{descriptor} already complete")
#         return True
#
#     if not order.charge_state_id:
#         charge_state = billing.charge_account(
#             username,
#             order.price,
#             descriptor,
#             charge_id,
#             off_session=order.off_session,
#             return_uri=return_uri
#         )
#         order.charge_state_id = charge_state.charge_state_id
#         order.save()
#         if not charge_state.success:
#             if charge_state.redirect_uri:
#                 order.state = order.STATE_NEEDS_PAYMENT
#                 order.redirect_uri = charge_state.redirect_uri
#             else:
#                 order.state = order.STATE_FAILED
#                 order.last_error = charge_state.error
#                 order.redirect_uri = None
#                 order.save()
#                 logger.warn(f"Payment for {descriptor} failed with error {charge_state.error}")
#                 return True
#         else:
#             if charge_state.immediate_completion:
#                 order.state = order.STATE_NEEDS_PAYMENT
#             else:
#                 order.state = order.STATE_NEEDS_PAYMENT
#             order.redirect_uri = None
#             order.save()
#     else:
#         charge_state = billing.get_charge_state(order.charge_state_id)
#         if charge_state.status == "pending":
#             order.state = order.STATE_NEEDS_PAYMENT
#             order.redirect_uri = charge_state.redirect_uri
#             order.save()
#         elif charge_state.status == "completed":
#             order.state = order.STATE_PROCESSING
#             order.redirect_uri = None
#             order.save()
#         elif charge_state.status == "failed":
#             order.state = order.STATE_FAILED
#             order.last_error = charge_state.last_error
#             order.redirect_uri = None
#             order.save()
#             logger.warn(f"Payment for {descriptor} failed with error {charge_state.last_error}")
#             return True
#
#     return False


def charge_order(
        order: models.AbstractOrder,
        username: str,
        descriptor: str,
        charge_id: str,
        return_uri: str,
        success_func,
        notif_queue=None,
) -> bool:
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
            return_uri=return_uri,
            notif_queue=notif_queue
        )
        order.charge_state_id = charge_state.charge_state_id
        order.save()
        if not charge_state.success:
            if charge_state.redirect_uri:
                order.state = order.STATE_NEEDS_PAYMENT
                order.redirect_uri = charge_state.redirect_uri
                order.save()
            else:
                order.state = order.STATE_FAILED
                order.last_error = charge_state.error
                order.redirect_uri = None
                order.save()
                logger.warn(f"Payment for {descriptor} failed with error {charge_state.error}")
        elif charge_state.immediate_completion:
            order.state = order.STATE_PROCESSING
            order.save()
            success_func.delay(order.id)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_registration_paid(registration_order_id):
    domain_registration_order = \
        models.DomainRegistrationOrder.objects.get(id=registration_order_id)  # type: models.DomainRegistrationOrder

    period = apps.epp_api.Period(
        value=domain_registration_order.period_value,
        unit=domain_registration_order.period_unit
    )
    zone, sld = zone_info.get_domain_info(domain_registration_order.domain)

    try:
        available, _, registry_id = apps.epp_client.check_domain(domain_registration_order.domain)
    except grpc.RpcError as rpc_error:
        logger.warn(f"Failed to check availability of {domain_registration_order.domain}: {rpc_error.details()}")
        raise rpc_error

    if not available:
        domain_registration_order.state = domain_registration_order.STATE_FAILED
        domain_registration_order.last_error = "Domain no longer available to purchase."
        domain_registration_order.save()
        billing.reverse_charge(domain_registration_order.id)
        return

    if zone.direct_registration_supported:
        if zone.pre_create_host_objects:
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
            billing.reverse_charge(domain_registration_order.id)
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


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_registration(registration_order_id):
    domain_registration_order = \
        models.DomainRegistrationOrder.objects.get(id=registration_order_id)  # type: models.DomainRegistrationOrder
    user = domain_registration_order.get_user()

    zone, _ = zone_info.get_domain_info(domain_registration_order.domain)
    if not zone:
        domain_registration_order.state = domain_registration_order.STATE_FAILED
        domain_registration_order.last_error = "You don't have permission to perform this action"
        logger.error(f"Failed to get zone info for {domain_registration_order.domain}")
        billing.reverse_charge(domain_registration_order.id)
        return

    charge_order(
        order=domain_registration_order,
        username=user.username,
        descriptor=f"{domain_registration_order.domain} domain registration",
        charge_id=domain_registration_order.id,
        return_uri=settings.EXTERNAL_URL_BASE + reverse(
            'domain_register_confirm', args=(domain_registration_order.id,)
        ),
        success_func=process_domain_registration_paid,
        notif_queue="domains_registration_billing_notif"
    )


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_registration_complete(registration_order_id):
    domain_registration_order = \
        models.DomainRegistrationOrder.objects.get(id=registration_order_id)  # type: models.DomainRegistrationOrder

    period = apps.epp_api.Period(
        value=domain_registration_order.period_value,
        unit=domain_registration_order.period_unit
    )
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

    emails.mail_registered.delay(domain_registration_order.id)
    gchat_bot.notify_registration.delay(domain_registration_order.id, str(period))


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_registration_failed(registration_order_id):
    domain_registration_order = \
        models.DomainRegistrationOrder.objects.get(id=registration_order_id)  # type: models.DomainRegistrationOrder

    billing.reverse_charge(domain_registration_order.id)
    domain_registration_order.state = domain_registration_order.STATE_FAILED
    domain_registration_order.save()

    emails.mail_register_failed.delay(domain_registration_order.id)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_renewal_paid(renew_order_id):
    domain_renewal_order = \
        models.DomainRenewOrder.objects.get(id=renew_order_id)  # type: models.DomainRenewOrder

    period = apps.epp_api.Period(
        value=domain_renewal_order.period_value,
        unit=domain_renewal_order.period_unit
    )

    try:
        domain_data = apps.epp_client.get_domain(domain_renewal_order.domain)
    except grpc.RpcError as rpc_error:
        logger.warn(f"Failed to load data of {domain_renewal_order.domain}: {rpc_error.details()}")
        raise rpc_error

    try:
        _pending, _new_expiry, registry_id = apps.epp_client.renew_domain(
            domain_renewal_order.domain, period, domain_data.expiry_date
        )
    except grpc.RpcError as rpc_error:
        domain_renewal_order.state = domain_renewal_order.STATE_FAILED
        domain_renewal_order.last_error = rpc_error.details()
        domain_renewal_order.save()
        billing.reverse_charge(domain_renewal_order.id)
        logger.error(f"Failed to renew {domain_renewal_order.domain}: {rpc_error.details()}")
        return

    gchat_bot.notify_renew.delay(domain_renewal_order.domain_obj.id, registry_id, str(period))

    domain_renewal_order.state = domain_renewal_order.STATE_COMPLETED
    domain_renewal_order.redirect_uri = None
    domain_renewal_order.last_error = None
    domain_renewal_order.save()

    logger.info(f"{domain_renewal_order.domain} successfully renewed")


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_renewal(renewal_order_id):
    domain_renewal_order = \
        models.DomainRenewOrder.objects.get(id=renewal_order_id)  # type: models.DomainRenewOrder
    user = domain_renewal_order.get_user()

    zone, sld = zone_info.get_domain_info(domain_renewal_order.domain)
    if not zone:
        domain_renewal_order.state = domain_renewal_order.STATE_FAILED
        domain_renewal_order.last_error = "You don't have permission to perform this action"
        logger.error(f"Failed to get zone info for {domain_renewal_order.domain}")
        billing.reverse_charge(domain_renewal_order.id)
        return

    charge_order(
        order=domain_renewal_order,
        username=user.username,
        descriptor=f"{domain_renewal_order.domain} domain renewal",
        charge_id=domain_renewal_order.id,
        return_uri=settings.EXTERNAL_URL_BASE + reverse(
            'renew_domain_confirm', args=(domain_renewal_order.id,)
        ),
        success_func=process_domain_renewal_paid,
        notif_queue="domains_renew_billing_notif"
    )


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_restore_paid(restore_order_id):
    domain_restore_order = \
        models.DomainRestoreOrder.objects.get(id=restore_order_id)  # type: models.DomainRestoreOrder

    zone, sld = zone_info.get_domain_info(domain_restore_order.domain)

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
            billing.reverse_charge(domain_restore_order.id)
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


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_restore(restore_order_id):
    domain_restore_order = \
        models.DomainRestoreOrder.objects.get(id=restore_order_id)  # type: models.DomainRestoreOrder
    user = domain_restore_order.get_user()

    zone, sld = zone_info.get_domain_info(domain_restore_order.domain)
    if not zone:
        domain_restore_order.state = domain_restore_order.STATE_FAILED
        domain_restore_order.last_error = "You don't have permission to perform this action"
        logger.error(f"Failed to get zone info for {domain_restore_order.domain}")
        billing.reverse_charge(domain_restore_order.id)
        return

    charge_order(
        order=domain_restore_order,
        username=user.username,
        descriptor=f"{domain_restore_order.domain} domain restore",
        charge_id=domain_restore_order.id,
        return_uri=settings.EXTERNAL_URL_BASE + reverse(
            'restore_domain_confirm', args=(domain_restore_order.id,)
        ),
        success_func=process_domain_restore_paid,
        notif_queue="domains_restore_billing_notif"
    )


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
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
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_restore_failed(restore_order_id):
    domain_restore_order = \
        models.DomainRestoreOrder.objects.get(id=restore_order_id)  # type: models.DomainRestoreOrder

    emails.mail_restore_failed.delay(domain_restore_order.id)

    billing.reverse_charge(domain_restore_order.id)
    domain_restore_order.state = domain_restore_order.STATE_FAILED
    domain_restore_order.save()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_transfer_paid(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder
    zone, sld = zone_info.get_domain_info(domain_transfer_order.domain)

    if zone.direct_transfer_supported:
        try:
            transfer_data = apps.epp_client.transfer_request_domain(
                domain_transfer_order.domain,
                domain_transfer_order.auth_code
            )
        except grpc.RpcError as rpc_error:
            billing.reverse_charge(domain_transfer_order.id)
            domain_transfer_order.state = domain_transfer_order.STATE_FAILED
            domain_transfer_order.last_error = rpc_error.details()
            logger.error(f"Failed to transfer {domain_transfer_order.domain}: {rpc_error.details()}")
        else:
            if transfer_data.status == 5:
                gchat_bot.notify_transfer.delay(domain_transfer_order.id, transfer_data.registry_name)
                logger.info(f"{domain_transfer_order.domain} successfully transferred")
            else:
                gchat_bot.notify_transfer_pending.delay(domain_transfer_order.id, transfer_data.registry_name)

                domain_transfer_order.state = domain_transfer_order.STATE_PENDING_APPROVAL
                domain_transfer_order.redirect_uri = None
                domain_transfer_order.last_error = None
                domain_transfer_order.save()

                logger.info(f"{domain_transfer_order.domain} transfer successfully submitted")
    else:
        try:
            _, _, registry_id = apps.epp_client.check_domain(domain_transfer_order.domain)
        except grpc.RpcError as rpc_error:
            billing.reverse_charge(domain_transfer_order.id)
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


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_transfer(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder
    user = domain_transfer_order.get_user()

    zone, _ = zone_info.get_domain_info(domain_transfer_order.domain)
    if not zone:
        domain_transfer_order.state = domain_transfer_order.STATE_FAILED
        domain_transfer_order.last_error = "You don't have permission to perform this action"
        logger.error(f"Failed to get zone info for {domain_transfer_order.domain}")
        billing.reverse_charge(domain_transfer_order.id)
        return

    charge_order(
        order=domain_transfer_order,
        username=user.username,
        descriptor=f"{domain_transfer_order.domain} domain transfer",
        charge_id=domain_transfer_order.id,
        return_uri=settings.EXTERNAL_URL_BASE + reverse(
            'domain_transfer_confirm', args=(domain_transfer_order.id,)
        ),
        success_func=process_domain_transfer_paid,
        notif_queue="domains_transfer_billing_notif"
    )


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_transfer_contacts(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder

    zone, sld = zone_info.get_domain_info(domain_transfer_order.domain)
    if not zone:
        logger.error(f"Failed to get zone info for {domain_transfer_order.domain}")
        return

    domain_data = apps.epp_client.get_domain(domain_transfer_order.domain)

    update_req = apps.epp_api.domain_pb2.DomainUpdateRequest(
        name=domain_data.name,
    )
    should_send = False
    if zone.registrant_supported:
        registrant_id = domain_transfer_order.registrant_contact.get_registry_id(domain_data.registry_name)
        if domain_data.registrant != registrant_id.registry_contact_id:
            update_req.new_registrant.value = registrant_id.registry_contact_id
            should_send = True

    def _update_contact(contact_type, new_id):
        global should_send
        old_contact = next(filter(lambda c: c.contact_type == contact_type, domain_data.contacts), None)

        if old_contact:
            if old_contact.contact_id == new_id:
                return
            update_req.remove.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
                contact=apps.epp_api.domain_pb2.Contact(
                    type=contact_type,
                    id=old_contact.contact_id
                )
            ))

        update_req.add.append(apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
            contact=apps.epp_api.domain_pb2.Contact(
                type=contact_type,
                id=new_id
            )
        ))
        should_send = True

    if domain_transfer_order.tech_contact and zone.tech_supported:
        tech_contact_id = domain_transfer_order.tech_contact.get_registry_id(domain_data.registry_name)
        _update_contact("tech", tech_contact_id.registry_contact_id)

    if domain_transfer_order.admin_contact and zone.admin_supported:
        admin_contact_id = domain_transfer_order.admin_contact.get_registry_id(domain_data.registry_name)
        _update_contact("admin", admin_contact_id.registry_contact_id)

    if domain_transfer_order.billing_contact and zone.billing_supported:
        billing_contact_id = domain_transfer_order.billing_contact.get_registry_id(domain_data.registry_name)
        _update_contact("billing", billing_contact_id.registry_contact_id)

    if should_send:
        apps.epp_client.stub.DomainUpdate(update_req)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_transfer_complete(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder

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

    emails.mail_transferred.delay(domain_transfer_order.id)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_transfer_failed(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder

    billing.reverse_charge(domain_transfer_order.id)
    domain_transfer_order.state = domain_transfer_order.STATE_FAILED
    domain_transfer_order.save()

    emails.mail_transfer_failed.delay(domain_transfer_order.id)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def set_dns_to_own(domain_id):
    domain = models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration
    domain_data = apps.epp_client.get_domain(domain.domain)

    domain_info = zone_info.get_domain_info(domain.domain)[0]

    hosts = ["ns1.as207960.net", "ns2.as207960.net"]

    cur_ns = list(map(lambda ns: ns.host_obj.lower(), domain_data.name_servers))

    rem_hosts = list(filter(lambda a: a not in hosts, cur_ns))
    add_hosts = list(filter(lambda a: a not in cur_ns, hosts))

    if (not rem_hosts) and (not add_hosts):
        return

    if domain_info.pre_create_host_objects:
        for host in hosts:
            host_available, _ = apps.epp_client.check_host(host, domain_data.registry_name)

            if host_available:
                apps.epp_client.create_host(host, [], domain_data.registry_name)

    apps.epp_client.stub.DomainUpdate(apps.epp_api.domain_pb2.DomainUpdateRequest(
        name=domain_data.name,
        remove=list(map(lambda h: apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
            nameserver=apps.epp_api.domain_pb2.NameServer(
                host_obj=h
            )
        ), rem_hosts)),
        add=list(map(lambda h: apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
            nameserver=apps.epp_api.domain_pb2.NameServer(
                host_obj=h
            )
        ), add_hosts))
    ))

