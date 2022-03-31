from rest_framework import viewsets, exceptions, status, decorators, mixins
from rest_framework.response import Response
from rest_framework.settings import api_settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor
import django_keycloak_auth.clients
import jwt
import datetime
from as207960_utils.api import permissions, auth
from . import serializers
from .. import models, apps, zone_info, tasks


class EPPBalanceViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        if "access-epp" not in request.auth.claims.get("resource_access", {}).get(
                settings.OIDC_CLIENT_ID, {}
        ).get("roles", []):
            raise PermissionDenied

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


class UserDomainsViewSet(viewsets.ViewSet):
    def update(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        if "access-user-domains" not in request.auth.claims.get("resource_access", {}).get(
                settings.OIDC_CLIENT_ID, {}
        ).get("roles", []):
            raise PermissionDenied

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
                domain_obj = models.DomainRegistration.objects\
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
                    }, settings.JWT_PRIV_KEY, algorithm='ES384')

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
        if "access-user-domains" not in request.auth.claims.get("resource_access", {}).get(
                settings.OIDC_CLIENT_ID, {}
        ).get("roles", []):
            raise PermissionDenied

        user = get_object_or_404(get_user_model(), username=pk)
        token = django_keycloak_auth.clients.get_active_access_token(user.oidc_profile)

        out = []
        for domain_obj in models.DomainRegistration.get_object_list(token, 'edit').filter(former_domain=False):
            domain_jwt = jwt.encode({
                "iat": datetime.datetime.utcnow(),
                "nbf": datetime.datetime.utcnow(),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
                "iss": "urn:as207960:domains",
                "aud": ["urn:as207960:hexdns"],
                "domain": domain_obj.domain,
                "domain_id": str(domain_obj.id),
                "sub": pk,
            }, settings.JWT_PRIV_KEY, algorithm='ES384')

            out.append({
                "domain": domain_obj.domain,
                "access": True,
                "token": domain_jwt
            })

        serializer = serializers.UserDomainChecksSerializer({
            "domains": out
        }, context={'request': request})
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['post'])
    def set_dns(self, request, pk=None):
        if "access-user-domains" not in request.auth.claims.get("resource_access", {}).get(
                settings.OIDC_CLIENT_ID, {}
        ).get("roles", []):
            raise PermissionDenied

        domain_obj = get_object_or_404(models.DomainRegistration, id=pk, former_domain=False)
        tasks.set_dns_to_own.delay(domain_obj.id)

        return Response(status=status.HTTP_202_ACCEPTED)


class ContactAddressViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ContactAddressSerializer
    queryset = models.ContactAddress.objects.all()
    permission_classes = [permissions.keycloak(models.ContactAddress)]

    def filter_queryset(self, queryset):
        if not isinstance(self.request.auth, auth.OAuthToken):
            raise PermissionDenied

        return models.ContactAddress.get_object_list(self.request.auth.token)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.can_delete():
            instance.delete()
        else:
            raise exceptions.PermissionDenied("Object status prohibits deletion")


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ContactSerializer
    queryset = models.Contact.objects.all()
    permission_classes = [permissions.keycloak(models.Contact)]

    def filter_queryset(self, queryset):
        if not isinstance(self.request.auth, auth.OAuthToken):
            raise PermissionDenied

        return models.Contact.get_object_list(self.request.auth.token)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, created_date=timezone.now())

    def perform_update(self, serializer):
        serializer.save(updated_date=timezone.now())

    def perform_destroy(self, instance):
        if instance.can_delete():
            instance.delete()
        else:
            raise exceptions.PermissionDenied("Object status prohibits deletion")


class DomainRegistrationOrderViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = serializers.DomainRegistrationOrderSerializer
    queryset = models.DomainRegistrationOrder.objects.all()
    permission_classes = [permissions.keycloak(models.DomainRegistrationOrder)]

    def filter_queryset(self, queryset):
        if not isinstance(self.request.auth, auth.OAuthToken):
            raise PermissionDenied

        return models.DomainRegistrationOrder.get_object_list(self.request.auth.token)


class DomainTransferOrderViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = serializers.DomainTransferOrderSerializer
    queryset = models.DomainTransferOrder.objects.all()
    permission_classes = [permissions.keycloak(models.DomainTransferOrder)]

    def filter_queryset(self, queryset):
        if not isinstance(self.request.auth, auth.OAuthToken):
            raise PermissionDenied

        return models.DomainTransferOrder.get_object_list(self.request.auth.token)


class DomainRestoreOrderViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = serializers.DomainRestoreOrderSerializer
    queryset = models.DomainRestoreOrder.objects.all()
    permission_classes = [permissions.keycloak(models.DomainRestoreOrder)]

    def filter_queryset(self, queryset):
        if not isinstance(self.request.auth, auth.OAuthToken):
            raise PermissionDenied

        return models.DomainRestoreOrder.get_object_list(self.request.auth.token)


class DomainRenewOrderViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = serializers.DomainRenewOrderSerializer
    queryset = models.DomainRenewOrder.objects.all()
    permission_classes = [permissions.keycloak(models.DomainRenewOrder)]

    def filter_queryset(self, queryset):
        if not isinstance(self.request.auth, auth.OAuthToken):
            raise PermissionDenied

        return models.DomainRenewOrder.get_object_list(self.request.auth.token)


