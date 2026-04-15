import django_keycloak_auth.clients
from django.contrib.auth import get_user_model
from rest_framework import viewsets, decorators, status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.conf import settings
from as207960_utils.api import auth
import datetime
import jwt
from . import serializers
from .. import apps, models, tasks


class AccessEPPPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not isinstance(request.auth, auth.OAuthToken):
            return False

        return "access-epp" in request.auth.claims.get("resource_access", {}).get(
            settings.OIDC_CLIENT_ID, {}
        ).get("roles", [])


class AccessUserDomainsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not isinstance(request.auth, auth.OAuthToken):
            return False

        return "access-user-domains" in request.auth.claims.get("resource_access", {}).get(
            settings.OIDC_CLIENT_ID, {}
        ).get("roles", [])


class EPPBalanceViewSet(viewsets.ViewSet):
    permission_classes = [AccessEPPPermission]

    def retrieve(self, request, pk=None):
        info = apps.epp_client.stub.BalanceInfo(apps.epp_api.epp_pb2.RegistryInfo(
            registry_name=pk
        ))
        balance_data = {
            "balance": info.balance,
            "credit_limit": info.credit_limit.value if info.HasField("credit_limit") else None,
            "available_credit": info.available_credit.value if info.HasField("available_credit") else None,
            "fixed_credit_threshold": info.fixed_credit_threshold.value
            if info.HasField("fixed_credit_threshold") else None,
            "percentage_credit_threshold": info.percentage_credit_threshold.value
            if info.HasField("percentage_credit_threshold") else None,
            "currency": info.currency
        }

        serializer = serializers.EPPBalanceSerializer(balance_data, context={'request': request})
        return Response(serializer.data)


class PendingOrderViewSet(viewsets.ViewSet):
    permission_classes = [AccessEPPPermission]

    def list(self, request):
        pending_registration = models.DomainRegistrationOrder.objects.filter(
            state=models.AbstractOrder.STATE_PENDING_APPROVAL).order_by("-timestamp")
        pending_transfer = models.DomainTransferOrder.objects.filter(state=models.AbstractOrder.STATE_PENDING_APPROVAL,
                                                                     last_error__isnull=False).order_by("-timestamp")
        pending_renew = models.DomainRenewOrder.objects.filter(
            state=models.AbstractOrder.STATE_PENDING_APPROVAL).order_by("-timestamp")
        pending_auto_renew = models.DomainAutomaticRenewOrder.objects.filter(
            state=models.AbstractOrder.STATE_PENDING_APPROVAL).order_by("-timestamp")
        pending_restore = models.DomainRestoreOrder.objects.filter(
            state=models.AbstractOrder.STATE_PENDING_APPROVAL).order_by("-timestamp")
        return Response({
            "registration": [serializers.DomainRegistrationOrderSerializer(instance=r, context={
                "request": request
            }).data for r in pending_registration],
            "transfer": [serializers.DomainTransferOrderSerializer(instance=r, context={
                "request": request
            }).data for r in pending_transfer],
            "renew": [serializers.DomainRenewOrderSerializer(instance=r, context={
                "request": request
            }).data for r in pending_renew],
            "auto_renew": [serializers.DomainRenewOrderSerializer(instance=r, context={
                "request": request
            }).data for r in pending_auto_renew],
            "restore": [serializers.DomainRestoreOrderSerializer(instance=r, context={
                "request": request
            }).data for r in pending_restore],
        })


class InProgressOrderViewSet(viewsets.ViewSet):
    permission_classes = [AccessEPPPermission]

    def list(self, request):
        in_progress_transfer = models.DomainTransferOrder.objects.filter(
            state=models.AbstractOrder.STATE_PENDING_APPROVAL, last_error__isnull=True).order_by("-timestamp")
        return Response({
            "transfer": [serializers.DomainTransferOrderSerializer(r).data for r in in_progress_transfer],
        })


