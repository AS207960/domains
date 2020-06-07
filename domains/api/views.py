from rest_framework import viewsets, exceptions, status, decorators
from rest_framework.response import Response
from rest_framework.settings import api_settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.conf import settings
import grpc
import decimal
from concurrent.futures import ThreadPoolExecutor

from . import serializers, permissions, auth
from .. import models, apps, zone_info
from ..views import billing


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


class Domain(viewsets.ViewSet):
    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        })
        if self.action == "renew":
            return serializers.DomainRenewSerializer(*args, **kwargs)
        elif self.action == "restore":
            return serializers.serializers.Serializer(*args, **kwargs)
        elif self.action == "check":
            return serializers.DomainCheckSerializer(*args, **kwargs)
        elif self.action == "check_renew":
            return serializers.DomainCheckRenewSerializer(*args, **kwargs)
        elif self.action == "check_restore":
            return serializers.DomainCheckRestoreSerializer(*args, **kwargs)
        elif self.request.method == "POST":
            return serializers.DomainCreateSerializer(*args, **kwargs)
        else:
            return serializers.DomainSerializer(*args, **kwargs)

    def list(self, request):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domains = models.DomainRegistration.get_object_list(request.auth.token).filter(pending=False)

        with ThreadPoolExecutor() as executor:
            domains_data = list(executor.map(
                lambda d: serializers.DomainSerializer.get_domain(d, request.user),
                domains
            ))

        serializer = serializers.DomainSerializer(domains_data, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, pending=False)
        if not domain.has_scope(request.auth.token, 'view'):
            raise PermissionDenied

        domain_data = serializers.DomainSerializer.get_domain(domain, request.user)

        serializer = serializers.DomainSerializer(domain_data, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        if not settings.REGISTRATION_ENABLED or not\
                models.DomainRegistration.has_class_scope(request.auth.token, 'create'):
            raise PermissionDenied

        serializer = serializers.DomainCreateSerializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, pending=False)
        if not domain.has_scope(request.auth.token, 'edit'):
            raise PermissionDenied

        serializer = serializers.DomainSerializer(
            serializers.DomainSerializer.get_domain(domain, request.user),
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

        domain = get_object_or_404(models.DomainRegistration, id=pk, pending=False)
        if not domain.has_scope(request.auth.token, 'edit'):
            raise PermissionDenied

        serializer = serializers.DomainSerializer(
            serializers.DomainSerializer.get_domain(domain, request.user),
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

        domain = get_object_or_404(models.DomainRegistration, id=pk, pending=False)
        if not domain.has_scope(request.auth.token, 'delete'):
            raise PermissionDenied

        pending = apps.epp_client.delete_domain(domain.domain)
        domain_info, sld = zone_info.get_domain_info(domain.domain)
        if not (domain_info.restore_supported or not pending):
            domain.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            domain_data = serializers.DomainSerializer.get_domain(domain, request.user)
            serializer = serializers.DomainSerializer(domain_data, context={'request': request})
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @decorators.action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, pending=False)
        if not settings.REGISTRATION_ENABLED or not domain.has_scope(request.auth.token, 'edit'):
            raise PermissionDenied

        zone, _ = zone_info.get_domain_info(domain.domain)
        if not zone:
            raise PermissionDenied

        if not zone.restore_supported:
            raise serializers.Unsupported()

        zone_price, sld = zone.pricing, zone.registry

        billing_value = zone_price.restore(sld)
        billing_error = billing.charge_account(
            request.user.username,
            billing_value,
            f"{domain.domain} domain restore",
            f"dm_{domain.pk}"
        )
        if billing_error:
            raise serializers.BillingError()

        try:
            _pending = apps.epp_client.restore_domain(domain.domain)
        except grpc.RpcError as rpc_error:
            billing.charge_account(
                request.user.username,
                -billing_value,
                f"{domain.domain} domain restore",
                f"dm_{domain.pk}"
            )
            raise rpc_error

        domain_data = serializers.DomainSerializer.get_domain(domain, request.user)
        serializer = serializers.DomainSerializer(domain_data, context={'request': request})
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, pending=False)
        if not settings.REGISTRATION_ENABLED or not domain.has_scope(request.auth.token, 'edit'):
            raise PermissionDenied

        serializer = serializers.DomainRenewSerializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)

        period = serializer.validated_data['period']

        zone, sld = zone_info.get_domain_info(domain.domain)
        if not zone:
            raise PermissionDenied

        if not zone.renew_supported:
            raise serializers.Unsupported()

        domain_data = apps.epp_client.get_domain(domain.domain)
        zone_price, _ = zone.pricing, zone.registry

        period_obj = apps.epp_api.DomainPeriod(
            unit=apps.epp_api.domain_pb2.Period.Unit.Years if period['unit'] == "y"
            else apps.epp_api.domain_pb2.Period.Unit.Months if period['unit'] == "m" else None,
            value=period['value']
        )

        billing_value = zone_price.renewal(sld, unit=period_obj.unit, value=period_obj.value)
        if billing_value is None:
            raise PermissionDenied
        billing_error = billing.charge_account(
            request.user.username,
            billing_value,
            f"{domain.domain} domain renewal",
            f"dm_{domain.pk}"
        )
        if billing_error:
            raise serializers.BillingError()

        try:
            apps.epp_client.renew_domain(domain.domain, period_obj, domain_data.expiry_date)
        except grpc.RpcError as rpc_error:
            billing.charge_account(
                request.user.username,
                -billing_value,
                f"{domain.domain} domain renewal",
                f"dm_{domain.pk}"
            )
            raise rpc_error

        domain_data = serializers.DomainSerializer.get_domain(domain, request.user)
        serializer = serializers.DomainSerializer(domain_data, context={'request': request})
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['post'])
    def check(self, request):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        if not settings.REGISTRATION_ENABLED or not \
                models.DomainRegistration.has_class_scope(request.auth.token, 'create'):
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
                period_unit = apps.epp_api.domain_pb2.Period.Unit.Years if period['unit'] == "y" \
                    else apps.epp_api.domain_pb2.Period.Unit.Months if period['unit'] == "m" else None

                price = zone.pricing.registration(sld, unit=period_unit, value=period['value'])

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

    @decorators.action(detail=True, methods=['post'])
    def check_renew(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, pending=False)
        if not domain.has_scope(request.auth.token, 'view'):
            raise PermissionDenied

        serializer = serializers.DomainCheckRenewSerializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)

        zone, sld = zone_info.get_domain_info(domain.domain)

        if zone.renew_supported:
            period = serializer.validated_data['period']
            period_unit = apps.epp_api.domain_pb2.Period.Unit.Years if period['unit'] == "y" \
                else apps.epp_api.domain_pb2.Period.Unit.Months if period['unit'] == "m" else None

            price = zone.pricing.renew(sld, unit=period_unit, value=period['value'])

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
                reason="Unsupported by the registry",
                price=None
            )

        serializer = serializers.DomainCheckRenewSerializer(data, context={'request': request})
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['get'])
    def check_restore(self, request, pk=None):
        if not isinstance(request.auth, auth.OAuthToken):
            raise PermissionDenied

        domain = get_object_or_404(models.DomainRegistration, id=pk, pending=False)
        if not domain.has_scope(request.auth.token, 'view'):
            raise PermissionDenied

        zone, sld = zone_info.get_domain_info(domain.domain)

        if zone.restore_supported:
            price = zone.pricing.restore(sld)

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
                reason="Unsupported by the registry",
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