class Domain(viewsets.ViewSet):
    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        })
        if self.action == "renew":
            return serializers.DomainRenewOrderSerializer(*args, **kwargs)
        elif self.action == "restore":
            return serializers.DomainRestoreOrderSerializer(*args, **kwargs)
        elif self.action == "check":
            return serializers.DomainCheckSerializer(*args, **kwargs)
        elif self.action == "check_transfer":
            return serializers.DomainCheckSerializer(*args, **kwargs)
        elif self.action == "check_renew":
            return serializers.DomainCheckRenewSerializer(*args, **kwargs)
        elif self.action == "check_restore":
            return serializers.DomainCheckRestoreSerializer(*args, **kwargs)
        else:
            return serializers.DomainSerializer(*args, **kwargs)

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def list(self, request):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domains = models.DomainRegistration.get_object_list(request.auth.token).filter(former_domain=False)

        with ThreadPoolExecutor() as executor:
            domains_data = list(executor.map(
                lambda d: serializers.DomainSerializer.get_domain(d, apps.epp_client.get_domain(d.domain), request.user),
                domains
            ))

        serializer = serializers.DomainSerializer(domains_data, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, former_domain=False)
        if not domain.has_scope(request.auth.token, 'view'):
            raise PermissionDenied

        domain_data = apps.epp_client.get_domain(domain.domain)
        domain_data = serializers.DomainSerializer.get_domain(domain, domain_data, request.user)

        serializer = serializers.DomainSerializer(domain_data, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, former_domain=False)
        if not domain.has_scope(request.auth.token, 'edit') or domain.deleted:
            raise PermissionDenied

        domain_data = apps.epp_client.get_domain(domain.domain)
        if not domain_data.can_update:
            raise PermissionDenied

        serializer = serializers.DomainSerializer(
            serializers.DomainSerializer.get_domain(domain, domain_data, request.user),
            data=request.data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, former_domain=False)
        if not domain.has_scope(request.auth.token, 'edit') or domain.deleted:
            raise PermissionDenied

        domain_data = apps.epp_client.get_domain(domain.domain)
        if not domain_data.can_update:
            raise PermissionDenied

        serializer = serializers.DomainSerializer(
            serializers.DomainSerializer.get_domain(domain, domain_data, request.user),
            data=request.data,
            context={
                'request': request
            },
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, former_domain=False)
        if not domain.has_scope(request.auth.token, 'delete') or domain.deleted:
            raise PermissionDenied

        domain_data = apps.epp_client.get_domain(domain.domain)
        if not domain_data.can_delete:
            raise PermissionDenied

        _pending = apps.epp_client.delete_domain(domain.domain)
        domain_info, sld = zone_info.get_domain_info(domain.domain)
        if not domain_info.restore_supported:
            domain.former_domain = True
            domain.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            domain.deleted = True
            domain.deleted_date = timezone.now()
            domain.save()
            domain_data = serializers.DomainSerializer.get_domain(domain, domain_data, request.user)
            serializer = serializers.DomainSerializer(domain_data, context={'request': request})
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @decorators.action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, former_domain=False)
        if not models.DomainRestoreOrder.has_class_scope(request.auth.token, 'create') \
                or not domain.has_scope(request.auth.token, 'edit') or not domain.deleted:
            raise PermissionDenied

        serializer = serializers.DomainRestoreOrderSerializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(domain_obj=domain)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @decorators.action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, former_domain=False)
        if not models.DomainRenewOrder.has_class_scope(request.auth.token, 'create') \
                or not domain.has_scope(request.auth.token, 'edit') or domain.deleted:
            raise PermissionDenied

        domain_data = apps.epp_client.get_domain(domain.domain)
        if not domain_data.can_renew:
            raise PermissionDenied

        serializer = serializers.DomainRenewOrderSerializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(domain_obj=domain)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @decorators.action(detail=False, methods=['post'])
    def check(self, request):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        serializer = serializers.DomainCheckSerializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)

        zone, sld = zone_info.get_domain_info(serializer.validated_data['domain'])
        if zone:
            available, reason, _ = apps.epp_client.check_domain(serializer.validated_data['domain'])
            if not available:
                data = serializers.DomainCheck(
                    available=False,
                    domain=serializer.validated_data['domain'],
                    reason=reason,
                    price=None
                )
            else:
                period = serializer.validated_data['period']
                period_unit = apps.epp_api.common_pb2.Period.Unit.Years if period['unit'] == "y" \
                    else apps.epp_api.common_pb2.Period.Unit.Months if period['unit'] == "m" else None

                price = zone.pricing.registration(
                    "GB", request.user.username, sld, unit=period_unit, value=period['value']
                ).amount

                if price is None:
                    data = serializers.DomainCheck(
                        available=False,
                        domain=serializer.validated_data['domain'],
                        reason="Invalid period for domain",
                        price=None
                    )
                else:
                    data = serializers.DomainCheck(
                        available=True,
                        domain=serializer.validated_data['domain'],
                        reason=None,
                        price=price
                    )
        else:
            data = serializers.DomainCheck(
                available=False,
                domain=serializer.validated_data['domain'],
                reason="Unsupported or invalid domain",
                price=None
            )

        serializer = serializers.DomainCheckSerializer(data, context={'request': request})
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['post'])
    def check_transfer(self, request):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        serializer = serializers.DomainCheckSerializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)

        zone, sld = zone_info.get_domain_info(serializer.validated_data['domain'])
        data = None
        if zone:
            if not zone.transfer_supported:
                data = serializers.DomainCheck(
                    available=False,
                    domain=serializer.validated_data['domain'],
                    reason="Extension not yet supported for transfers",
                    price=None
                )
            else:
                if zone.pre_transfer_query_supported:
                    available, _, _ = apps.epp_client.check_domain(serializer.validated_data['domain'])
                else:
                    available = False

                if not available:
                    if zone.pre_transfer_query_supported:
                        domain_data = apps.epp_client.get_domain(serializer.validated_data['domain'])
                        if any(s in domain_data.statuses for s in (3, 7, 8, 10, 15)):
                            available = False
                            data = serializers.DomainCheck(
                                available=False,
                                domain=serializer.validated_data['domain'],
                                reason="Domain not eligible for transfer",
                                price=None
                            )

                if available:
                    price = zone.pricing.transfer("GB", request.user.username, sld).amount
                    data = serializers.DomainCheck(
                        available=True,
                        domain=serializer.validated_data['domain'],
                        reason=None,
                        price=price
                    )
                else:
                    if not data:
                        data = serializers.DomainCheck(
                            available=False,
                            domain=serializer.validated_data['domain'],
                            reason=None,
                            price=None
                        )
        else:
            data = serializers.DomainCheck(
                available=False,
                domain=serializer.validated_data['domain'],
                reason="Unsupported or invalid domain",
                price=None
            )

        serializer = serializers.DomainCheckSerializer(data, context={'request': request})
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['post'])
    def check_renew(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, former_domain=False)
        if not domain.has_scope(request.auth.token, 'view'):
            raise PermissionDenied

        serializer = serializers.DomainCheckRenewSerializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)

        zone, sld = zone_info.get_domain_info(domain.domain)

        if zone.renew_supported and not domain.deleted:
            period = serializer.validated_data['period']
            period_unit = apps.epp_api.common_pb2.Period.Unit.Years if period['unit'] == "y" \
                else apps.epp_api.common_pb2.Period.Unit.Months if period['unit'] == "m" else None

            price = zone.pricing.renew("GB", request.user.username, sld, unit=period_unit, value=period['value'])

            if price is None:
                data = serializers.DomainCheck(
                    available=False,
                    domain=domain.domain,
                    reason="Invalid period for domain",
                    price=None
                )
            else:
                data = serializers.DomainCheck(
                    available=True,
                    domain=domain.domain,
                    reason=None,
                    price=price
                )
        else:
            data = serializers.DomainCheck(
                available=False,
                domain=domain.domain,
                reason="Unsupported by the registry" if not zone.renew_supported else
                "Domain not in state to be renewed",
                price=None
            )

        serializer = serializers.DomainCheckRenewSerializer(data, context={'request': request})
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['get'])
    def check_restore(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, former_domain=False)
        if not domain.has_scope(request.auth.token, 'view'):
            raise PermissionDenied

        zone, sld = zone_info.get_domain_info(domain.domain)

        if zone.restore_supported and domain.deleted:
            price = zone.pricing.restore("GB", request.user.username, sld).amount

            data = serializers.DomainCheck(
                available=True,
                domain=domain.domain,
                reason=None,
                price=price
            )
        else:
            data = serializers.DomainCheck(
                available=False,
                domain=domain.domain,
                reason="Unsupported by the registry" if not zone.restore_supported else
                "Domain not in state to be restored",
                price=None
            )

        serializer = serializers.DomainCheckRestoreSerializer(data, context={'request': request})
        return Response(serializer.data)


