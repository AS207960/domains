from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
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

        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "feedback_url": feedback_url,
            "domain_url": domain_url,
        }
        html_content = render_to_string("domains_email/register_success.html", context)
        txt_content = render_to_string("domains_email/register_success.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain registration success',
            body=txt_content,
            to=[user.email],
            bcc=['email-log@as207960.net'],
            reply_to=['Glauca Support <hello@glauca.digital>']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


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

        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "reason": reason,
            "feedback_url": feedback_url,
        }
        html_content = render_to_string("domains_email/register_fail.html", context)
        txt_content = render_to_string("domains_email/register_fail.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain registration failure',
            body=txt_content,
            to=[user.email],
            bcc=['email-log@as207960.net'],
            reply_to=['Glauca Support <hello@glauca.digital>']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


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

        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "feedback_url": feedback_url,
            "domain_url": domain_url,
        }
        html_content = render_to_string("domains_email/transfer_success.html", context)
        txt_content = render_to_string("domains_email/transfer_success.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain transfer success',
            body=txt_content,
            to=[user.email],
            bcc=['email-log@as207960.net'],
            reply_to=['Glauca Support <hello@glauca.digital>']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


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

        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "reason": reason,
            "feedback_url": feedback_url,
        }
        html_content = render_to_string("domains_email/transfer_fail.html", context)
        txt_content = render_to_string("domains_email/transfer_fail.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain transfer failure',
            body=txt_content,
            to=[user.email],
            bcc=['email-log@as207960.net'],
            reply_to=['Glauca Support <hello@glauca.digital>']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


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

        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "feedback_url": feedback_url,
        }
        html_content = render_to_string("domains_email/restore_success.html", context)
        txt_content = render_to_string("domains_email/restore_success.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain restore success',
            body=txt_content,
            to=[user.email],
            bcc=['email-log@as207960.net'],
            reply_to=['Glauca Support <hello@glauca.digital>']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


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

        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "reason": reason,
            "feedback_url": feedback_url,
        }
        html_content = render_to_string("domains_email/restore_fail.html", context)
        txt_content = render_to_string("domains_email/restore_fail.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain restore failure',
            body=txt_content,
            to=[user.email],
            bcc=['email-log@as207960.net'],
            reply_to=['Glauca Support <hello@glauca.digital>']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


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

        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "feedback_url": feedback_url,
        }
        html_content = render_to_string("domains_email/transfer_out.html", context)
        txt_content = render_to_string("domains_email/transfer_out.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain transferred out',
            body=txt_content,
            to=[user.email],
            bcc=['email-log@as207960.net'],
            reply_to=['Glauca Support <hello@glauca.digital>']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_transfer_out_request(domain_id):
    domain = models.DomainRegistration.objects\
        .filter(id=domain_id).first()  # type: models.DomainRegistration
    user = domain.get_user()
    if user:
        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "transfer_approve_url":
                settings.EXTERNAL_URL_BASE + reverse('domain_transfer_out', args=(domain.id, "approve")),
            "transfer_reject_url":
                settings.EXTERNAL_URL_BASE + reverse('domain_transfer_out', args=(domain.id, "reject")),
        }
        html_content = render_to_string("domains_email/transfer_out_request.html", context)
        txt_content = render_to_string("domains_email/transfer_out_request.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain transfer request',
            body=txt_content,
            to=[user.email],
            bcc=['email-log@as207960.net'],
            reply_to=['Glauca Support <hello@glauca.digital>']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_auto_renew_redirect(order_id):
    order = models.DomainAutomaticRenewOrder.objects\
        .filter(id=order_id).first()  # type: models.DomainAutomaticRenewOrder
    if order.domain_obj:
        user = order.domain_obj.get_user()
        if user:
            context = {
                "name": user.first_name,
                "domain": order.unicode_domain,
                "subject": f"{order.unicode_domain} renewal - payment required",
                "redirect_url": order.redirect_uri
            }
            html_content = render_to_string("domains_email/renewal_redirect.html", context)
            txt_content = render_to_string("domains_email/renewal_redirect.txt", context)

            email = EmailMultiAlternatives(
                subject=f"{order.unicode_domain} renewal - payment required",
                body=txt_content,
                to=[user.email],
                bcc=['email-log@as207960.net'],
                reply_to=['Glauca Support <hello@glauca.digital>']
            )
            email.attach_alternative(html_content, "text/html")
            email.send()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_auto_renew_failed(order_id):
    order = models.DomainAutomaticRenewOrder.objects\
        .filter(id=order_id).first()  # type: models.DomainAutomaticRenewOrder
    if order.domain_obj:
        user = order.domain_obj.get_user()
        if user:
            context = {
                "name": user.first_name,
                "domain": order.unicode_domain,
                "subject": f"{order.unicode_domain} renewal - payment failed",
                "error": order.last_error
            }
            html_content = render_to_string("domains_email/renewal_failed.html", context)
            txt_content = render_to_string("domains_email/renewal_failed.txt", context)

            email = EmailMultiAlternatives(
                subject=f"{order.unicode_domain} renewal - payment failed",
                body=txt_content,
                to=[user.email],
                bcc=['email-log@as207960.net'],
                reply_to=['Glauca Support <hello@glauca.digital>']
            )
            email.attach_alternative(html_content, "text/html")
            email.send()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_auto_renew_success(order_id):
    order = models.DomainAutomaticRenewOrder.objects\
        .filter(id=order_id).first()  # type: models.DomainAutomaticRenewOrder
    if order.domain_obj:
        user = order.domain_obj.get_user()
        if user:
            context = {
                "name": user.first_name,
                "domain": order.unicode_domain,
                "subject": f"{order.unicode_domain} renewal successful",
            }
            html_content = render_to_string("domains_email/renewal_success.html", context)
            txt_content = render_to_string("domains_email/renewal_success.txt", context)

            email = EmailMultiAlternatives(
                subject=f"{order.unicode_domain} renewal successful",
                body=txt_content,
                to=[user.email],
                bcc=['email-log@as207960.net'],
                reply_to=['Glauca Support <hello@glauca.digital>']
            )
            email.attach_alternative(html_content, "text/html")
            email.send()