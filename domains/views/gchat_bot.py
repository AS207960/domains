from django.http.response import HttpResponse
from django.shortcuts import reverse, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from celery import shared_task
import django_keycloak_auth.clients
import google.oauth2.id_token
import google.oauth2.service_account
import google.auth.transport.requests
import googleapiclient.discovery
import json
from .. import models

REQUEST = google.auth.transport.requests.Request()
CREDENTIALS = google.oauth2.service_account.Credentials.from_service_account_file(
    settings.GCHAT_SERVICE_ACCOUNT, scopes=['https://www.googleapis.com/auth/chat.bot']
)
CHAT_API = googleapiclient.discovery.build('chat', 'v1', credentials=CREDENTIALS, cache_discovery=False)
CHAT_ISSUER = 'chat@system.gserviceaccount.com'
PUBLIC_CERT_URL_PREFIX = 'https://www.googleapis.com/service_accounts/v1/metadata/x509/'
AUDIENCE = settings.GCHAT_PROJECT_ID


def make_contact(contact, label):
    return {
        "keyValue": {
            "topLabel": f"{label} contact",
            "content": contact.description,
            "bottomLabel": str(contact.id),
            "button": {
                "textButton": {
                    "text": "View",
                    "onClick": {
                        "openLink": {
                            "url": settings.EXTERNAL_URL_BASE +
                                   reverse('edit_contact', args=(contact.id,))
                        }
                    }
                }
            }
        }
    } if contact else {
        "keyValue": {
            "topLabel": f"{label} contact",
            "content": "N/A"
        }
    }


