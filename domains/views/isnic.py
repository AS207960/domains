import logging
import email.parser
import base64
import urllib.parse
from django.http import HttpResponse
from . import postal
import requests

logger = logging.getLogger(__name__)


@postal.verify_postal_sig
def postal(_request, req_body):
    msg_to = req_body.get('rcpt_to')
    msg_from = req_body.get('mail_from')
    msg_bytes = base64.b64decode(req_body.get("message"))

    logger.info(
        f"Got ISNIC email webhook; from: {msg_from}, to: {msg_to}"
    )
    message = email.parser.BytesParser(_class=email.message.EmailMessage, policy=email.policy.SMTPUTF8) \
        .parsebytes(msg_bytes)

    msg_body = message.get_body(preferencelist=('plain',))
    if not msg_body:
        return HttpResponse(status=400)

    if message["Subject"].startswith("ISNIC Contact Registration"):
        msg_txt = msg_body.get_content()
        msg_lines = msg_txt.splitlines()
        for line in msg_lines:
            url = urllib.parse.urlparse(line.strip())
            if url.scheme == "https" and url.netloc.endswith("isnic.is"):
                requests.get(url.geturl()).raise_for_status()

        return HttpResponse(status=200)

    else:
        return HttpResponse(status=200)
