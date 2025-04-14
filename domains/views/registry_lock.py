import datetime
import json
import cryptography.hazmat.primitives.serialization
import webauthn
import base64

from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import django_keycloak_auth.clients
from .. import models, zone_info, apps
from ..views import gchat_bot

RP = webauthn.types.RelyingParty(
    id=settings.RP_ID,
    name="Glauca Domains",
    icon="https://as207960.net/assets/img/logo.png"
)
FIDO_METADATA = webauthn.metadata.FIDOMetadata.from_metadata(webauthn.metadata.get_metadata())


def get_user(domain: models.DomainRegistration) -> "webauthn.types.User":
    return webauthn.types.User(
        id=str(domain.id).encode(),
        name=domain.unicode_domain,
        display_name=f"Registry lock",
        icon="https://as207960.net/assets/img/logo.png"
    )


def is_authenticated(request, domain: models.DomainRegistration, registering=False, consume=False) -> bool:
    if registering and domain.webauthn_keys.count() == 0:
        return True

    expiry_key = f"webauthn_expiry_{domain.id}"
    expiry = request.session.get(expiry_key, None)
    if not expiry:
        return False

    expiry = int(request.session[expiry_key])
    now = int(datetime.datetime.utcnow().timestamp())
    if now >= expiry:
        return False

    if consume:
        del request.session[f"webauthn_expiry_{domain.id}"]

    return True