def make_user_data(user):
    return {
        "header": "User data",
        "widgets": [{
            "keyValue": {
                "topLabel": "User ID",
                "content": user.username,
            }
        }, {
            "keyValue": {
                "topLabel": "User name",
                "content": f"{user.first_name} {user.last_name}"
            }
        }, {
            "keyValue": {
                "topLabel": "User email",
                "content": user.email
            }
        }]
    }


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def request_registration(registration_order_id, registry_id: str, period: str):
    domain_registration_order = \
        models.DomainRegistrationOrder.objects.get(id=registration_order_id)  # type: models.DomainRegistrationOrder
    user = domain_registration_order.get_user()

    sections = [{
        "header": "Domain data",
        "widgets": [{
            "keyValue": {
                "topLabel": "Domain name",
                "content": domain_registration_order.domain
            }
        }, {
            "keyValue": {
                "topLabel": "Registry ID",
                "content": registry_id if registry_id else "UNKNOWN"
            }
        }, {
            "keyValue": {
                "topLabel": "Object ID",
                "content": str(domain_registration_order.domain_id)
            }
        }, {
            "keyValue": {
                "topLabel": "Period",
                "content": period
            }
        }, {
            "keyValue": {
                "topLabel": "Auth code",
                "content": domain_registration_order.auth_info
            }
        }]
    }, {
        "header": "Contacts",
        "widgets": [
            make_contact(domain_registration_order.registrant_contact, "Registrant"),
            make_contact(domain_registration_order.admin_contact, "Admin"),
            make_contact(domain_registration_order.tech_contact, "Tech"),
            make_contact(domain_registration_order.billing_contact, "Billing")
        ]
    }]
    if domain_registration_order.last_error:
        sections.append({
            "header": "Previous error",
            "widgets": [{
                "textParagraph": {
                    "text": domain_registration_order.last_error
                }
            }]
        })
    sections.extend([make_user_data(user), {
        "widgets": [{
            "buttons": [{
                "textButton": {
                    "text": "Mark complete",
                    "onClick": {
                        "action": {
                            "actionMethodName": "mark-domain-registered",
                            "parameters": [{
                                "key": "domain_id",
                                "value": str(domain_registration_order.pk)
                            }]
                        }
                    }
                }
            }, {
                "textButton": {
                    "text": "Mark failed",
                    "onClick": {
                        "action": {
                            "actionMethodName": "mark-domain-register-fail",
                            "parameters": [{
                                "key": "domain_id",
                                "value": str(domain_registration_order.pk)
                            }]
                        }
                    }
                }
            }]
        }]
    }])

    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_registration_order.domain_id}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} has requested the "
                        f"registration of {domain_registration_order.domain}" + (
                            " which has errored" if domain_registration_order.last_error else ""
                        ),
                "cards": [{
                    "header": {
                        "title": "Domain registration request" if not settings.DEBUG
                        else "Domain registration request [TEST]",
                    },
                    "sections": sections,
                    "name": f"domain-register-{domain_registration_order.domain_id}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def notify_registration(registration_order_id, period: str):
    domain_registration_order = \
        models.DomainRegistrationOrder.objects.get(id=registration_order_id)  # type: models.DomainRegistrationOrder
    user = domain_registration_order.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_registration_order.domain_id}",
            body={
                "text": f"{user.first_name} {user.last_name} has registered {domain_registration_order.domain}",
                "cards": [{
                    "header": {
                        "title": "Domain registration notification" if not settings.DEBUG
                        else "Domain registration notification [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_registration_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_registration_order.domain_id)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Period",
                                "content": period
                            }
                        }]
                    }, make_user_data(user), {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "View",
                                    "onClick": {
                                        "openLink": {
                                            "url": settings.EXTERNAL_URL_BASE + reverse(
                                                'domain', args=(domain_registration_order.domain_obj.pk,))
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-register-{domain_registration_order.domain_obj_id}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def request_transfer(transfer_order_id, registry_id):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder
    user = domain_transfer_order.get_user()

    sections = [{
        "header": "Domain data",
        "widgets": [{
            "keyValue": {
                "topLabel": "Domain name",
                "content": domain_transfer_order.domain
            }
        }, {
            "keyValue": {
                "topLabel": "Registry ID",
                "content": registry_id if registry_id else "UNKNOWN"
            }
        }, {
            "keyValue": {
                "topLabel": "Object ID",
                "content": str(domain_transfer_order.pk)
            }
        }, {
            "keyValue": {
                "topLabel": "Auth code",
                "content": domain_transfer_order.auth_code
            }
        }]
    }, {
        "header": "Contacts",
        "widgets": [
            make_contact(domain_transfer_order.registrant_contact, "Registrant"),
            make_contact(domain_transfer_order.admin_contact, "Admin"),
            make_contact(domain_transfer_order.tech_contact, "Tech"),
            make_contact(domain_transfer_order.billing_contact, "Billing")
        ]
    }]
    if domain_transfer_order.last_error:
        sections.append({
            "header": "Previous error",
            "widgets": [{
                "textParagraph": {
                    "text": domain_transfer_order.last_error
                }
            }]
        })
    sections.extend([make_user_data(user), {
        "widgets": [{
            "buttons": [{
                "textButton": {
                    "text": "Mark complete",
                    "onClick": {
                        "action": {
                            "actionMethodName": "mark-domain-transferred",
                            "parameters": [{
                                "key": "domain_id",
                                "value": str(domain_transfer_order.pk)
                            }]
                        }
                    }
                }
            }, {
                "textButton": {
                    "text": "Mark failed",
                    "onClick": {
                        "action": {
                            "actionMethodName": "mark-domain-transfer-fail",
                            "parameters": [{
                                "key": "domain_id",
                                "value": str(domain_transfer_order.pk)
                            }]
                        }
                    }
                }
            }]
        }]
    }])

    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_transfer_order.domain_id}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} "
                        f"has requested the transfer of {domain_transfer_order.domain}" + (
                            " which has errored" if domain_transfer_order.last_error else ""
                        ),
                "cards": [{
                    "header": {
                        "title": "Domain transfer request" if not settings.DEBUG
                        else "Domain transfer request [TEST]",
                    },
                    "sections": sections,
                    "name": f"domain-transfer-{domain_transfer_order.domain_id}",
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def notify_transfer_pending(transfer_order_id, registry_id: str):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder
    user = domain_transfer_order.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_transfer_order.domain_id}",
            body={
                "text": f"{user.first_name} {user.last_name} "
                        f"has started the transfer of {domain_transfer_order.domain}",
                "cards": [{
                    "header": {
                        "title": "Domain transfer pending notification" if not settings.DEBUG
                        else "Domain transfer pending notification [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_transfer_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id if registry_id else "UNKNOWN"
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_transfer_order.pk)
                            }
                        }]
                    }, make_user_data(user)],
                    "name": f"domain-transfer-{domain_transfer_order.domain_id}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def notify_transfer(transfer_order_id, registry_id: str):
    domain_transfer_order = \
        models.DomainTransferOrder.objects.get(id=transfer_order_id)  # type: models.DomainTransferOrder
    user = domain_transfer_order.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_transfer_order.domain_id}",
            body={
                "text": f"{user.first_name} {user.last_name} has transferred {domain_transfer_order.domain}",
                "cards": [{
                    "header": {
                        "title": "Domain transfer notification" if not settings.DEBUG
                        else "Domain transfer notification [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_transfer_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id if registry_id else "UNKNOWN"
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_transfer_order.domain_id)
                            }
                        }]
                    }, make_user_data(user), {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "View",
                                    "onClick": {
                                        "openLink": {
                                            "url": settings.EXTERNAL_URL_BASE + reverse(
                                                'domain', args=(domain_transfer_order.domain_id,))
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-transfer-{domain_transfer_order.domain_id}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def request_restore(restore_order_id):
    domain_restore_order = models.DomainRestoreOrder.objects.get(id=restore_order_id)  # type: models.DomainRestoreOrder
    user = domain_restore_order.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_restore_order.domain_obj.id}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} has requested the "
                        f"restoration of {domain_restore_order.domain}"
                        f'{"; with renewal" if domain_restore_order.should_renew else ""}',
                "cards": [{
                    "header": {
                        "title": "Domain restore request" if not settings.DEBUG
                        else "Domain restore request [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_restore_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_restore_order.domain_obj.id)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Should renew",
                                "content": str(domain_restore_order.should_renew)
                            }
                        }]
                    }, make_user_data(user), {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "Mark complete",
                                    "onClick": {
                                        "action": {
                                            "actionMethodName": "mark-domain-restored",
                                            "parameters": [{
                                                "key": "domain_id",
                                                "value": str(domain_restore_order.pk)
                                            }]
                                        }
                                    }
                                }
                            }, {
                                "textButton": {
                                    "text": "Mark failed",
                                    "onClick": {
                                        "action": {
                                            "actionMethodName": "mark-domain-restore-fail",
                                            "parameters": [{
                                                "key": "domain_id",
                                                "value": str(domain_restore_order.pk)
                                            }]
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-restore-{domain_restore_order.domain_obj.id}",
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def request_restore_renew(restore_order_id, period: str):
    domain_restore_order = models.DomainRestoreOrder.objects.get(id=restore_order_id)  # type: models.DomainRestoreOrder
    user = domain_restore_order.get_user()

    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_restore_order.domain_obj.id}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} has requested the "
                        f"renewal of {domain_restore_order.domain} following restore",
                "cards": [{
                    "header": {
                        "title": "Domain restore renew request" if not settings.DEBUG
                        else "Domain restore renew request [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_restore_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_restore_order.domain_obj.id)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Period",
                                "content": period
                            }
                        }]
                    }, make_user_data(user), {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "Mark complete",
                                    "onClick": {
                                        "action": {
                                            "actionMethodName": "mark-domain-restored",
                                            "parameters": [{
                                                "key": "domain_id",
                                                "value": str(domain_restore_order.pk)
                                            }]
                                        }
                                    }
                                }
                            }, {
                                "textButton": {
                                    "text": "Mark failed",
                                    "onClick": {
                                        "action": {
                                            "actionMethodName": "mark-domain-restore-fail",
                                            "parameters": [{
                                                "key": "domain_id",
                                                "value": str(domain_restore_order.pk)
                                            }]
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-restore-{domain_restore_order.domain_obj.id}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def notify_restore(restore_order_id):
    domain_restore_order = models.DomainRestoreOrder.objects.get(id=restore_order_id)  # type: models.DomainRestoreOrder
    user = domain_restore_order.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_restore_order.domain_obj.id}",
            body={
                "text": f"{user.first_name} {user.last_name} has restored {domain_restore_order.domain}",
                "cards": [{
                    "header": {
                        "title": "Domain restore notification" if not settings.DEBUG
                        else "Domain restore notification [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_restore_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_restore_order.domain_obj.id)
                            }
                        }]
                    }, make_user_data(user), {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "View",
                                    "onClick": {
                                        "openLink": {
                                            "url": settings.EXTERNAL_URL_BASE + reverse(
                                                'domain', args=(domain_restore_order.domain_obj.id,))
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-restore-{domain_restore_order.domain_obj.id}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def request_renew(renew_order_id, registry_id: str, period: str, auto: bool = False):
    domain_renew_order = models.DomainRenewOrder.objects.get(id=renew_order_id)  # type: models.DomainRenewOrder
    user = domain_renew_order.get_user()

    sections = [{
        "header": "Domain data",
        "widgets": [{
            "keyValue": {
                "topLabel": "Domain name",
                "content": domain_renew_order.domain
            }
        }, {
            "keyValue": {
                "topLabel": "Registry ID",
                "content": registry_id if registry_id else "UNKNOWN"
            }
        }, {
            "keyValue": {
                "topLabel": "Object ID",
                "content": str(domain_renew_order.domain_obj.id)
            }
        }, {
            "keyValue": {
                "topLabel": "Period",
                "content": period
            }
        }]
    }]
    if domain_renew_order.last_error:
        sections.append({
            "header": "Previous error",
            "widgets": [{
                "textParagraph": {
                    "text": domain_renew_order.last_error
                }
            }]
        })
    sections.extend([make_user_data(user), {
        "widgets": [{
            "buttons": [{
                "textButton": {
                    "text": "Mark complete",
                    "onClick": {
                        "action": {
                            "actionMethodName": "mark-domain-auto-renewed" if auto else "mark-domain-renewed",
                            "parameters": [{
                                "key": "domain_id",
                                "value": str(domain_renew_order.pk)
                            }]
                        }
                    }
                }
            }, {
                "textButton": {
                    "text": "Mark failed",
                    "onClick": {
                        "action": {
                            "actionMethodName": "mark-domain-auto-renew-fail" if auto else "mark-domain-renew-fail",
                            "parameters": [{
                                "key": "domain_id",
                                "value": str(domain_renew_order.pk)
                            }]
                        }
                    }
                }
            }]
        }]
    }])

    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_renew_order.domain_obj.id}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} has requested the "
                        f"renewal of {domain_renew_order.domain}" +
                        (" automatically" if auto else "") + (
                            " which has errored" if domain_renew_order.last_error else ""
                        ),
                "cards": [{
                    "header": {
                        "title": "Domain renew request" if not settings.DEBUG
                        else "Domain renew request [TEST]",
                    },
                    "sections": sections,
                    "name": f"domain-renew-{domain_renew_order.domain_obj.id}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def notify_renew(domain_id, registry_id: str, period: str, auto: bool = False):
    domain_obj = \
        models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_obj.pk}",
            body={
                "text": f"{user.first_name} {user.last_name} has renewed {domain_obj.domain}" +
                        (" automatically" if auto else ""),
                "cards": [{
                    "header": {
                        "title": "Domain renew notification" if not settings.DEBUG
                        else "Domain renew notification [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id if registry_id else "UNKNOWN"
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Period",
                                "content": period
                            }
                        }]
                    }, make_user_data(user), {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "View",
                                    "onClick": {
                                        "openLink": {
                                            "url": settings.EXTERNAL_URL_BASE + reverse('domain', args=(domain_obj.pk,))
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-renew-{domain_obj.pk}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def notify_delete(domain_id, registry_id: str):
    domain_obj = models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_obj.pk}",
            body={
                "text": f"{user.first_name} {user.last_name} has deleted {domain_obj.domain}",
                "cards": [{
                    "header": {
                        "title": "Domain delete notification" if not settings.DEBUG
                        else "Domain delete notification [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id if registry_id else "UNKNOWN"
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }]
                    }, make_user_data(user)],
                    "name": f"domain-delete-{domain_obj.pk}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def request_transfer_accept(domain_id, registry_id: str):
    domain_obj = models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_obj.id}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} has requested the "
                        f"acceptance of the transfer out of {domain_obj.domain}",
                "cards": [{
                    "header": {
                        "title": "Domain transfer accept request" if not settings.DEBUG
                        else "Domain transfer accept request [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id if registry_id else "UNKNOWN"
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }]
                    }, make_user_data(user)],
                    "name": f"domain-transfer-accept-{domain_obj.pk}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def request_transfer_reject(domain_id, registry_id: str):
    domain_obj = models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_obj.id}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} has requested the "
                        f"rejection of the transfer out of {domain_obj.domain}",
                "cards": [{
                    "header": {
                        "title": "Domain transfer reject request" if not settings.DEBUG
                        else "Domain transfer reject request [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id if registry_id else "UNKNOWN"
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }]
                    }, make_user_data(user)],
                    "name": f"domain-transfer-reject-{domain_obj.pk}"
                }]
            }
        ).execute()


