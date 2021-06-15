from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from django.conf import settings
from django.core import mail
import base64
import logging
import binascii
import json
import email.parser
import uuid
import requests
from .. import models

logger = logging.getLogger(__name__)


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


@csrf_exempt
def postal(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    orig_sig = request.headers.get("X-Postal-Signature")
    if not orig_sig:
        return HttpResponse(status=400)

    try:
        orig_sig = base64.b64decode(orig_sig)
    except binascii.Error:
        return HttpResponse(status=400)

    own_hash = SHA.new()
    own_hash.update(request.body)
    pubkey_bytes = base64.b64decode(settings.POSTAL_PUBLIC_KEY)
    pubkey = RSA.importKey(pubkey_bytes)
    verifier = PKCS1_v1_5.new(pubkey)
    valid_sig = verifier.verify(own_hash, orig_sig)

    if not valid_sig:
        return HttpResponse(status=401)

    try:
        req_body = json.loads(request.body.decode())
    except (json.JSONDecodeError, UnicodeError):
        return HttpResponse(status=400)

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
    message['From'] = "AS207960 Domain Privacy <domain-privacy@as207960.net>"
    message['Reply-To'] = old_from
    message['Subject'] = f"[AS207960 Domain Privacy] {old_subject}"
    print(message)

    new_msg_bytes = message.as_bytes()

    new_message = RawMessage(
        to=[privacy_contact.email], from_email="AS207960 Domain Privacy <domain-privacy@as207960.net>",
        body=new_msg_bytes
    )
    mail.get_connection().send_messages([new_message])

    return HttpResponse(status=200)