class PendingLockViewSet(viewsets.ViewSet):
    permission_classes = [AccessEPPPermission]

    def list(self, request):
        pending_locks = models.DomainRegistration.objects.filter(pending_registry_lock_status__isnull=False)
        return Response({
            "domains": [{
                "domain": r.domain,
                "state": str(models.RegistryLockState(r.pending_registry_lock_status))
            }
                for r in pending_locks],
        })


class DomainLockingViewSet(viewsets.ViewSet):
    permission_classes = [AccessEPPPermission]

    @decorators.action(detail=True, methods=['post'])
    def lock_complete(self, request, pk=None):
        instance = get_object_or_404(models.DomainRegistration, id=pk)

        if not instance.pending_registry_lock_status:
            raise ValidationError("invalid state transition")

        tasks.process_domain_locking_complete.delay(instance.id)
        return Response(status=status.HTTP_202_ACCEPTED)

    @decorators.action(detail=True, methods=['post'])
    def lock_failed(self, request, pk=None):
        instance = get_object_or_404(models.DomainRegistration, id=pk)

        if not instance.pending_registry_lock_status:
            raise ValidationError("invalid state transition")

        tasks.process_domain_locking_failed.delay(instance.id)
        return Response(status=status.HTTP_202_ACCEPTED)


class AdminOrderViewSet(viewsets.ViewSet):
    permission_classes = [AccessEPPPermission]
    order_object = None
    retry_task = None
    complete_task = None
    fail_task = None
    order_serializer = None

    @decorators.action(detail=True, methods=['get'])
    def lookup_pending_by_domain(self, request, pk=None):
        instance = get_object_or_404(self.order_object, domain__iexact=pk,
                                     state=models.AbstractOrder.STATE_PENDING_APPROVAL)
        d = self.order_serializer(data=instance, context={
            "request": request
        })
        return Response(d.data)

    @decorators.action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        instance = get_object_or_404(self.order_object, id=pk)

        if instance.state != models.AbstractOrder.STATE_PENDING_APPROVAL:
            raise ValidationError("invalid state transition")

        h = self.retry_task.delay(instance.id)
        h.get()
        instance.refresh_from_db()
        d = self.order_serializer(data=instance, context={
            "request": request
        })
        return Response(d.data)

    @decorators.action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        instance = get_object_or_404(self.order_object, id=pk)

        if instance.state != models.AbstractOrder.STATE_PENDING_APPROVAL:
            raise ValidationError("invalid state transition")

        self.complete_task.delay(instance.id).forget()
        return Response(status=status.HTTP_202_ACCEPTED)

    @decorators.action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        if "error" not in request.data or not (request.data["error"] is None or isinstance(request.data["error"], str)):
            raise ValidationError({
                "error": "Error must be string or null"
            })

        instance = get_object_or_404(self.order_object, id=pk)

        if instance.state != models.AbstractOrder.STATE_PENDING_APPROVAL:
            raise ValidationError("invalid state transition")

        self.fail_task.delay(
            instance.id, error=request.data["error"],
            silent=bool(request.data.get("silent", False))
        ).forget()
        return Response(status=status.HTTP_202_ACCEPTED)


class DomainRegistrationAdminOrderViewSet(AdminOrderViewSet):
    order_object = models.DomainRegistrationOrder
    retry_task = tasks.process_domain_registration_paid
    complete_task = tasks.process_domain_registration_complete
    fail_task = tasks.process_domain_registration_failed
    order_serializer = serializers.DomainRegistrationOrderSerializer


class DomainTransferAdminOrderViewSet(AdminOrderViewSet):
    order_object = models.DomainTransferOrder
    retry_task = tasks.process_domain_transfer_paid
    complete_task = tasks.process_domain_transfer_complete
    fail_task = tasks.process_domain_transfer_failed
    order_serializer = serializers.DomainTransferOrderSerializer