@shared_task(
    autoretry_for=(Exception,), retry_backoff=1, retry_backoff_max=60, max_retries=None, default_retry_delay=3
)
def request_locking_update(domain_id, registry_id: str):
    domain_obj = models.DomainRegistration.objects.get(id=domain_id)  # type: models.DomainRegistration
    user = domain_obj.get_user()
    lock_status = models.RegistryLockState(domain_obj.pending_registry_lock_status)
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_obj.id}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} has requested to change the registry lock "
                        f"on {domain_obj.domain} to: {str(lock_status)}",
                "cards": [{
                    "header": {
                        "title": "Domain registry lock request" if not settings.DEBUG
                        else "Domain registry lock request [TEST]",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id if registry_id else "UNKNOWN"
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Locking state",
                                "content": str(lock_status)
                            }
                        }]
                    }, make_user_data(user), {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "Mark complete",
                                    "onClick": {
                                        "action": {
                                            "actionMethodName": "mark-domain-locked",
                                            "parameters": [{
                                                "key": "domain_id",
                                                "value": str(domain_obj.pk)
                                            }]
                                        }
                                    }
                                }
                            }, {
                                "textButton": {
                                    "text": "Mark failed",
                                    "onClick": {
                                        "action": {
                                            "actionMethodName": "mark-domain-lock-fail",
                                            "parameters": [{
                                                "key": "domain_id",
                                                "value": str(domain_obj.pk)
                                            }]
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-locking-{domain_obj.pk}"
                }]
            }
        ).execute()


