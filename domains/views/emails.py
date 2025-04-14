from django.template.loader import render_to_string
from django.shortcuts import reverse
from celery import shared_task
from django.conf import settings
from .. import models
import requests
import django_keycloak_auth.clients


def get_feedback_url(description: str, reference: str):
    if settings.FEEDBACK_URL == "none":
        return None
    access_token = django_keycloak_auth.clients.get_access_token()
    r = requests.post(f"{settings.FEEDBACK_URL}/api/feedback_request/", json={
        "description": description,
        "action_reference": reference
    }, headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    })
    r.raise_for_status()
    data = r.json()
    return data["public_url"]


def send_email(user, data: dict):
    request = {
        "template_id": settings.LISTMONK_TEMPLATE_ID,
        "from_email": settings.DEFAULT_FROM_EMAIL,
        "data": data,
        "headers": [{
            "Reply-To": "Glauca Support <hello@glauca.digital>",
            "Bcc": "email-log@as207960.net"
        }]
    }
    request["data"]["service"] = "Domains by Glauca"

    try:
        django_keycloak_auth.clients.get_active_access_token(user.oidc_profile)
        if user.oidc_profile.id_data and user.oidc_profile.id_data.get("listmonk_user_id"):
            request["subscriber_id"] = user.oidc_profile.id_data["listmonk_user_id"]
        else:
            request["subscriber_email"] = user.email
    except django_keycloak_auth.clients.TokensExpired:
        request["subscriber_email"] = user.email

    access_token = django_keycloak_auth.clients.get_access_token()
    r = requests.post(
        f"{settings.LISTMONK_URL}/api/tx",
        json=request,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
    )
    r.raise_for_status()

@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_registered(registration_order_id):
    domain = models.DomainRegistrationOrder.objects\
        .filter(pk=registration_order_id).first()  # type: models.DomainRegistrationOrder
    user = domain.get_user()
    if user:
        feedback_url = get_feedback_url(
            f"{domain.domain} domain registration", domain.id
        )
        domain_url = settings.EXTERNAL_URL_BASE + reverse('domain', args=(domain.domain_obj.id,))

        send_email(user, {
            "subject": "Domain registration success",
            "feedback_url": feedback_url,
            "content": render_to_string("domains_email/register_success.html", {
                "domain": domain.domain,
                "domain_url": domain_url,
            })
        })

@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_register_failed(registration_order_id, reason: str = None):
    domain = models.DomainRegistrationOrder.objects \
        .filter(pk=registration_order_id).first()  # type: models.DomainRegistrationOrder
    user = domain.get_user()
    if user:
        feedback_url = get_feedback_url(
            f"{domain.domain} domain registration", domain.id
        )

        send_email(user, {
            "subject": "Domain registration failure",
            "feedback_url": feedback_url,
            "content": render_to_string("domains_email/register_fail.html", {
                "domain": domain.domain,
                "reason": reason if reason else domain.last_error
            })
        })


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_transferred(transfer_order_id):
    domain = models.DomainTransferOrder.objects.filter(pk=transfer_order_id).first()  # type: models.DomainTransferOrder
    user = domain.get_user()
    if user:
        feedback_url = get_feedback_url(
            f"{domain.domain} domain transfer", domain.id
        )
        domain_url = settings.EXTERNAL_URL_BASE + reverse('domain', args=(domain.domain_obj.id,))

        send_email(user, {
            "subject": "Domain transfer success",
            "feedback_url": feedback_url,
            "content": render_to_string("domains_email/transfer_success.html", {
                "domain": domain.domain,
                "domain_url": domain_url,
            })
        })


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_transfer_failed(transfer_order_id, reason: str = None):
    domain = models.DomainTransferOrder.objects.filter(pk=transfer_order_id).first()  # type: models.DomainTransferOrder
    user = domain.get_user()
    if user:
        feedback_url = get_feedback_url(
            f"{domain.domain} domain transfer", domain.id
        )

        send_email(user, {
            "subject": "Domain transfer failure",
            "feedback_url": feedback_url,
            "content": render_to_string("domains_email/transfer_fail.html", {
                "domain": domain.domain,
                "reason": reason
            })
        })


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_restored(restore_order_id):
    domain = models.DomainRestoreOrder.objects.filter(pk=restore_order_id).first()  # type: models.DomainRestoreOrder
    user = domain.get_user()
    if user:
        feedback_url = get_feedback_url(
            f"{domain.domain} domain restoration", domain.id
        )

        send_email(user, {
            "subject": "Domain restore success",
            "feedback_url": feedback_url,
            "content": render_to_string("domains_email/restore_success.html", {
                "domain": domain.domain,
            })
        })


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_restore_failed(restore_order_id, reason: str = None):
    domain = models.DomainRestoreOrder.objects.filter(pk=restore_order_id).first()  # type: models.DomainRestoreOrder
    user = domain.get_user()
    if user:
        feedback_url = get_feedback_url(
            f"{domain.domain} domain restoration", domain.id
        )

        send_email(user, {
            "subject": "Domain restore failure",
            "feedback_url": feedback_url,
            "content": render_to_string("domains_email/restore_fail.html", {
                "domain": domain.domain,
                "reason": reason
            })
        })

