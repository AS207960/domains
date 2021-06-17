from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from django.conf import settings
import base64
import binascii
import json


def verify_postal_sig(inner):
    @csrf_exempt
    def wrapper(request, *args, **kwargs):
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

        return inner(request, req_body, *args, **kwargs)

    return wrapper