@csrf_exempt
def webhook(request):
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth_header.startswith("Bearer "):
        raise SuspiciousOperation

    bearer_token = auth_header[len("Bearer "):]

    try:
        token = google.oauth2.id_token.verify_token(
            bearer_token, REQUEST, audience=AUDIENCE, certs_url=PUBLIC_CERT_URL_PREFIX + CHAT_ISSUER
        )

        if token['iss'] != CHAT_ISSUER:
            raise SuspiciousOperation
    except Exception:
        raise SuspiciousOperation

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise SuspiciousOperation

    event_type = data.get("type")
    if event_type == "ADDED_TO_SPACE":
        resp_data = added_to_space(data)
    elif event_type == "REMOVED_FROM_SPACE":
        resp_data = removed_from_space(data)
    elif event_type == "MESSAGE":
        resp_data = message_event(data)
    elif event_type == "CARD_CLICKED":
        resp_data = card_clicked(data)
    else:
        resp_data = None

    if resp_data:
        return HttpResponse(json.dumps(resp_data), content_type='application/json')
    else:
        return HttpResponse(status=204)


@login_required
def link_account(request, state_id):
    link_state = get_object_or_404(models.HangoutsUserLinkState, id=state_id)

    account = models.HangoutsUsers.objects.filter(account=request.user).first()
    if not account:
        account = models.HangoutsUsers(account=request.user)

    account.user = link_state.user
    account.save()
    link_state.linked = True
    link_state.save()

    return redirect(link_state.return_url)


