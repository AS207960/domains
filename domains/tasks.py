from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.shortcuts import reverse
from . import models, zone_info, apps, utils
from .views import billing, gchat_bot, emails
import grpc
import requests
import pika
import typing
import google.protobuf.wrappers_pb2


pika_parameters = pika.URLParameters(settings.RABBITMQ_RPC_URL)
logger = get_task_logger(__name__)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def update_contact(contact_registry_id):
    contact_obj = models.ContactRegistry.objects.filter(id=contact_registry_id).first()  # type: models.ContactRegistry
    if not contact_obj:
        return

    if contact_obj.registry:
        zone_data = zone_info.DomainInfo(contact_obj.registry, None)
    else:
        zone_data = None

    if contact_obj.role:
        role = apps.epp_api.ContactRole(contact_obj.role)
    else:
        role = None

    is_isnic = zone_data and zone_data.is_isnic
    is_eurid = zone_data and zone_data.is_eurid
    internationalized_address_supported = zone_data.internationalized_address_supported if zone_data else False
    internationalized_address_required = zone_data.internationalized_address_required if zone_data else False

    instance = contact_obj.contact
    try:
        contact = apps.epp_client.get_contact(contact_obj.registry_contact_id, contact_obj.registry_id)
        contact.update(
            local_address=instance.get_local_address(
                eurid_role=role if is_eurid else None
            ) if not is_isnic else None,
            int_address=(
                instance.get_int_address(internationalized_address_required)
                if not is_isnic else instance.get_local_address()
            ) if internationalized_address_supported else None,
            phone=apps.epp_api.Phone(
                number=f"+{instance.phone.country_code}.{instance.phone.national_number}",
                ext=instance.phone_ext
            ) if instance.phone else None,
            fax=apps.epp_api.Phone(
                number=f"+{instance.fax.country_code}.{instance.fax.national_number}",
                ext=instance.fax_ext
            ) if instance.fax else None,
            email=(
                instance.get_public_email() if not is_isnic else settings.ISNIC_CONTACT_EMAIL
            ) if not is_eurid else instance.email,
            entity_type=instance.entity_type,
            trading_name=instance.trading_name,
            company_number=instance.company_number,
            disclosure=instance.get_disclosure(zone_data),
            eurid=apps.epp_api.EURIDContactUpdate(
                whois_email=instance.private_whois_email if not instance.disclose_email else None,
                vat_number=None,
                language="en",
                country_of_citizenship=instance.eurid_citizenship if instance.eurid_citizenship else None,
            ) if is_eurid else None,
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
        return_uri: typing.Optional[str],
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
        if charge_state.immediate_completion:
            order.state = order.STATE_PROCESSING
            order.save()
            success_func.delay(order.id)
        else:
            if charge_state.success:
                order.state = order.STATE_PROCESSING
                order.save()
            elif charge_state.redirect_uri:
                order.state = order.STATE_NEEDS_PAYMENT
                order.redirect_uri = charge_state.redirect_uri
                order.save()
            else:
                order.state = order.STATE_FAILED
                order.last_error = charge_state.error
                order.redirect_uri = None
                order.save()
                logger.warn(f"Payment for {descriptor} failed with error {charge_state.error}")

    return False


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
    zone, sld = zone_info.get_domain_info(domain_registration_order.domain, registry_id=domain_registration_order.registry_id)

    try:
        available, _, registry_id = apps.epp_client.check_domain(domain_registration_order.domain)
    except grpc.RpcError as rpc_error:
        logger.warn(f"Failed to check availability of {domain_registration_order.domain}: {rpc_error.details()}")
        raise rpc_error

    domain_registration_order.registry_id = registry_id

    if not available:
        domain_registration_order.state = domain_registration_order.STATE_FAILED
        domain_registration_order.last_error = "Domain no longer available to purchase."
        domain_registration_order.save()
        billing.reverse_charge(domain_registration_order.id)
        emails.mail_register_failed.delay(domain_registration_order.id)
        return

    if zone.direct_registration_supported:
        if zone.pre_create_host_objects:
            for host in ('ns1.as207960.net', 'ns2.as207960.net', 'ns3.as207960.net', 'ns4.as207960.net'):
                try:
                    host_available, _ = apps.epp_client.check_host(host, registry_id)

                    if host_available:
                        apps.epp_client.create_host(host, [], registry_id, None)
                except grpc.RpcError as rpc_error:
                    logger.error(f"Failed to setup hosts for {domain_registration_order.domain}: {rpc_error.details()}")
                    raise rpc_error

        try:
            eurid = None
            contact_objs = []
            if zone.admin_supported and domain_registration_order.admin_contact:
                contact_objs.append(apps.epp_api.DomainContact(
                    contact_type="admin",
                    contact_id=domain_registration_order.admin_contact.get_registry_id(
                        registry_id, zone, role=apps.epp_api.ContactRole.Admin
                    ).registry_contact_id
                ))
            if zone.is_eurid:
                contact_objs.append(apps.epp_api.DomainContact(
                    contact_type="billing",
                    contact_id=settings.EURID_BILLING_CONTACT
                ))
            elif zone.billing_supported and domain_registration_order.billing_contact:
                contact_objs.append(apps.epp_api.DomainContact(
                    contact_type="billing",
                    contact_id=domain_registration_order.billing_contact.get_registry_id(
                        registry_id, zone, role=apps.epp_api.ContactRole.Billing
                    ).registry_contact_id
                ))
            if zone.tech_supported and domain_registration_order.tech_contact:
                if zone.is_eurid:
                    eurid = apps.epp_api.eurid_pb2.DomainCreateExtension(
                        on_site=google.protobuf.wrappers_pb2.StringValue(
                            value=domain_registration_order.tech_contact.get_registry_id(
                                registry_id, zone, role=apps.epp_api.ContactRole.OnSite
                            ).registry_contact_id
                        ),
                    )
                else:
                    contact_objs.append(apps.epp_api.DomainContact(
                        contact_type="tech",
                        contact_id=domain_registration_order.tech_contact.get_registry_id(
                            registry_id, zone, role=apps.epp_api.ContactRole.Tech
                        ).registry_contact_id
                    ))

            if zone.keysys_de or zone.keysys_tel or zone.keysys_auto_renew or zone.hsts_preload or zone.intended_use_required:
                keysys = apps.epp_api.keysys_pb2.DomainCreate()
                if zone.keysys_auto_renew:
                    keysys.renewal_mode = apps.epp_api.keysys_pb2.AutoRenew
                if zone.keysys_de:
                    keysys.de.abuse_contact.value = "https://as207960.net/contact"
                    keysys.de.general_contact.value = "https://as207960.net/contact"
                if zone.keysys_tel:
                    keysys.tel.whois_type.value = (
                        apps.epp_api.keysys_pb2.TelLegal if domain_registration_order.registrant_contact.is_company else
                        apps.epp_api.keysys_pb2.TelNatural
                    )
                    keysys.tel.publish_whois.value = False
                if zone.hsts_preload:
                    keysys.accept_ssl_requirements = True
                if zone.intended_use_required:
                    keysys.intended_use = domain_registration_order.intended_use
            else:
                keysys = None

            registrant_contact = zone.registrant_proxy(domain_registration_order.registrant_contact)
            if not registrant_contact:
                registrant_contact = domain_registration_order.registrant_contact.get_registry_id(
                    registry_id, zone, role=apps.epp_api.ContactRole.Registrant
                ).registry_contact_id if zone.registrant_supported else 'NONE'
            pending, _, _, _ = apps.epp_client.create_domain(
                domain=domain_registration_order.domain,
                period=period,
                registrant=registrant_contact,
                contacts=contact_objs,
                name_servers=[apps.epp_api.DomainNameServer(
                    host_obj='ns1.as207960.net' if zone.host_object_supported else None,
                    host_name='ns1.as207960.net' if not zone.host_object_supported else None,
                    address=[]
                ), apps.epp_api.DomainNameServer(
                    host_obj='ns2.as207960.net' if zone.host_object_supported else None,
                    host_name='ns2.as207960.net' if not zone.host_object_supported else None,
                    address=[]
                ), apps.epp_api.DomainNameServer(
                    host_obj='ns3.as207960.net' if zone.host_object_supported else None,
                    host_name='ns3.as207960.net' if not zone.host_object_supported else None,
                    address=[]
                ), apps.epp_api.DomainNameServer(
                    host_obj='ns4.as207960.net' if zone.host_object_supported else None,
                    host_name='ns4.as207960.net' if not zone.host_object_supported else None,
                    address=[]
                )],
                auth_info=domain_registration_order.auth_info,
                keysys=keysys,
                eurid=eurid,
                registry_id=domain_registration_order.registry_id
            )
        except grpc.RpcError as rpc_error:
            domain_registration_order.state = domain_registration_order.STATE_PENDING_APPROVAL
            domain_registration_order.last_error = rpc_error.details()
            domain_registration_order.save()
            gchat_bot.request_registration.delay(domain_registration_order.id, registry_id, str(period))
            logger.error(f"Failed to register {domain_registration_order.domain}: {rpc_error.details()},"
                         f" passing off to human")
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
            gchat_bot.notify_registration_pending.delay(domain_registration_order.id, str(period))
            logger.info(f"{domain_registration_order.domain} registration successfully submitted")
    else:
        domain_registration_order.save()
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

    zone, _ = zone_info.get_domain_info(domain_registration_order.domain, registry_id=domain_registration_order.registry_id)
    if not zone:
        domain_registration_order.state = domain_registration_order.STATE_FAILED
        domain_registration_order.last_error = "You don't have permission to perform this action"
        logger.error(f"Failed to get zone info for {domain_registration_order.domain}")
        billing.reverse_charge(domain_registration_order.id)
        emails.mail_register_failed.delay(domain_registration_order.id)
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
    if models.DomainRegistration.objects.filter(
        id=domain_registration_order.domain_id
    ).first():
        return

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
        billing_contact=domain_registration_order.billing_contact,
        registry_id=domain_registration_order.registry_id
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
    zone, sld = zone_info.get_domain_info(
        domain_renewal_order.domain, registry_id=domain_renewal_order.domain_obj.registry_id)

    period = apps.epp_api.Period(
        value=domain_renewal_order.period_value,
        unit=domain_renewal_order.period_unit
    )
    try:
        domain_data = apps.epp_client.get_domain(
            domain_renewal_order.domain, registry_id=domain_renewal_order.domain_obj.registry_id
        )
    except grpc.RpcError as rpc_error:
        logger.warn(f"Failed to load data of {domain_renewal_order.domain}: {rpc_error.details()}")
        raise rpc_error

    if zone.renew_supported:
        if zone.direct_renew_supported:
            try:
                _pending, _new_expiry, registry_id = apps.epp_client.renew_domain(
                    domain_renewal_order.domain, period, domain_data.expiry_date,
                    registry_id=domain_renewal_order.domain_obj.registry_id
                )
            except grpc.RpcError as rpc_error:
                domain_renewal_order.state = domain_renewal_order.STATE_PENDING_APPROVAL
                domain_renewal_order.last_error = rpc_error.details()
                domain_renewal_order.save()
                gchat_bot.request_renew.delay(domain_renewal_order.id, domain_data.registry_id, str(period))
                logger.error(f"Failed to renew {domain_renewal_order.domain}: {rpc_error.details()},"
                             f" passing off to human")
                return

            gchat_bot.notify_renew.delay(domain_renewal_order.domain_obj.id, registry_id, str(period))

            domain_renewal_order.state = domain_renewal_order.STATE_COMPLETED
            domain_renewal_order.redirect_uri = None
            domain_renewal_order.last_error = None
            domain_renewal_order.save()

            logger.info(f"{domain_renewal_order.domain} successfully renewed")
            return

        else:
            gchat_bot.request_renew.delay(domain_renewal_order.id, domain_data.registry_id, str(period))

            domain_renewal_order.state = domain_renewal_order.STATE_PENDING_APPROVAL
            domain_renewal_order.save()

            logger.info(f"{domain_renewal_order.domain} successfully requested renewal")
            return

    domain_renewal_order.state = domain_renewal_order.STATE_COMPLETED
    domain_renewal_order.redirect_uri = None
    domain_renewal_order.last_error = None
    domain_renewal_order.save()
    gchat_bot.notify_renew.delay(domain_renewal_order.domain_obj_id, domain_data.registry_id, str(period))
    logger.info(f"{domain_renewal_order.domain} successfully renewed")


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_renewal(renewal_order_id):
    domain_renewal_order = \
        models.DomainRenewOrder.objects.get(id=renewal_order_id)  # type: models.DomainRenewOrder
    user = domain_renewal_order.get_user()

    zone, sld = zone_info.get_domain_info(
        domain_renewal_order.domain, registry_id=domain_renewal_order.domain_obj.registry_id)
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
def process_domain_renewal_complete(renew_order_id):
    domain_renew_order = \
        models.DomainRenewOrder.objects.get(id=renew_order_id)  # type: models.DomainRenewOrder

    period = apps.epp_api.Period(
        value=domain_renew_order.period_value,
        unit=domain_renew_order.period_unit
    )

    domain_renew_order.state = domain_renew_order.STATE_COMPLETED
    domain_renew_order.redirect_uri = None
    domain_renew_order.last_error = None
    domain_renew_order.save()
    gchat_bot.notify_renew.delay(domain_renew_order.domain_obj_id, "N/A", str(period))


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_renewal_failed(renew_order_id):
    domain_renew_order = \
        models.DomainRenewOrder.objects.get(id=renew_order_id)  # type: models.DomainRenewOrder

    billing.reverse_charge(domain_renew_order.id)
    domain_renew_order.state = domain_renew_order.STATE_FAILED
    domain_renew_order.save()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_restore_paid(restore_order_id):
    domain_restore_order = \
        models.DomainRestoreOrder.objects.get(id=restore_order_id)  # type: models.DomainRestoreOrder

    zone, sld = zone_info.get_domain_info(
        domain_restore_order.domain, registry_id=domain_restore_order.domain_obj.registry_id)

    try:
        domain_data = apps.epp_client.get_domain(
            domain_restore_order.domain, registry_id=domain_restore_order.domain_obj.registry_id
        )
    except grpc.RpcError as rpc_error:
        logger.warn(f"Failed to load data of {domain_restore_order.domain}: {rpc_error.details()}")
        domain_data = None

    if zone.direct_restore_supported:
        try:
            pending, registry_id = apps.epp_client.restore_domain(
                domain_restore_order.domain,
                registry_id=domain_restore_order.domain_obj.registry_id
            )
            domain_restore_order.domain_obj.deleted = pending
            domain_restore_order.domain_obj.pending = pending
            domain_restore_order.domain_obj.save()
            gchat_bot.notify_restore.delay(domain_restore_order.id)
        except grpc.RpcError as rpc_error:
            domain_restore_order.state = domain_restore_order.STATE_PENDING_APPROVAL
            domain_restore_order.last_error = rpc_error.details()
            domain_restore_order.save()
            gchat_bot.request_restore.delay(domain_restore_order.id, "")
            logger.error(f"Failed to restore {domain_restore_order.domain}: {rpc_error.details()},"
                         f" passing off to human")
            return

        if domain_restore_order.should_renew and zone.renew_supported:
            period = apps.epp_api.Period(
                value=domain_restore_order.period_value,
                unit=domain_restore_order.period_unit
            )

            if zone.direct_renew_supported and domain_data:
                try:
                    _pending, _new_expiry, _registry_id = apps.epp_client.renew_domain(
                        domain_restore_order.domain, period, domain_data.expiry_date,
                        registry_id=domain_restore_order.domain_obj.registry_id
                    )
                except grpc.RpcError as rpc_error:
                    logger.error(f"Failed to renew {domain_restore_order.domain}: {rpc_error.details()}")
                    return
            else:
                gchat_bot.request_restore_renew.delay(domain_restore_order.id, str(period))

                domain_restore_order.state = domain_restore_order.STATE_PENDING_APPROVAL
                domain_restore_order.save()

                logger.info(f"{domain_restore_order.domain} successfully requested renewal following restore")
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

    zone, sld = zone_info.get_domain_info(
        domain_restore_order.domain, registry_id=domain_restore_order.domain_obj.registry_id)
    if not zone:
        domain_restore_order.state = domain_restore_order.STATE_FAILED
        domain_restore_order.last_error = "You don't have permission to perform this action"
        logger.error(f"Failed to get zone info for {domain_restore_order.domain}")
        billing.reverse_charge(domain_restore_order.id)
        emails.mail_restore_failed.delay(domain_restore_order.id)
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

    billing.reverse_charge(domain_restore_order.id)
    domain_restore_order.state = domain_restore_order.STATE_FAILED
    domain_restore_order.save()

    emails.mail_restore_failed.delay(domain_restore_order.id)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_transfer_paid(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder
    zone, sld = zone_info.get_domain_info(domain_transfer_order.domain, registry_id=domain_transfer_order.registry_id)

    if zone.direct_transfer_supported:
        try:
            if zone.period_required_for_transfer:
                period = zone.pricing.periods[0]
            else:
                period = None

            if zone.is_eurid:
                _, _, registry_id = apps.epp_client.check_domain(domain_transfer_order.domain)
                eurid_data = apps.epp_api.eurid_pb2.DomainTransferExtension(
                    registrant=domain_transfer_order.registrant_contact.get_registry_id(
                        registry_id, zone, role=apps.epp_api.ContactRole.Registrant
                    ).registry_contact_id,
                    on_site=google.protobuf.wrappers_pb2.StringValue(
                        value=domain_transfer_order.tech_contact.get_registry_id(
                            registry_id, zone, role=apps.epp_api.ContactRole.OnSite
                        ).registry_contact_id
                    ) if domain_transfer_order.tech_contact else None,
                    billing=google.protobuf.wrappers_pb2.StringValue(
                        value=settings.EURID_BILLING_CONTACT
                    )
                )
            else:
                eurid_data = None

            transfer_data = apps.epp_client.transfer_request_domain(
                domain_transfer_order.domain,
                domain_transfer_order.auth_code,
                period=period,
                registry_id=domain_transfer_order.registry_id,
                eurid=eurid_data,
            )
        except grpc.RpcError as rpc_error:
            error_code = utils.epp_grpc_error_code(rpc_error)
            if error_code == "authorization-error":
                domain_transfer_order.state = domain_transfer_order.STATE_FAILED
                domain_transfer_order.last_error = "The transfer code provided is invalid."
                domain_transfer_order.save()
                billing.reverse_charge(domain_transfer_order.id)
                emails.mail_transfer_failed.delay(domain_transfer_order.id)
            elif error_code == "object-status-prohibits-operation":
                domain_transfer_order.state = domain_transfer_order.STATE_FAILED
                domain_transfer_order.last_error = "The domain is locked from being transferred by the previous registrar."
                domain_transfer_order.save()
                billing.reverse_charge(domain_transfer_order.id)
                emails.mail_transfer_failed.delay(domain_transfer_order.id)
            else:
                domain_transfer_order.state = domain_transfer_order.STATE_PENDING_APPROVAL
                domain_transfer_order.last_error = rpc_error.details()
                domain_transfer_order.save()
                gchat_bot.request_transfer.delay(domain_transfer_order.id, "")
                logger.error(f"Failed to transfer {domain_transfer_order.domain}: {rpc_error.details()},"
                             f" passing off to human")
        else:
            domain_transfer_order.registry_id = transfer_data.registry_name

            if transfer_data.status == 5:
                domain_transfer_order.state = domain_transfer_order.STATE_COMPLETED
                domain_transfer_order.redirect_uri = None
                domain_transfer_order.last_error = None
                domain_transfer_order.save()
                gchat_bot.notify_transfer.delay(domain_transfer_order.id, transfer_data.registry_name)
                process_domain_transfer_complete.delay(domain_transfer_order.id)
                logger.info(f"{domain_transfer_order.domain} successfully transferred")
            else:
                domain_transfer_order.state = domain_transfer_order.STATE_PENDING_APPROVAL
                domain_transfer_order.redirect_uri = None
                domain_transfer_order.last_error = None
                domain_transfer_order.save()

                gchat_bot.notify_transfer_pending.delay(domain_transfer_order.id, transfer_data.registry_name)

                logger.info(f"{domain_transfer_order.domain} transfer successfully submitted")
    else:
        try:
            _, _, registry_id = apps.epp_client.check_domain(domain_transfer_order.domain)
        except grpc.RpcError as rpc_error:
            domain_transfer_order.state = domain_transfer_order.STATE_PENDING_APPROVAL
            domain_transfer_order.last_error = rpc_error.details()
            domain_transfer_order.save()
            gchat_bot.request_transfer.delay(domain_transfer_order.id, "")
            logger.error(f"Failed to transfer {domain_transfer_order.domain}: {rpc_error.details()},"
                         f" passing off to human")
            return

        gchat_bot.request_transfer.delay(domain_transfer_order.id, registry_id)

        domain_transfer_order.registry_id = registry_id
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

    zone, _ = zone_info.get_domain_info(domain_transfer_order.domain, registry_id=domain_transfer_order.registry_id)
    if not zone:
        domain_transfer_order.state = domain_transfer_order.STATE_FAILED
        domain_transfer_order.last_error = "You don't have permission to perform this action"
        domain_transfer_order.save()
        logger.error(f"Failed to get zone info for {domain_transfer_order.domain}")
        billing.reverse_charge(domain_transfer_order.id)
        emails.mail_transfer_failed.delay(domain_transfer_order.id)
        return

    if registration := models.DomainRegistration.objects.filter(domain=domain_transfer_order.domain, former_domain=False).first():
        if registration.auth_info == domain_transfer_order.auth_code:
            registration.former_domain = True
            domain_transfer_order.state = domain_transfer_order.STATE_COMPLETED
            domain_transfer_order.redirect_uri = None
            domain_transfer_order.last_error = None
            domain_transfer_order.save()
            gchat_bot.notify_transfer.delay(domain_transfer_order.id, "INTERNAL")
            process_domain_transfer_complete.delay(domain_transfer_order.id)
            logger.info(f"{domain_transfer_order.domain} successfully transferred internally")
        else:
            domain_transfer_order.state = domain_transfer_order.STATE_FAILED
            domain_transfer_order.last_error = "The authorization code is invalid."
            domain_transfer_order.save()
            emails.mail_transfer_failed.delay(domain_transfer_order.id)

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

    zone, sld = zone_info.get_domain_info(domain_transfer_order.domain, registry_id=domain_transfer_order.registry_id)
    if not zone:
        logger.error(f"Failed to get zone info for {domain_transfer_order.domain}")
        return

    if zone.is_eurid:
        return

    domain_data = apps.epp_client.get_domain(
        domain_transfer_order.domain, registry_id=domain_transfer_order.registry_id
    )

    update_req = apps.epp_api.domain_pb2.DomainUpdateRequest(
        name=domain_data.name,
    )
    should_send = False
    if zone.registrant_supported and zone.registrant_change_supported:
        registrant_id = zone.registrant_proxy(domain_transfer_order.registrant_contact)
        if not registrant_id:
            registrant_id = domain_transfer_order.registrant_contact.get_registry_id(
                domain_data.registry_name, zone, role=apps.epp_api.ContactRole.Registrant
            )
        if domain_data.registrant != registrant_id.registry_contact_id:
            if zone.keysys_owner_trade:
                r = requests.get(
                    "https://api.rrpproxy.net/api/call",
                    params={
                        "s_login": settings.RRPPROXY_USER,
                        "s_pw": settings.RRPPROXY_PASS,
                        "command": "TradeDomain",
                        "domain": domain_data.name,
                        "ownercontact0": registrant_id.registry_contact_id,
                    }
                )
                r.raise_for_status()
            else:
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
        tech_contact_id = domain_transfer_order.tech_contact.get_registry_id(
            domain_data.registry_name, zone, role=apps.epp_api.ContactRole.Tech
        )
        _update_contact("tech", tech_contact_id.registry_contact_id)

    if domain_transfer_order.admin_contact and zone.admin_supported:
        admin_contact_id = domain_transfer_order.admin_contact.get_registry_id(
            domain_data.registry_name, zone, role=apps.epp_api.ContactRole.Admin
        )
        _update_contact("admin", admin_contact_id.registry_contact_id)

    if domain_transfer_order.billing_contact and zone.billing_supported:
        billing_contact_id = domain_transfer_order.billing_contact.get_registry_id(
            domain_data.registry_name, zone, role=apps.epp_api.ContactRole.Billing
        )
        _update_contact("billing", billing_contact_id.registry_contact_id)

    if should_send:
        apps.epp_client.stub.DomainUpdate(update_req)

@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_transfer_keysys(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder

    zone, sld = zone_info.get_domain_info(domain_transfer_order.domain, registry_id=domain_transfer_order.registry_id)
    if not zone:
        logger.error(f"Failed to get zone info for {domain_transfer_order.domain}")
        return

    domain_data = apps.epp_client.get_domain(
        domain_transfer_order.domain, registry_id=domain_transfer_order.registry_id
    )

    update_req = apps.epp_api.domain_pb2.DomainUpdateRequest(
        name=domain_data.name,
    )

    should_send = False

    if zone.keysys_auto_renew:
        update_req.keysys.renewal_mode = apps.epp_api.keysys_pb2.AutoRenew
        should_send = True

    if zone.keysys_de:
        update_req.keysys.de.abuse_contact.value = "https://as207960.net/contact"
        update_req.keysys.de.general_contact.value = "https://as207960.net/contact"
        should_send = True

    if zone.keysys_tel:
        update_req.keysys.tel.whois_type.value = (
            apps.epp_api.keysys_pb2.TelLegal if domain_transfer_order.domain_obj.registrant_contact.is_company else
            apps.epp_api.keysys_pb2.TelNatural
        )
        update_req.keysys.tel.publish_whois.value = False
        should_send = True

    if should_send:
        apps.epp_client.stub.DomainUpdate(update_req)

@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_transfer_complete(transfer_order_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder

    if models.DomainRegistration.objects.filter(id=domain_transfer_order.domain_id).exists():
        return

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
    process_domain_transfer_keysys.delay(domain_transfer_order.id)

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

    set_dns(domain, [
        "ns1.as207960.net",
        "ns2.as207960.net",
        "ns3.as207960.net",
        "ns4.as207960.net"
    ])

def set_dns(domain: models.DomainRegistration, hosts: typing.List[str]):
    domain_data = apps.epp_client.get_domain(
        domain.domain, registry_id=domain.registry_id
    )

    domain_info = zone_info.get_domain_info(domain.domain, registry_id=domain.registry_id)[0]

    if domain_info.host_object_supported:
        cur_ns = list(map(lambda ns: ns.host_obj.lower(), domain_data.name_servers))
    else:
        cur_ns = list(map(lambda ns: ns.host_name.lower(), domain_data.name_servers))

    rem_hosts = list(filter(lambda a: a not in hosts, cur_ns))
    add_hosts = list(filter(lambda a: a not in cur_ns, hosts))

    if (not rem_hosts) and (not add_hosts):
        return

    if domain_info.pre_create_host_objects:
        for host in hosts:
            host_available, _ = apps.epp_client.check_host(host, domain_data.registry_name)

            if host_available:
                apps.epp_client.create_host(host, [], domain_data.registry_name, None)

    apps.epp_client.stub.DomainUpdate(apps.epp_api.domain_pb2.DomainUpdateRequest(
        name=domain_data.name,
        remove=list(map(lambda h: apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
            nameserver=apps.epp_api.domain_pb2.NameServer(
                host_obj=h if domain_info.host_object_supported else None,
                host_name=h if not domain_info.host_object_supported else None,
            )
        ), rem_hosts)),
        add=list(map(lambda h: apps.epp_api.domain_pb2.DomainUpdateRequest.Param(
            nameserver=apps.epp_api.domain_pb2.NameServer(
                host_obj=h if domain_info.host_object_supported else None,
                host_name=h if not domain_info.host_object_supported else None,
            )
        ), add_hosts))
    ))

@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_auto_renew_paid(renew_order_id):
    domain_renewal_order = \
        models.DomainAutomaticRenewOrder.objects.get(id=renew_order_id)  # type: models.DomainAutomaticRenewOrder
    zone, sld = zone_info.get_domain_info(
        domain_renewal_order.domain, registry_id=domain_renewal_order.domain_obj.registry_id)

    period = apps.epp_api.Period(
        value=domain_renewal_order.period_value,
        unit=domain_renewal_order.period_unit
    )

    try:
        domain_data = apps.epp_client.get_domain(
            domain_renewal_order.domain, registry_id=domain_renewal_order.domain_obj.registry_id
        )
    except grpc.RpcError as rpc_error:
        logger.warn(f"Failed to load data of {domain_renewal_order.domain}: {rpc_error.details()}")
        raise rpc_error

    if zone.renew_supported:
        if zone.direct_renew_supported:
            try:
                _pending, _new_expiry, _ = apps.epp_client.renew_domain(
                    domain_renewal_order.domain, period, domain_data.expiry_date,
                    registry_id=domain_renewal_order.domain_obj.registry_id
                )
            except grpc.RpcError as rpc_error:
                domain_renewal_order.state = domain_renewal_order.STATE_PENDING_APPROVAL
                domain_renewal_order.last_error = rpc_error.details()
                domain_renewal_order.save()
                gchat_bot.request_renew.delay(domain_renewal_order.id, domain_data.registry_id, str(period), auto=True)
                logger.error(f"Failed to renew {domain_renewal_order.domain}: {rpc_error.details()},"
                             f" passing off to human")
                return
        else:
            gchat_bot.request_renew.delay(domain_renewal_order.id, domain_data.registry_id, str(period), auto=True)

            domain_renewal_order.state = domain_renewal_order.STATE_PENDING_APPROVAL
            domain_renewal_order.save()

            logger.info(f"{domain_renewal_order.domain} successfully requested renewal")
            return

    gchat_bot.notify_renew.delay(domain_renewal_order.domain_obj.id, domain_data.registry_name, str(period))

    domain_renewal_order.state = domain_renewal_order.STATE_COMPLETED
    domain_renewal_order.redirect_uri = None
    domain_renewal_order.last_error = None
    domain_renewal_order.save()

    emails.mail_auto_renew_success.delay(domain_renewal_order.id)
    logger.info(f"{domain_renewal_order.domain} successfully renewed")


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_auto_renew_complete(renew_order_id):
    domain_renew_order = \
        models.DomainAutomaticRenewOrder.objects.get(id=renew_order_id)  # type: models.DomainRenewOrder

    emails.mail_auto_renew_success.delay(domain_renew_order.id)

    domain_renew_order.state = domain_renew_order.STATE_COMPLETED
    domain_renew_order.redirect_uri = None
    domain_renew_order.last_error = None
    domain_renew_order.save()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_auto_renew_failed(renew_order_id):
    domain_renew_order = \
        models.DomainAutomaticRenewOrder.objects.get(id=renew_order_id)  # type: models.DomainRenewOrder

    billing.reverse_charge(domain_renew_order.id)
    domain_renew_order.state = domain_renew_order.STATE_FAILED
    domain_renew_order.save()

    emails.mail_auto_renew_failed.delay(domain_renew_order.id)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_locking_complete(domain_id):
    domain_obj = models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration

    domain_obj.pending_registry_lock_status = None
    domain_obj.save()

    emails.mail_locked.delay(domain_obj.id)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def process_domain_locking_failed(domain_id):
    domain_obj = models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration

    domain_obj.pending_registry_lock_status = None
    domain_obj.save()

    emails.mail_lock_failed.delay(domain_obj.id)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def notify_dnssec_disabled(domain_id):
    domain_obj = models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration

    pika_connection = pika.BlockingConnection(parameters=pika_parameters)
    pika_channel = pika_connection.channel()
    pika_channel.basic_publish(
        exchange='',
        routing_key='hexdns_disable_dnssec',
        body=domain_obj.domain.encode()
    )
    pika_connection.close()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def notify_dnssec_enabled(domain_id):
    domain_obj = models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration

    pika_connection = pika.BlockingConnection(parameters=pika_parameters)
    pika_channel = pika_connection.channel()
    pika_channel.basic_publish(
        exchange='',
        routing_key='hexdns_enable_dnssec',
        body=domain_obj.domain.encode()
    )
    pika_connection.close()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3,
    ignore_result=True
)
def request_auth_code(domain_id):
    domain = models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration

    zone, _ = zone_info.get_domain_info(domain.domain, registry_id=domain.registry_id)
    if not zone:
        logger.error(f"Failed to request auth code for {domain.domain}: unknown zone")
        return

    if not zone.keysys_request_auth_code and not zone.eurid_request_auth_code:
        logger.error(f"Failed to request auth code for {domain.domain}: unsupported for zone")
        return

    if zone.keysys_request_auth_code:
        try:
            apps.epp_client.stub.DomainUpdate(apps.epp_api.domain_pb2.DomainUpdateRequest(
                name=domain.domain,
                registry_name=google.protobuf.wrappers_pb2.StringValue(value=domain.registry_id),
                keysys=apps.epp_api.keysys_pb2.DomainUpdate(
                    request_auth_code=google.protobuf.wrappers_pb2.BoolValue(value=True),
                )
            ))
        except grpc.RpcError as rpc_error:
            logger.warn(f"Failed to request auth code for {domain.domain}: {rpc_error.details()}")
            raise rpc_error

        try:
            domain_data = apps.epp_client.get_domain(
                domain.domain, registry_id=domain.registry_id
            )
        except grpc.RpcError as rpc_error:
            logger.warn(f"Failed to load data of {domain.domain}: {rpc_error.details()}")
            raise rpc_error

        new_auth_code = domain_data.auth_code
        auth_code_expiry = None
    elif zone.eurid_request_auth_code:
        try:
            domain_data = apps.epp_client.stub.DomainInfo(apps.epp_api.domain_pb2.DomainInfoRequest(
                name=domain.domain,
                registry_name=google.protobuf.wrappers_pb2.StringValue(value=domain.registry_id) if domain.registry_id else None,
            ))
        except grpc.RpcError as rpc_error:
            error_code = utils.epp_grpc_error_code(rpc_error)
            if error_code == "object-does-not-exist":
                logger.warn(f"Cannot request auth code for nonexistent domain {domain.domain}: {rpc_error.details()}")
                return
            else:
                logger.warn(f"Failed to request auth code for {domain.domain}: {rpc_error.details()}")
                raise rpc_error

        if domain_data.auth_info:
            new_auth_code = domain_data.auth_info.value
            auth_code_expiry = domain_data.eurid_data.auth_info_valid_until.ToDatetime() if domain_data.eurid_data.auth_info_valid_until else None
        else:
            try:
                domain_data = apps.epp_client.stub.DomainInfo(apps.epp_api.domain_pb2.DomainInfoRequest(
                    name=domain.domain,
                    registry_name=google.protobuf.wrappers_pb2.StringValue(value=domain.registry_id) if domain.registry_id else None,
                    eurid_data=apps.epp_api.eurid_pb2.DomainInfoRequest(
                        request=True
                    )
                ))
            except grpc.RpcError as rpc_error:
                error_code = utils.epp_grpc_error_code(rpc_error)
                if error_code == "object-exists":
                    logger.warn(f"Authcode already exists for domain {domain.domain}: {rpc_error.details()}")
                    return
                elif error_code == "object-does-not-exist":
                    logger.warn(f"Cannot request auth code for nonexistent domain {domain.domain}: {rpc_error.details()}")
                    return
                else:
                    logger.warn(f"Failed to request auth code for {domain.domain}: {rpc_error.details()}")
                    raise rpc_error

            new_auth_code = domain_data.auth_info.value
            auth_code_expiry = domain_data.eurid_data.auth_info_valid_until.ToDatetime() if domain_data.eurid_data.auth_info_valid_until else None
    else:
        raise NotImplementedError()

    emails.mail_new_auth_code.delay(domain.id, new_auth_code, auth_code_expiry)
    logger.info(f"New auth code set for {domain.domain}")