class NameServer(viewsets.ViewSet):
    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        })
        return serializers.NameServerSerializer(*args, **kwargs)

    def list(self, request):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        hosts = models.NameServer.get_object_list(request.auth.token)

        with ThreadPoolExecutor() as executor:
            hosts_data = list(executor.map(
                serializers.NameServerSerializer.get_host,
                hosts
            ))

        serializer = serializers.NameServerSerializer(hosts_data, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        host = get_object_or_404(models.NameServer, id=pk)
        if not host.has_scope(request.auth.token, 'view'):
            raise PermissionDenied

        serializer = serializers.NameServerSerializer(
            serializers.NameServerSerializer.get_host(host),
            context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        serializer = serializers.NameServerSerializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        host = get_object_or_404(models.NameServer, id=pk)
        if not host.has_scope(request.auth.token, 'edit'):
            raise PermissionDenied
        serializer = serializers.NameServerSerializer(
            serializers.NameServerSerializer.get_host(host),
            data=request.data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        host = get_object_or_404(models.NameServer, id=pk)
        if not host.has_scope(request.auth.token, 'edit'):
            raise PermissionDenied

        serializer = serializers.NameServerSerializer(
            serializers.NameServerSerializer.get_host(host),
            data=request.data,
            context={
                'request': request
            },
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        host = get_object_or_404(models.NameServer, id=pk)
        if not host.has_scope(request.auth.token, 'delete'):
            raise PermissionDenied

        pending = apps.epp_client.delete_host(host.name_server, host.registry_id)
        if not pending:
            host.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