def added_to_space(event):
    space = event.get("space", {})
    user = event.get("user", {})
    if space.get("singleUserBotDm", False):
        return None

    space_id = space.get("name")
    user_id = user.get("name")
    if not space_id or not user_id:
        return None

    space_obj = models.HangoutsSpaces(
        space_id=space_id
    )
    space_obj.save()

    return {
        "text": f"Hewowo! Thanks to <{user_id}> for adding me! ^_^"
    }


def removed_from_space(event):
    space = event.get("space", {})
    space_id = space.get("name")
    if not space_id:
        return None

    space_obj = models.HangoutsSpaces.objects.filter(
        space_id=space_id
    ).first()
    if space_obj:
        space_obj.delete()

    return None


def message_event(event):
    user = event.get("user", {})
    user_id = user.get("name", "")
    message = event.get("message", {})
    message_id = message.get("name", "")
    redirect_uri = event.get("configCompleteRedirectUrl", "")

    link_state = models.HangoutsUserLinkState.objects.filter(message_name=message_id, linked=True).first()
    if link_state:
        account = models.HangoutsUsers.objects.filter(user=user_id).first()
        if account:
            link_state.delete()
            return {
                "text": f"Account {account.account.first_name} {account.account.last_name} ({account.account.email}) "
                        f"successfully linked! Uwu!"
            }

    if message.get("argumentText").strip() == "link":
        link_state = models.HangoutsUserLinkState(
            user=user_id,
            message_name=message.get("name", ""),
            return_url=redirect_uri
        )
        link_state.save()
        return {
            "actionResponse": {
                "type": "REQUEST_CONFIG",
                "url": settings.EXTERNAL_URL_BASE + reverse('gchat_account_link', args=(link_state.pk,))
            }
        }