class DomainRenewAdminOrderViewSet(AdminOrderViewSet):
    order_object = models.DomainRenewOrder
    retry_task = tasks.process_domain_renewal_paid
    complete_task = tasks.process_domain_renewal_complete
    fail_task = tasks.process_domain_renewal_failed
    order_serializer = serializers.DomainRenewOrderSerializer


class DomainAutoRenewAdminOrderViewSet(AdminOrderViewSet):
    order_object = models.DomainAutomaticRenewOrder
    retry_task = tasks.process_domain_auto_renew_paid
    complete_task = tasks.process_domain_auto_renew_complete
    fail_task = tasks.process_domain_auto_renew_failed
    order_serializer = serializers.DomainRenewOrderSerializer


class UserDomainsViewSet(viewsets.ViewSet):
    permission_classes = [AccessUserDomainsPermission]

    def update(self, request, pk=None):
        user = get_object_or_404(get_user_model(), username=pk)
        try:
            token = django_keycloak_auth.clients.get_active_access_token(user.oidc_profile)
        except django_keycloak_auth.clients.TokensExpired:
            out = []
        else:
            serializer = serializers.UserDomainChecksSerializer(data=request.data, context={
                'request': request
            })
            serializer.is_valid(raise_exception=True)

            out = []
            for domain in serializer.validated_data["domains"]:
                domain_obj = models.DomainRegistration.objects \
                    .filter(domain__iexact=domain["domain"], former_domain=False).first()
                if not domain_obj:
                    access = None
                else:
                    access = domain_obj.has_scope(token, 'edit')
                if not access:
                    out.append({
                        "domain": domain["domain"],
                        "domain_id": None,
                        "access": False,
                        "token": None,
                    })
                else:
                    domain_jwt = jwt.encode({
                        "iat": datetime.datetime.utcnow(),
                        "nbf": datetime.datetime.utcnow(),
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
                        "iss": "urn:as207960:domains",
                        "aud": ["urn:as207960:hexdns"],
                        "domain": domain["domain"],
                        "domain_id": str(domain_obj.id),
                        "sub": pk,
                    }, settings.JWT_PRIV_KEY, algorithm='ES256')

                    out.append({
                        "domain": domain["domain"],
                        "access": True,
                        "token": domain_jwt
                    })

        serializer = serializers.UserDomainChecksSerializer({
            "domains": out
        }, context={'request': request})
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['get'])
    def all(self, request, pk=None):
        user = get_object_or_404(get_user_model(), username=pk)
        token = django_keycloak_auth.clients.get_active_access_token(user.oidc_profile)

        out = []
        for domain_obj in models.DomainRegistration.get_object_list(token, 'edit').filter(former_domain=False):
            domain_jwt = jwt.encode({
                "iat": datetime.datetime.now(datetime.UTC),
                "nbf": datetime.datetime.now(datetime.UTC),
                "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=5),
                "iss": "urn:as207960:domains",
                "aud": ["urn:as207960:hexdns"],
                "domain": domain_obj.domain,
                "domain_id": str(domain_obj.id),
                "sub": pk,
            }, settings.JWT_PRIV_KEY, algorithm='ES256')

            out.append({
                "domain": domain_obj.domain,
                "access": True,
                "token": domain_jwt
            })

        serializer = serializers.UserDomainChecksSerializer({
            "domains": out
        }, context={'request': request})
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['get'])
    def lookup_by_domain(self, request, pk=None):
        domain_obj = get_object_or_404(models.DomainRegistration, domain__iexact=pk, former_domain=False)
        return Response({
            "id": domain_obj.id,
        })

    @decorators.action(detail=True, methods=['post'])
    def set_dns(self, request, pk=None):
        domain_obj = get_object_or_404(models.DomainRegistration, id=pk, former_domain=False)
        tasks.set_dns_to_own.delay(domain_obj.id)

        return Response(status=status.HTTP_202_ACCEPTED)
