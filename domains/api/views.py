from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from . import serializers
from .. import models


class ContactAddressViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ContactAddressSerializer

    def get_queryset(self):
        return models.ContactAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ContactSerializer

    def get_queryset(self):
        return models.Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DomainSet(viewsets.ViewSet):
    def list(self, request):
        domains = models.DomainRegistration.objects.filter(user=request.user, pending=False)
        serializer = serializers.DomainSerializer(domains, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        domain = get_object_or_404(models.DomainRegistration, id=pk, pending=False)
        if domain.user != request.user:
            raise PermissionDenied

        serializer = serializers.DomainSerializer(domain, context={'request': request})
        return Response(serializer.data)