@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_transferred_out(domain_id):
    domain = models.DomainRegistration.objects\
        .filter(id=domain_id).first()  # type: models.DomainRegistration
    user = domain.get_user()
    if user:
        feedback_url = get_feedback_url(
            f"{domain.domain} domain transfer out", domain.id
        )

        send_email(user, {
            "subject": "Domain transferred out",
            "feedback_url": feedback_url,
            "content": render_to_string("domains_email/transfer_out.html", {
                "domain": domain.domain,
            })
        })


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_transfer_out_request(domain_id):
    domain = models.DomainRegistration.objects\
        .filter(id=domain_id).first()  # type: models.DomainRegistration
    user = domain.get_user()
    if user:
        send_email(user, {
            "subject": "Domain transfer request",
            "content": render_to_string("domains_email/transfer_out_request.html", {
                "domain": domain.domain,
                "transfer_approve_url":
                    settings.EXTERNAL_URL_BASE + reverse('domain_transfer_out', args=(domain.id, "approve")),
                "transfer_reject_url":
                    settings.EXTERNAL_URL_BASE + reverse('domain_transfer_out', args=(domain.id, "reject")),
            })
        })


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_auto_renew_redirect(order_id):
    order = models.DomainAutomaticRenewOrder.objects\
        .filter(id=order_id).first()  # type: models.DomainAutomaticRenewOrder
    if order.domain_obj:
        user = order.domain_obj.get_user()
        if user:
            send_email(user, {
                "subject": f"{order.unicode_domain} renewal - payment required",
                "content": render_to_string("domains_email/renewal_redirect.html", {
                    "domain": order.unicode_domain,
                    "redirect_url": order.redirect_uri
                })
            })


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_auto_renew_failed(order_id):
    order = models.DomainAutomaticRenewOrder.objects\
        .filter(id=order_id).first()  # type: models.DomainAutomaticRenewOrder
    if order.domain_obj:
        user = order.domain_obj.get_user()
        if user:
            send_email(user, {
                "subject": f"{order.unicode_domain} renewal - payment failed",
                "content": render_to_string("domains_email/renewal_failed.html", {
                    "domain": order.unicode_domain,
                    "error": order.last_error
                })
            })


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_auto_renew_success(order_id):
    order = models.DomainAutomaticRenewOrder.objects\
        .filter(id=order_id).first()  # type: models.DomainAutomaticRenewOrder
    if order.domain_obj:
        user = order.domain_obj.get_user()
        if user:
            send_email(user, {
                "subject": f"{order.unicode_domain} renewal successful",
                "content": render_to_string("domains_email/renewal_success.html", {
                    "domain": order.unicode_domain,
                })
            })


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_locked(domain_id):
    domain = models.DomainRegistration.objects.filter(pk=domain_id).first()  # type: models.DomainRegistration
    user = domain.get_user()
    if user:
        feedback_url = get_feedback_url(
            f"{domain.domain} registry lock", domain.id
        )

        send_email(user, {
            "subject": "Domain registry lock update success",
            "feedback_url": feedback_url,
            "content": render_to_string("domains_email/locking_success.html", {
                "domain": domain.domain,
            })
        })


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_lock_failed(domain_id, reason: str = None):
    domain = models.DomainRegistration.objects.filter(pk=domain_id).first()  # type: models.DomainRegistration
    user = domain.get_user()
    if user:
        feedback_url = get_feedback_url(
            f"{domain.domain} registry lock", domain.id
        )

        send_email(user, {
            "subject": "Domain registry lock update success",
            "feedback_url": feedback_url,
            "content": render_to_string("domains_email/locking_fail.html", {
                "domain": domain.domain,
                "reason": reason
            })
        })