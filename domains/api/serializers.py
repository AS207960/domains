from rest_framework import serializers

from .. import models


class ContactAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactAddress
        fields = ('url', 'id', 'description', 'name', 'organisation', 'street_1', 'street_2', 'street_3', 'city',
                  'province', 'postal_code', 'country_code', 'birthday', 'identity_number', 'disclose_name',
                  'disclose_organisation', 'disclose_address')


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = ('url', 'id', 'description', 'local_address', 'int_address', 'phone', 'phone_ext', 'fax', 'fax_ext',
                  'email', 'entity_type', 'trading_name', 'company_number', 'disclose_phone', 'disclose_fax',
                  'disclose_email')
        read_only_fields = ('created_date', 'updated_date')


class DomainSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(view_name='domain-detail')
    id = serializers.UUIDField()
    domain = serializers.CharField(max_length=255)
    auth_info = serializers.CharField(max_length=255)