@login_required
def manage_registry_lock(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    domain = apps.epp_client.get_domain(
        user_domain.domain, registry_id=user_domain.registry_id
    )
    domain_info: zone_info.DomainInfo = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit') or not domain_info.registry_lock_supported:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    authenticators = user_domain.webauthn_keys
    can_register = is_authenticated(request, user_domain, registering=True)
    authenticated = is_authenticated(request, user_domain, registering=False)
    can_authenticate = authenticators.count() != 0 and not authenticated

    pending_locking_status = models.RegistryLockState(user_domain.pending_registry_lock_status) \
        if user_domain.pending_registry_lock_status is not None else None
    locking_status = models.RegistryLockState.from_domain(domain)

    key_ids = list(map(lambda k: base64.b64decode(k.key_id), authenticators.all()))

    if can_register:
        options, challenge = webauthn.create_webauthn_credentials(
            rp=RP, user=get_user(user_domain), user_verification=webauthn.types.UserVerification.Required,
            attestation_request=webauthn.types.Attestation.DirectAttestation,
            existing_keys=key_ids
        )
        request.session[f"webauthn_create_challenge_{user_domain.id}"] = challenge
    else:
        options = None

    if can_authenticate:
        login_options, challenge = webauthn.get_webauthn_credentials(
            rp=RP, user_verification=webauthn.types.UserVerification.Required, existing_keys=key_ids
        )
        request.session[f"webauthn_get_challenge_{user_domain.id}"] = challenge
    else:
        login_options = None

    return render(request, "domains/domain_registry_lock.html", {
        "domain": user_domain,
        "registration_data": json.dumps(options) if options else None,
        "authentication_data": json.dumps(login_options) if login_options else None,
        "authenticators": authenticators,
        "can_register": can_register,
        "authenticated": authenticated,
        "can_authenticate": can_authenticate,
        "locking_status": locking_status,
        "pending_locking_status": pending_locking_status,
    })


@login_required
@require_POST
def update(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    domain = apps.epp_client.get_domain(
        user_domain.domain, registry_id=user_domain.registry_id
    )
    domain_info: zone_info.DomainInfo = zone_info.get_domain_info(user_domain.domain, registry_id=user_domain.registry_id)[0]
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')
    can_update = is_authenticated(request, user_domain, consume=True)

    action = request.POST.get("action", None)

    if not user_domain.has_scope(access_token, 'edit') or not can_update \
            or not action or not domain_info.registry_lock_supported or user_domain.pending_registry_lock_status:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    locking_status = models.RegistryLockState.from_domain(domain)

    if action == "lock" and locking_status != models.RegistryLockState.Locked:
        user_domain.pending_registry_lock_status = models.RegistryLockState.Locked.value
        user_domain.save()
        gchat_bot.request_locking_update.delay(user_domain.pk, domain.registry_name)
    elif action == "unlock" and locking_status != models.RegistryLockState.Unlocked:
        user_domain.pending_registry_lock_status = models.RegistryLockState.Unlocked.value
        user_domain.save()
        gchat_bot.request_locking_update.delay(user_domain.pk, domain.registry_name)
    elif action == "temp_unlock" and locking_status == models.RegistryLockState.Locked:
        user_domain.pending_registry_lock_status = models.RegistryLockState.TempUnlock.value
        user_domain.save()
        gchat_bot.request_locking_update.delay(user_domain.pk, domain.registry_name)

    return redirect('domain_registry_lock', user_domain.id)


def map_attestation(result: "webauthn.CreateResult", key_id: str) -> models.WebAuthNKey:
    out = models.WebAuthNKey(
        aaguid=result.aaguid,
        key_id=key_id,
        sign_count=result.sign_count,
        pubkey_alg=result.public_key_alg,
        pubkey=result.public_key.public_bytes(
            cryptography.hazmat.primitives.serialization.Encoding.PEM,
            cryptography.hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
    )
    if result.attestation.mode == webauthn.types.AttestationMode.NoneAttestation:
        raise webauthn.errors.WebAuthnError(message="Authenticator attestation is required")
    elif result.attestation.mode == webauthn.types.AttestationMode.AndroidSafetynet:
        if not result.attestation.safety_net_cts:
            raise webauthn.errors.WebAuthnError(message="Android SafetyNet breached")

        out.name = "Android Device"
        return out
    elif result.attestation.mode == webauthn.types.AttestationMode.Apple:
        out.name = "Apple Passkey"
        return out
    elif result.attestation.mode in (
            webauthn.types.AttestationMode.FIDOU2F,
            webauthn.types.AttestationMode.Packed
    ):
        if result.attestation.type != webauthn.types.AttestationType.AttestationCA:
            raise webauthn.errors.WebAuthnError(message="Unknown attestation CA")

        if result.attestation.fido_metadata.fido_certification_level == \
                webauthn.metadata.FIDOCertification.NotCertified:
            raise webauthn.errors.WebAuthnError(message="Authenticator not FIDO certified")

        if result.attestation.fido_metadata.is_compromised:
            raise webauthn.errors.WebAuthnError(message="Authenticator reported as compromised")

        out.name = result.attestation.fido_metadata.description
        out.icon = result.attestation.fido_metadata.icon
        return out
    else:
        raise webauthn.errors.WebAuthnError(message=f"Unsupported attestation format: {result.attestation.mode.name}")


@login_required
@require_POST
def register_key(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')
    can_register = is_authenticated(request, user_domain, registering=True, consume=True)

    if not user_domain.has_scope(access_token, 'edit') or not can_register:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    challenge = request.session.pop(f"webauthn_create_challenge_{user_domain.id}", None)
    key_id = request.POST.get("key_id", None)
    client_data = request.POST.get("client_data", None)
    attestation = request.POST.get("attestation", None)
    if not challenge or not client_data or not attestation or not key_id:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    try:
        result = webauthn.verify_create_webauthn_credentials(
            rp=RP, challenge_b64=challenge,
            client_data_b64=client_data, attestation_b64=attestation,
            fido_metadata=FIDO_METADATA, user_verification_required=True,
        )
        key_obj = map_attestation(result, key_id)
    except webauthn.errors.WebAuthnError as e:
        return render(request, "domains/error.html", {
            "error": f"Failed to register authenticator: {e.message}",
            "back_url": referrer
        })

    key_obj.domain = user_domain
    key_obj.save()

    return redirect('domain_registry_lock', user_domain.id)


@login_required
@require_POST
def update_key(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')
    can_update = is_authenticated(request, user_domain, consume=True)
    key_id = request.POST.get("key_id", None)
    action = request.POST.get("action", None)

    if not user_domain.has_scope(access_token, 'edit') or not can_update \
            or not key_id or not action:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    key: models.WebAuthNKey = user_domain.webauthn_keys.filter(id=key_id).first()
    if not key:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    if action == "deregister":
        key.delete()

    return redirect('domain_registry_lock', user_domain.id)


@login_required
@require_POST
def authenticate(request, domain_id):
    access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=request.user.oidc_profile)
    user_domain = get_object_or_404(models.DomainRegistration, id=domain_id, deleted=False, former_domain=False)
    referrer = request.META.get("HTTP_REFERER")
    referrer = referrer if referrer else reverse('domains')

    if not user_domain.has_scope(access_token, 'edit'):
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    challenge = request.session.pop(f"webauthn_get_challenge_{user_domain.id}", None)
    key_id = request.POST.get("key_id", None)
    client_data = request.POST.get("client_data", None)
    authenticator = request.POST.get("authenticator", None)
    signature = request.POST.get("signature", None)

    if not challenge or not client_data or not authenticator or not key_id or not signature:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    key: models.WebAuthNKey = user_domain.webauthn_keys.filter(key_id=key_id).first()
    if not key:
        return render(request, "domains/error.html", {
            "error": "You don't have permission to perform this action",
            "back_url": referrer
        })

    pubkey = cryptography.hazmat.primitives.serialization.load_pem_public_key(key.pubkey.encode())

    try:
        result = webauthn.verify_get_webauthn_credentials(
            rp=RP, challenge_b64=challenge,
            client_data_b64=client_data, authenticator_b64=authenticator,
            signature_b64=signature, sign_count=key.sign_count, pubkey_alg=key.pubkey_alg,
            pubkey=pubkey, user_verification_required=True
        )
    except webauthn.errors.WebAuthnError as e:
        return render(request, "domains/error.html", {
            "error": f"Failed to authenticate: {e.message}",
            "back_url": referrer
        })

    key.sign_count = result.sign_count
    key.save()

    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    request.session[f"webauthn_expiry_{user_domain.id}"] = int(expiry.timestamp())

    return redirect('domain_registry_lock', user_domain.id)
