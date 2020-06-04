from rest_framework import viewsets, exceptions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor

from . import serializers, permissions
from .. import models, apps

class ContactAddressViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ContactAddressSerializer
    queryset = models.ContactAddress.objects.all()
    permission_classes = [permissions.IsOwner]

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)

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
    permission_classes = [permissions.IsOwner]

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, created_date=timezone.now())

    def perform_update(self, serializer):
        serializer.save(updated_date=timezone.now())

    def perform_destroy(self, instance):
        if instance.can_delete():
            instance.delete()
        else:
            raise exceptions.PermissionDenied("Object status prohibits deletion")


class DomainSet(viewsets.ViewSet):
    def list(self, request):
        if not request.user.is_authenticated:
            raise PermissionDenied

        domains = models.DomainRegistration.objects.filter(user=request.user, pending=False)

        with ThreadPoolExecutor() as executor:
            domains_data = list(executor.map(
                lambda d: serializers.DomainSerializer.get_domain(d, request.user),
                domains
            ))

        serializer = serializers.DomainSerializer(domains_data, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        domain = get_object_or_404(models.DomainRegistration, id=pk, pending=False)
        if domain.user != request.user:
            raise PermissionDenied

        domain_data = serializers.DomainSerializer.get_domain(domain, request.user)

        serializer = serializers.DomainSerializer(domain_data, context={'request': request})
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
        if not request.user.is_authenticated:
            raise PermissionDenied

        hosts = models.NameServer.objects.filter(user=request.user)

        with ThreadPoolExecutor() as executor:
            hosts_data = list(executor.map(
                serializers.NameServerSerializer.get_host,
                hosts
            ))

        serializer = serializers.NameServerSerializer(hosts_data, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        host = get_object_or_404(models.NameServer, id=pk)
        if host.user != request.user:
            raise PermissionDenied

        serializer = serializers.NameServerSerializer(
            serializers.NameServerSerializer.get_host(host),
            context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request):
        serializer = serializers.NameServerSerializer(data=request.data, context={
            'request': request
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, pk=None):
        host = get_object_or_404(models.NameServer, id=pk)
        if host.user != request.user:
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

    def destroy(self, request, pk=None):
        host = get_object_or_404(models.NameServer, id=pk)
        if host.user != request.user:
            raise PermissionDenied

        pending = apps.epp_client.delete_host(host.name_server, host.registry_id)
        if not pending:
            host.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
