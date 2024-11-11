from django.http import HttpResponse
from django.conf import settings
from django.core import mail
import base64
import logging
import email.parser
import uuid
import requests
import re
import urllib.parse
from .. import models
from . import postal

logger = logging.getLogger(__name__)
owner_change_re = re.compile(r"^https://icann-transfers.key-systems.net/\?.*trigger=(?P<code>[^&]+).*$")

class RawMessageBody:
    def __init__(self, body):
        self.body = body

    def get_charset(self):
        return None

    def as_bytes(self, *_args, **_kwargs):
        return self.body


class RawMessage:
    encoding = None

    def __init__(self, to, body: bytes, from_email=None):
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        self.to = to
        self.body = body

    def recipients(self):
        return self.to

    def message(self):
        return RawMessageBody(self.body)


@postal.verify_postal_sig
def postal(_request, req_body):
    msg_to = req_body.get('rcpt_to')
    msg_from = req_body.get('mail_from')
    msg_bytes = base64.b64decode(req_body.get("message"))

    logger.info(
        f"Got email webhook; from: {msg_from}, to: {msg_to}"
    )
    message = email.parser.BytesParser(_class=email.message.EmailMessage, policy=email.policy.SMTPUTF8) \
        .parsebytes(msg_bytes)

    trigger_found = False
    if msg_from in ("noreply@emailverification.info", "noreply@icann.glauca.digital"):
        msg_body = message.get_body(preferencelist=('plain',))
        if msg_body:
            msg_txt = msg_body.get_content()
            msg_lines = msg_txt.splitlines()
            for line in msg_lines:
                if line.startswith("trigger = "):
                    trigger = line[len("trigger = "):]
                    r = requests.get(
                        "https://api.rrpproxy.net/api/call",
                        params={
                            "s_login": settings.RRPPROXY_USER,
                            "s_pw": settings.RRPPROXY_PASS,
                            "command": "activatecontact",
                            "trigger": trigger
                        }
                    )
                    r.raise_for_status()
                    trigger_found = True

                if line.startswith("https://icann-transfers.key-systems.net"):
                    m = owner_change_re.match(line)
                    if m:
                        trigger = urllib.parse.unquote(m['code'])
                        r = requests.get(
                            "https://api.rrpproxy.net/api/call",
                            params={
                                "s_login": settings.RRPPROXY_USER,
                                "s_pw": settings.RRPPROXY_PASS,
                                "command": "ActivateOwnerChange",
                                "action": "APPROVE",
                                "trigger": trigger,
                                "transferlock": "0"
                            }
                        )
                        r.raise_for_status()
                        trigger_found = True

    if trigger_found:
        return HttpResponse(status=200)

    privacy_id = msg_to.split("@")[0]
    try:
        privacy_id = uuid.UUID(privacy_id)
    except ValueError:
        logger.warning("Invalid UUID recipient")
        return HttpResponse(status=200)

    privacy_contact = models.Contact.objects.filter(privacy_email=privacy_id).first()
    if not privacy_contact:
        logger.warning("Unknown privacy email")
        return HttpResponse(status=200)

    del message['Received']
    del message['ARC-Seal']
    del message['ARC-Message-Signature']
    del message['ARC-Authentication-Results']
    del message['Received-SPF']
    del message['Authentication-Results']
    del message['DKIM-Signature']

    old_from = message['From']
    old_subject = message['Subject']
    del message['From']
    del message['Reply-To']
    del message['Subject']
    del message['x-postal-spam-threshold']
    del message['x-postal-spam-score']
    del message['x-postal-threat']
    message['From'] = "Glauca Domain Privacy <domain-privacy@as207960.net>"
    message['Reply-To'] = old_from

    if message.get('x-postal-spam', 'no') == 'yes':
        message['Subject'] = f"[SPAM - Glauca Domain Privacy] {old_subject}"
    else:
        message['Subject'] = f"[Glauca Domain Privacy] {old_subject}"

    del message['x-postal-spam']

    new_msg_bytes = message.as_bytes()

    new_message = RawMessage(
        to=[privacy_contact.email], from_email="Glauca Domain Privacy <domain-privacy@as207960.net>",
        body=new_msg_bytes
    )
    mail.get_connection().send_messages([new_message])

    return HttpResponse(status=200)