def card_clicked(event):
    from .. import tasks

    action = event.get("action", {})
    action_params = action.get("parameters", [])
    action_name = action.get("actionMethodName")
    user = event.get("user", {})
    user_id = user.get("name")

    account = models.HangoutsUsers.objects.filter(user=user_id).first()
    if not account:
        return {
            "actionResponse": {
                "type": "NEW_MESSAGE"
            },
            "text": f"OwO, what's this <{user_id}>? I don't have an account linked for your user. "
                    f"Pwease send \"link\" to me to setup your account. kthxbye"
        }
    account = account.account
    account_access_token = django_keycloak_auth.clients.get_active_access_token(account.oidc_profile)
    domain_id = next(map(
        lambda p: p.get("value"),
        filter(lambda p: p.get("key") == "domain_id", action_params)
    ), None)

    if action_name in ("mark-domain-registered", "mark-domain-register-fail"):
        domain_registration_order = models.DomainRegistrationOrder.objects \
            .filter(pk=domain_id).first()  # type: models.DomainRegistrationOrder
        if not domain_registration_order:
            return None

        if not domain_registration_order.has_scope(account_access_token, 'edit'):
            return {
                "text": f"Sowwy <{user_id}>, you don't have permwission to do that"
            }

        if action_name == "mark-domain-registered":
            tasks.process_domain_registration_complete.delay(domain_registration_order.id)

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Registration of {domain_registration_order.domain} completed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain registration complete",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_registration_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_registration_order.domain_id)
                            }
                        }]
                    }, {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "View",
                                    "onClick": {
                                        "openLink": {
                                            "url": settings.EXTERNAL_URL_BASE + reverse(
                                                'domain', args=(domain_registration_order.domain_id,))
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-register-{domain_registration_order.domain_id}"
                }]
            }
        elif action_name == "mark-domain-register-fail":
            tasks.process_domain_registration_failed.delay(domain_registration_order.id)

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Registration of {domain_registration_order.domain} marked failed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain registration failed",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_registration_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_registration_order.domain_id)
                            }
                        }]
                    }],
                    "name": f"domain-register-{domain_registration_order.domain_id}"
                }]
            }
    elif action_name in ("mark-domain-restored", "mark-domain-restore-fail"):
        domain_restore_order = models.DomainRestoreOrder.objects \
            .filter(pk=domain_id).first()  # type: models.DomainRestoreOrder
        if not domain_restore_order:
            return None

        if not domain_restore_order.has_scope(account_access_token, 'edit'):
            return {
                "text": f"Sowwy <{user_id}>, you don't have permwission to do that"
            }

        if action_name == "mark-domain-restored":
            tasks.process_domain_restore_complete.delay(domain_restore_order.id)

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Restore of {domain_restore_order.domain} marked complete by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain restore complete",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_restore_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_restore_order.id)
                            }
                        }]
                    }],
                    "name": f"domain-restore-{domain_restore_order.id}"
                }]
            }
        elif action_name == "mark-domain-restore-fail":
            tasks.process_domain_restore_failed.delay(domain_restore_order.id)

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Restore of {domain_restore_order.domain} marked failed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain restore failed",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_restore_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_restore_order.domain_obj.id)
                            }
                        }]
                    }],
                    "name": f"domain-restore-{domain_restore_order.id}"
                }]
            }

    elif action_name in ("mark-domain-renewed", "mark-domain-renew-fail",
                         "mark-domain-auto-renewed", "mark-domain-auto-renew-fail"):
        is_auto = action_name in ("mark-domain-auto-renewed", "mark-domain-auto-renew-fail")
        if is_auto:
            domain_renew_order = models.DomainAutomaticRenewOrder.objects \
                .filter(pk=domain_id).first()  # type: models.DomainAutomaticRenewOrder
        else:
            domain_renew_order = models.DomainRenewOrder.objects \
                .filter(pk=domain_id).first()  # type: models.DomainRenewOrder
        if not domain_renew_order:
            return None

        if not domain_renew_order.has_scope(account_access_token, 'edit'):
            return {
                "text": f"Sowwy <{user_id}>, you don't have permwission to do that"
            }

        if action_name in ("mark-domain-renewed", "mark-domain-auto-renewed"):
            if is_auto:
                tasks.process_domain_auto_renew_complete.delay(domain_renew_order.id)
            else:
                tasks.process_domain_renewal_complete.delay(domain_renew_order.id)

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Renewal of {domain_renew_order.domain} marked complete by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain renewal complete",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_renew_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_renew_order.domain_obj.id)
                            }
                        }]
                    }],
                    "name": f"domain-renew-{domain_renew_order.id}"
                }]
            }
        elif action_name in ("mark-domain-renew-fail", "mark-domain-auto-renew-fail"):
            if is_auto:
                tasks.process_domain_auto_renew_failed.delay(domain_renew_order.id)
            else:
                tasks.process_domain_renewal_failed.delay(domain_renew_order.id)

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Renewal of {domain_renew_order.domain} marked failed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain renewal failed",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_renew_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_renew_order.domain_obj.id)
                            }
                        }]
                    }],
                    "name": f"domain-renew-{domain_renew_order.id}"
                }]
            }

    elif action_name in ("mark-domain-transferred", "mark-domain-transfer-fail"):
        domain_transfer_order = models.DomainTransferOrder.objects \
            .filter(pk=domain_id).first()  # type: models.DomainTransferOrder
        if not domain_transfer_order:
            return None

        if not domain_transfer_order.has_scope(account_access_token, 'edit'):
            return {
                "text": f"Sowwy <{user_id}>, you don't have permwission to do that"
            }

        if action_name == "mark-domain-transferred":
            tasks.process_domain_transfer_complete.delay(domain_transfer_order.id)

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Transfer of {domain_transfer_order.domain} completed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain transfer complete",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_transfer_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_transfer_order.domain_id)
                            }
                        }]
                    }, {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "View",
                                    "onClick": {
                                        "openLink": {
                                            "url": settings.EXTERNAL_URL_BASE + reverse(
                                                'domain', args=(domain_transfer_order.domain_id,))
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-transfer-{domain_transfer_order.domain_id}"
                }]
            }
        elif action_name == "mark-domain-transfer-fail":
            tasks.process_domain_transfer_failed.delay(domain_transfer_order.id)

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Transfer of {domain_transfer_order.domain} marked failed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain transfer failed",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_transfer_order.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_transfer_order.domain_id)
                            }
                        }]
                    }],
                    "name": f"domain-transfer-{domain_transfer_order.domain_id}"
                }]
            }

    elif action_name in ("mark-domain-locked", "mark-domain-lock-fail"):
        domain_obj = models.DomainRegistration.objects \
            .filter(pk=domain_id).first()  # type: models.DomainRegistration
        if not domain_obj:
            return None

        if not domain_obj.has_scope(account_access_token, 'edit'):
            return {
                "text": f"Sowwy <{user_id}>, you don't have permwission to do that"
            }

        to_state = str(models.RegistryLockState(domain_obj.pending_registry_lock_status))

        if action_name == "mark-domain-locked":
            tasks.process_domain_locking_complete.delay(domain_obj.id)

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Locking update of {domain_obj.domain} completed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain locking complete",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Locking state",
                                "content": to_state
                            }
                        }]
                    }],
                    "name": f"domain-locking-{domain_obj.pk}"
                }]
            }
        elif action_name == "mark-domain-lock-fail":
            tasks.process_domain_locking_failed.delay(domain_obj.id)

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Locking update of {domain_obj.domain} marked failed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain locking failed",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Locking state",
                                "content": to_state
                            }
                        }]
                    }],
                    "name": f"domain-locking-{domain_obj.pk}"
                }]
            }
