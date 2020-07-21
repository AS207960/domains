from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from celery import shared_task
from .. import models


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def mail_registered(registration_order_id):
    domain = models.DomainRegistrationOrder.objects\
        .filter(pk=registration_order_id).first()  # type: models.DomainRegistrationOrder
    user = domain.get_user()
    if user:
        context = {
            "name": user.first_name,
            "domain": domain.domain,
        }
        html_content = render_to_string("domains_email/register_success.html", context)
        txt_content = render_to_string("domains_email/register_success.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain registration success',
            body=txt_content,
            to=[user.email],
            bcc=['q@as207960.net']
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
        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "reason": reason
        }
        html_content = render_to_string("domains_email/register_fail.html", context)
        txt_content = render_to_string("domains_email/register_fail.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain registration failure',
            body=txt_content,
            to=[user.email],
            bcc=['q@as207960.net']
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
        context = {
            "name": user.first_name,
            "domain": domain.domain,
        }
        html_content = render_to_string("domains_email/transfer_success.html", context)
        txt_content = render_to_string("domains_email/transfer_success.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain transfer success',
            body=txt_content,
            to=[user.email],
            bcc=['q@as207960.net']
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
        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "reason": reason
        }
        html_content = render_to_string("domains_email/transfer_fail.html", context)
        txt_content = render_to_string("domains_email/transfer_fail.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain transfer failure',
            body=txt_content,
            to=[user.email],
            bcc=['q@as207960.net']
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
        context = {
            "name": user.first_name,
            "domain": domain.domain,
        }
        html_content = render_to_string("domains_email/restore_success.html", context)
        txt_content = render_to_string("domains_email/restore_success.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain restore success',
            body=txt_content,
            to=[user.email],
            bcc=['q@as207960.net']
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
        context = {
            "name": user.first_name,
            "domain": domain.domain,
            "reason": reason
        }
        html_content = render_to_string("domains_email/restore_fail.html", context)
        txt_content = render_to_string("domains_email/restore_fail.txt", context)

        email = EmailMultiAlternatives(
            subject='Domain restore failure',
            body=txt_content,
            to=[user.email],
            bcc=['q@as207960.net']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
