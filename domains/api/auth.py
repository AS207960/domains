from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
import django_keycloak_auth.clients
import keycloak
import jose.jwt
import dataclasses


class BearerAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return None
        if not token.startswith("Bearer "):
            return None

        token = token[len("Bearer "):]

        try:
            claims = django_keycloak_auth.clients.verify_token(token)
        except keycloak.exceptions.KeycloakClientError:
            raise exceptions.AuthenticationFailed('Invalid token')

        user = get_user_model().objects.filter(username=claims["sub"]).first()

        return user, OAuthToken(token=token, claims=claims)


class SessionAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        user = getattr(request._request, 'user', None)
        if not user or not user.is_active:
            return None
        self.enforce_csrf(request)
        token = django_keycloak_auth.clients.get_active_access_token(user.oidc_profile)

        certs = django_keycloak_auth.clients.get_openid_connect_client().certs()
        try:
            claims = jose.jwt.decode(token, certs, options={
                "verify_aud": False
            })
        except jose.jwt.JWTError:
            raise exceptions.AuthenticationFailed('Invalid token')

        return user, OAuthToken(token=token, claims=claims)

    def enforce_csrf(self, request):
        check = authentication.CSRFCheck()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)


@dataclasses.dataclass
class OAuthToken:
    token: str
    claims: dict
