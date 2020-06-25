from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .. import models


def mail_registered(domain: models.DomainRegistration):
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


def mail_register_failed(domain: models.DomainRegistration, reason: str = None):
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


def mail_transferred(domain: models.PendingDomainTransfer):
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


def mail_transfer_failed(domain: models.PendingDomainTransfer, reason: str = None):
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


def mail_restored(domain: models.DomainRegistration):
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
