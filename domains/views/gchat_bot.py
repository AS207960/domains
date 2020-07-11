from django.http.response import HttpResponse
from django.shortcuts import reverse, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import django_keycloak_auth.clients
import google.oauth2.id_token
import google.oauth2.service_account
import google.auth.transport.requests
import googleapiclient.discovery
import json
import retry
import threading
from .. import models, epp_api
from . import emails, billing

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


def as_thread(fun):
    def new_fun(*args, **kwargs):
        t = threading.Thread(target=fun, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()
    return new_fun


@as_thread
@retry.retry(delay=1, backoff=1.5, max_delay=60)
def request_registration(domain_obj: models.DomainRegistration, registry_id: str, period: epp_api.Period):
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_obj.pk}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} has requested the "
                        f"registration of {domain_obj.domain}",
                "cards": [{
                    "header": {
                        "title": "Domain registration request" if not settings.DEBUG
                        else "Domain registration request [TEST]",
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
                                "content": registry_id
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Period",
                                "content": str(period)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Auth code",
                                "content": domain_obj.auth_info
                            }
                        }]
                    }, {
                        "header": "Contacts",
                        "widgets": [
                            make_contact(domain_obj.registrant_contact, "Registrant"),
                            make_contact(domain_obj.admin_contact, "Admin"),
                            make_contact(domain_obj.tech_contact, "Tech"),
                            make_contact(domain_obj.billing_contact, "Billing")
                        ]
                    }, make_user_data(user), {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "Mark complete",
                                    "onClick": {
                                        "action": {
                                            "actionMethodName": "mark-domain-registered",
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
                                            "actionMethodName": "mark-domain-register-fail",
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
                    "name": f"domain-register-{domain_obj.pk}"
                }]
            }
        ).execute()


@as_thread
@retry.retry(delay=1, backoff=1.5, max_delay=60)
def notify_registration(domain_obj: models.DomainRegistration, registry_id: str, period: epp_api.Period):
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_obj.pk}",
            body={
                "text": f"{user.first_name} {user.last_name} has registered {domain_obj.domain}",
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
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Period",
                                "content": str(period)
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
                    "name": f"domain-register-{domain_obj.pk}"
                }]
            }
        ).execute()


@as_thread
@retry.retry(delay=1, backoff=1.5, max_delay=60)
def request_transfer(domain_obj: models.PendingDomainTransfer, registry_id):
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dt_{domain_obj.pk}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} has requested the "
                        f"transfer of {domain_obj.domain}",
                "cards": [{
                    "header": {
                        "title": "Domain transfer request" if not settings.DEBUG
                        else "Domain transfer request [TEST]",
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
                                "content": registry_id
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Auth code",
                                "content": domain_obj.auth_info
                            }
                        }]
                    }, {
                        "header": "Contacts",
                        "widgets": [
                            make_contact(domain_obj.registrant_contact, "Registrant"),
                            make_contact(domain_obj.admin_contact, "Admin"),
                            make_contact(domain_obj.tech_contact, "Tech"),
                            make_contact(domain_obj.billing_contact, "Billing")
                        ]
                    }, make_user_data(user), {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "Mark complete",
                                    "onClick": {
                                        "action": {
                                            "actionMethodName": "mark-domain-transferred",
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
                                            "actionMethodName": "mark-domain-transfer-fail",
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
                    "name": f"domain-transfer-{domain_obj.pk}",
                }]
            }
        ).execute()


@as_thread
@retry.retry(delay=1, backoff=1.5, max_delay=60)
def notify_transfer_pending(domain_obj: models.PendingDomainTransfer, registry_id: str):
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_transfer_{domain_obj.pk}",
            body={
                "text": f"{user.first_name} {user.last_name} has started the transfer of "
                        f"{domain_obj.domain}",
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
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }]
                    }, make_user_data(user)],
                    "name": f"domain-transfer-{domain_obj.pk}"
                }]
            }
        ).execute()


@as_thread
@retry.retry(delay=1, backoff=1.5, max_delay=60)
def notify_transfer(domain_obj: models.DomainRegistration, registry_id: str):
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_obj.pk}",
            body={
                "text": f"{user.first_name} {user.last_name} has transferred {domain_obj.domain}",
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
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
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
                    "name": f"domain-transfer-{domain_obj.pk}"
                }]
            }
        ).execute()


@as_thread
@retry.retry(delay=1, backoff=1.5, max_delay=60)
def request_restore(domain_obj: models.DomainRegistration):
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dt_{domain_obj.pk}",
            body={
                "text": f"<users/all> {user.first_name} {user.last_name} has requested the "
                        f"restoration of {domain_obj.domain}",
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
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
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
                                                "value": str(domain_obj.pk)
                                            }]
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-restore-{domain_obj.pk}",
                }]
            }
        ).execute()


