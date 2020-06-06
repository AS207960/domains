from rest_framework import viewsets, exceptions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor

from . import serializers, permissions, auth
from .. import models, apps


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

        if not models.NameServer.has_class_scope(request.auth.token, 'create'):
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