@as_thread
@retry.retry(delay=1, backoff=1.5, max_delay=60)
def notify_restore(domain_obj: models.DomainRegistration, registry_id: str):
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_obj.pk}",
            body={
                "text": f"{user.first_name} {user.last_name} has restored {domain_obj.domain}",
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
                                "content": domain_obj.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Registry ID",
                                "content": registry_id
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
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
                    "name": f"domain-restore-{domain_obj.pk}"
                }]
            }
        ).execute()


@as_thread
@retry.retry(delay=1, backoff=1.5, max_delay=60)
def notify_renew(domain_obj: models.DomainRegistration, registry_id: str, period: epp_api.Period):
    user = domain_obj.get_user()
    for space in models.HangoutsSpaces.objects.all():
        CHAT_API.spaces().messages().create(
            parent=space.space_id,
            threadKey=f"dm_{domain_obj.pk}",
            body={
                "text": f"{user.first_name} {user.last_name} has renewed {domain_obj.domain}",
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
                                "content": registry_id
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain_obj.pk)
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Period",
                                "content": str(period)
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

    if action_name in ("mark-domain-registered", "mark-domain-register-fail", "mark-domain-restored"):
        domain = models.DomainRegistration.objects.filter(pk=domain_id).first()  # type: models.DomainRegistration
        if not domain:
            return None

        if not domain.has_scope(account_access_token, 'edit'):
            return {
                "text": f"Sowwy <{user_id}>, you don't have permwission to do that"
            }

        if action_name == "mark-domain-registered":
            as_thread(emails.mail_registered)(domain)
            domain.pending = False
            domain.save()

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Registration of {domain.domain} completed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain registration complete",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain.pk)
                            }
                        }]
                    }, {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "View",
                                    "onClick": {
                                        "openLink": {
                                            "url": settings.EXTERNAL_URL_BASE + reverse('domain', args=(domain.pk,))
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-register-{domain.pk}"
                }]
            }
        elif action_name == "mark-domain-register-fail":
            as_thread(billing.reverse_charge)(f"dm_{domain.pk}")
            as_thread(emails.mail_register_failed)(domain)
            domain.delete()

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Registration of {domain.domain} marked failed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain registration failed",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain.id)
                            }
                        }]
                    }],
                    "name": f"domain-register-{domain.id}"
                }]
            }
        elif action_name == "mark-domain-restored":
            as_thread(emails.mail_restored)(domain)
            domain.pending = False
            domain.deleted = False
            domain.save()

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Restore of {domain.domain} marked complete by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain restore complete",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain.id)
                            }
                        }]
                    }],
                    "name": f"domain-restore-{domain.id}"
                }]
            }

    elif action_name in ("mark-domain-transferred", "mark-domain-transfer-fail"):
        domain = models.PendingDomainTransfer.objects.filter(pk=domain_id).first()  # type: models.PendingDomainTransfer
        if not domain:
            return None

        if not domain.has_scope(account_access_token, 'edit'):
            return {
                "text": f"Sowwy <{user_id}>, you don't have permwission to do that"
            }

        if action_name == "mark-domain-transferred":
            as_thread(emails.mail_transferred)(domain)

            new_domain = models.DomainRegistration(
                domain=domain.domain,
                auth_info=None,
                pending=False,
                deleted=False,
                registrant_contact=domain.registrant_contact,
                admin_contact=domain.admin_contact,
                billing_contact=domain.billing_contact,
                tech_contact=domain.tech_contact,
            )
            new_domain.save()
            domain.delete()

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Transfer of {domain.domain} completed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain transfer complete",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": new_domain.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(new_domain.pk)
                            }
                        }]
                    }, {
                        "widgets": [{
                            "buttons": [{
                                "textButton": {
                                    "text": "View",
                                    "onClick": {
                                        "openLink": {
                                            "url": settings.EXTERNAL_URL_BASE + reverse('domain', args=(new_domain.pk,))
                                        }
                                    }
                                }
                            }]
                        }]
                    }],
                    "name": f"domain-transfer-{domain.id}"
                }]
            }
        elif action_name == "mark-domain-transfer-fail":
            as_thread(billing.reverse_charge)(f"dm_transfer_{domain.pk}")
            as_thread(emails.mail_transfer_failed)(domain)
            domain.delete()

            return {
                "actionResponse": {
                    "type": "UPDATE_MESSAGE"
                },
                "text": f"Transfer of {domain.domain} marked failed by <{user_id}>",
                "cards": [{
                    "header": {
                        "title": "Domain transfer failed",
                    },
                    "sections": [{
                        "header": "Domain data",
                        "widgets": [{
                            "keyValue": {
                                "topLabel": "Domain name",
                                "content": domain.domain
                            }
                        }, {
                            "keyValue": {
                                "topLabel": "Object ID",
                                "content": str(domain.id)
                            }
                        }]
                    }],
                    "name": f"domain-transfer-{domain.id}"
                }]
            }
