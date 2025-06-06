import datetime
import crispy_forms.bootstrap
import crispy_forms.helper
import crispy_forms.layout
import django_keycloak_auth.clients
from phonenumber_field.formfields import PhoneNumberField
from django import forms
from django.urls import reverse
from django.core import validators
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.core.exceptions import ValidationError
from . import models, apps, zone_info


class ContactForm(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=user.oidc_profile)
        self.fields['description'].help_text = "Something descriptive of the contact so you can find it later"
        self.fields['local_address'].help_text = "The address in the local format, usually the only one required"
        self.fields['int_address'].help_text = "The Latinised version of the address, usually not required"
        self.fields['phone'].help_text = \
            "A phone number the contact can be reached at, in international format (e.g. +44 29 2010 2455)"
        self.fields['phone_ext'].help_text = \
            "If the contact is on an internal extension of the contact number, please provide it here"
        self.fields['fax'].help_text =\
            "A phone number for the contact's fax machine, in international format (e.g. +44 29 2010 2455)"
        self.fields['phone_ext'].help_text = \
            "If the contact's fax machine is on an internal extension of the fax number, please provide it here"
        self.fields['entity_type'].help_text = "What legal form does the contact have?"
        self.fields['trading_name'].help_text = "Only required for entities conducting business"
        self.fields['company_number'].help_text = "Only required for legal entities on a government register"
        self.fields['local_address'].queryset = models.ContactAddress.get_object_list(access_token)
        self.fields['int_address'].queryset = models.ContactAddress.get_object_list(access_token)
        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'description',
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Address',
                crispy_forms.layout.HTML("""
                    <div class="alert alert-info" role="alert">
                        Manage addresses <a href="{% url 'addresses' %}" class="alert-link">here</a>
                    </div>
                """),
                'local_address',
                'int_address',
            ),
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Voice phone number',
                'phone',
                'phone_ext'
            ),
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Fax phone number',
                'fax',
                'fax_ext'
            ),
            crispy_forms.layout.HTML("<hr/>"),
            'email',
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Entity information',
                'entity_type',
                'trading_name',
                'company_number'
            ),
            crispy_forms.layout.Fieldset(
                'WHOIS Disclosure',
                crispy_forms.layout.HTML("""
                    <div class="alert alert-info" role="alert">
                        More info <a href="https://docs.glauca.digital/domains/email-privacy/" class="alert-link">here</a>
                    </div>
                """),
                'disclose_phone',
                'disclose_fax',
                'disclose_email'
            )
        )
        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Submit'))

    class Meta:
        model = models.Contact
        fields = "__all__"
        exclude = ("id", "resource_id", "created_date", "updated_date", "privacy_email", "handle", "eurid_citizenship")


class AddressForm(forms.ModelForm):
    def __init__(self, *args, show_fi=True, **kwargs):
        super().__init__(*args, **kwargs)
        this_year = datetime.date.today().year
        self.fields['description'].help_text = "Something descriptive of the address so you can find it later"
        self.fields['name'].help_text = \
            "Your own name if acting as an individual, or the representative's name from the organisation. " \
            "This need not be the name on your government-issued ID."
        self.fields['birthday'].widget = forms.SelectDateWidget(years=range(this_year - 99, this_year))
        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9 my-1'
        layout = [
            'description',
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Contact information',
                'name',
                'organisation',
            )
        ]
        if show_fi:
            layout.append(crispy_forms.layout.Fieldset(
                'Personal information',
                crispy_forms.layout.HTML("""
                    <div class="alert alert-info" role="alert">
                        Birthday is required for foreign personal registrants under the .fi domain<br/>
                        National identity number is required for Finnish registrants under the .fi domain<br/>
                    </div>
                """),
                'birthday',
                'identity_number',
            ))

        layout.extend([
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Address',
                'street_1',
                'street_2',
                'street_3',
                'city',
                'province',
                'postal_code',
                'country_code'
            ),
            crispy_forms.layout.Fieldset(
                'WHOIS Disclosure',
                crispy_forms.layout.HTML("""
                    <div class="alert alert-info" role="alert">
                        More info <a href="https://docs.glauca.digital/domains/email-privacy/" target="_blank" class="alert-link">here</a>
                    </div>
                """),
                'disclose_name',
                'disclose_organisation',
                'disclose_address'
            )
        ])

        self.helper.layout = crispy_forms.layout.Layout(*layout)

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Submit'))

    class Meta:
        model = models.ContactAddress
        fields = "__all__"
        widgets = {'country_code': CountrySelectWidget(
            layout="""
            <div class="input-group input-group-sm">
                {widget}
                    <span class="input-group-text">
                        <img class="country-select-flag" id="{flag_id}" src="{country.flag}">
                    </span>
            </div>
            """
        )}
        exclude = ("id", "resource_id")


class ContactAndAddressForm(forms.Form):
    description = forms.CharField(
        max_length=255, help_text="Something descriptive of the contact so you can find it later"
    )
    name = forms.CharField(
        max_length=255, validators=[validators.MinLengthValidator(4)],
        help_text=(
            "Your own name if acting as an individual, or the representative's name from the organisation. "
            "This need not be the name on your government-issued ID."
        )
    )
    birthday = forms.DateField(required=False)
    identity_number = forms.CharField(max_length=255, required=False, label="National identity number")
    organisation = forms.CharField(max_length=255, required=False)
    street_1 = forms.CharField(max_length=255, label="Address line 1")
    street_2 = forms.CharField(max_length=255, required=False, label="Address line 2")
    street_3 = forms.CharField(max_length=255, required=False, label="Address line 3")
    city = forms.CharField(max_length=255)
    province = forms.CharField(max_length=255, required=False)
    postal_code = forms.CharField(max_length=255)
    country_code = CountryField().formfield(label="Country", widget=CountrySelectWidget(
        layout="""
            <div class="input-group input-group-sm">
                {widget}
                    <span class="input-group-text">
                        <img class="country-select-flag" id="{flag_id}" src="{country.flag}">
                    </span>
            </div>
            """
    ))
    phone = PhoneNumberField(
        help_text="A phone number the contact can be reached at, in international format (e.g. +44 29 2010 2455)"
    )
    phone_ext = forms.CharField(
        max_length=64, required=False, label="Phone extension",
        help_text="If the contact is on an internal extension of the contact number, please provide it here"
    )
    fax = PhoneNumberField(
        required=False,
        help_text="A phone number for the contact's fax machine, in international format (e.g. +44 29 2010 2455)"
    )
    fax_ext = forms.CharField(
        max_length=64, required=False, label="Fax extension",
        help_text="If the contact's fax machine is on an internal extension of the fax number, please provide it here"
    )
    email = forms.EmailField()
    entity_type = forms.IntegerField(
        widget=forms.Select(choices=models.Contact.ENTITY_TYPES),
        help_text="What legal form does the contact have?"
    )
    trading_name = forms.CharField(
        max_length=255, required=False, help_text="Only required for entities conducting business"
    )
    company_number = forms.CharField(
        max_length=255, required=False, help_text="Only required for legal entities on a government register"
    )
    disclose_name = forms.BooleanField(required=False)
    disclose_organisation = forms.BooleanField(required=False)
    disclose_address = forms.BooleanField(required=False)
    disclose_phone = forms.BooleanField(required=False)
    disclose_fax = forms.BooleanField(required=False)
    disclose_email = forms.BooleanField(required=False)

    def __init__(self, *args, show_fi=True, **kwargs):
        super().__init__(*args, **kwargs)
        this_year = datetime.date.today().year
        self.fields['birthday'].widget = forms.SelectDateWidget(years=range(this_year - 99, this_year))
        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9 my-1'
        layout = [
            'description',
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Contact information',
                'name',
                'organisation',
            )
        ]
        if show_fi:
            layout.append(crispy_forms.layout.Fieldset(
                'Personal information',
                crispy_forms.layout.HTML("""
                    <div class="alert alert-info" role="alert">
                        Birthday is required for foreign personal registrants under the .fi domain<br/>
                        National identity number is required for Finnish registrants under the .fi domain<br/>
                    </div>
                """),
                'birthday',
                'identity_number',
            ))

        layout.extend([
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Address',
                'street_1',
                'street_2',
                'street_3',
                'city',
                'province',
                'postal_code',
                'country_code'
            ),
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Voice phone number',
                'phone',
                'phone_ext'
            ),
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Fax phone number',
                'fax',
                'fax_ext'
            ),
            crispy_forms.layout.HTML("<hr/>"),
            'email',
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Entity information',
                'entity_type',
                'trading_name',
                'company_number'
            ),
            crispy_forms.layout.Fieldset(
                'WHOIS Disclosure',
                crispy_forms.layout.HTML("""
                    <div class="alert alert-info" role="alert">
                        More info <a href="https://docs.glauca.digital/domains/email-privacy/" target="_blank" class="alert-link">here</a>
                    </div>
                """),
                'disclose_name',
                'disclose_organisation',
                'disclose_address',
                'disclose_phone',
                'disclose_fax',
                'disclose_email'
            )
        ])

        self.helper.layout = crispy_forms.layout.Layout(*layout)

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Submit'))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["country_code"] == "GB" and not models.UK_POSTCODE_RE.match(cleaned_data["postal_code"]):
            raise ValidationError({
                "postal_code": "Invalid postcode"
            })


class DomainContactForm(forms.Form):
    contact = forms.ModelChoiceField(queryset=None, label="Set new contact", required=False)
    type = forms.CharField()

    def __init__(self, *args, user, contact_type, domain_id, **kwargs):
        super().__init__(*args, **kwargs)
        access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=user.oidc_profile)
        self.fields['contact'].queryset = models.Contact.get_object_list(access_token)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = reverse('update_domain_contact', args=(domain_id,))
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'contact',
            crispy_forms.layout.Hidden('type', contact_type)
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Save', css_class='btn-block'))

    def set_cur_id(self, cur_id, registry_id):
        reg_contact = models.ContactRegistry.objects.filter(registry_contact_id=cur_id, registry_id=registry_id).first()
        if reg_contact:
            self.fields['contact'].value = reg_contact.contact.id


class DomainHostObjectForm(forms.Form):
    host = forms.CharField(max_length=63, label="Host name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'ns1.example.com'}
    ))

    def __init__(self, *args, domain_id, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = reverse('add_domain_host_obj', args=(domain_id,))
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'host',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Add', css_class="btn-block"))


class BaseDomainHostObjectFormSet(forms.BaseFormSet):
    def __init__(self, *args, domain_id, **kwargs):
        super().__init__(*args, **kwargs)

        self.domain_id = domain_id
        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = reverse('add_domain_host_obj', args=(domain_id,))
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'host',
        )

        self.helper.add_input(crispy_forms.layout.Submit('action', 'Add', css_class="btn-block"))
        self.helper.add_input(crispy_forms.layout.Submit('action', 'Replace', css_class="btn-block"))

    def get_form_kwargs(self, index):
        kwargs = self.form_kwargs.copy()
        kwargs["domain_id"] = self.domain_id
        return kwargs


DomainHostObjectFormSet = forms.formset_factory(
    DomainHostObjectForm, min_num=1, validate_min=True, extra=3, formset=BaseDomainHostObjectFormSet
)


class DomainHostAddrForm(forms.Form):
    host = forms.CharField(max_length=63, label="Host name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'ns1.example.com'}
    ))
    v4_address = forms.GenericIPAddressField(label="IPv4 Address", required=False, widget=forms.TextInput(
        attrs={'placeholder': '192.0.2.2'}
    ), help_text="Only required for glue records", protocol="ipv4")
    v6_address = forms.GenericIPAddressField(label="IPv6 Address", required=False, widget=forms.TextInput(
        attrs={'placeholder': '2001:db8:8:4::2'}
    ), help_text="Only required for glue records", protocol="ipv6")

    def __init__(self, *args, domain_id, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = reverse('add_domain_host_addr', args=(domain_id,))
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'host',
            'v4_address',
            'v6_address'
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Add', css_class="btn-block"))


class DomainDSDataForm(forms.Form):
    ALGORITHMS = (
        (5, "RSA/SHA-1 (5) INSECURE"),
        (7, "RSASHA1-NSEC3-SHA1 (7) INSECURE"),
        (8, "RSA/SHA-256 (8)"),
        (10, "RSA/SHA-512 (10) NOT RECOMMENDED"),
        (12, "GOST R 34.10-2001 (12)"),
        (13, "ECDSA Curve P-256 with SHA-256 (13)"),
        (14, "ECDSA Curve P-384 with SHA-384 (14)"),
        (15, "Ed25519 (15)"),
        (16, "Ed448 (16)"),
        (253, "Private Algorithm - Domain Name (254)"),
        (254, "Private Algorithm - OID (254)"),
    )

    DIGEST_TYPES = (
        (1, "SHA-1 (1) INSECURE"),
        (2, "SHA-256 (2)"),
        (4, "SHA-384 (4)")
    )

    key_tag = forms.IntegerField(min_value=0, max_value=65535, required=True)
    algorithm = forms.TypedChoiceField(choices=ALGORITHMS, coerce=int, empty_value=0, required=True)
    digest_type = forms.TypedChoiceField(choices=DIGEST_TYPES, coerce=int, empty_value=0, required=True)
    digest = forms.CharField(required=True)

    def __init__(self, *args, domain_id, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = reverse('add_domain_ds_data', args=(domain_id,))
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'key_tag',
            'algorithm',
            'digest_type',
            'digest'
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Add', css_class="btn-block"))


class DomainDNSKeyDataForm(forms.Form):
    ALGORITHMS = (
        (5, "RSA/SHA-1 (5) INSECURE"),
        (7, "RSASHA1-NSEC3-SHA1 (7) INSECURE"),
        (8, "RSA/SHA-256 (8)"),
        (10, "RSA/SHA-512 (10) NOT RECOMMENDED"),
        (12, "GOST R 34.10-2001 (12)"),
        (13, "ECDSA Curve P-256 with SHA-256 (13)"),
        (14, "ECDSA Curve P-384 with SHA-384 (14)"),
        (15, "Ed25519 (15)"),
        (16, "Ed448 (16)"),
        (253, "Private Algorithm - Domain Name (254)"),
        (254, "Private Algorithm - OID (254)"),
    )

    flags = forms.IntegerField(min_value=0, max_value=65535, required=True)
    protocol = forms.IntegerField(min_value=0, max_value=255, required=True, initial=3)
    algorithm = forms.TypedChoiceField(choices=ALGORITHMS, coerce=int, empty_value=0, required=True)
    public_key = forms.CharField(required=True)

    def __init__(self, *args, domain_id, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = reverse('add_domain_dnskey_data', args=(domain_id,))
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'flags',
            'protocol',
            'algorithm',
            'public_key'
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Add', css_class="btn-block"))


class DomainSearchForm(forms.Form):
    domain = forms.CharField(max_length=63, label="Domain name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'myawesome.website'}
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = 'domain_search'
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'domain',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Search'))


def map_period(period: apps.epp_api.Period):
    str_value = str(period.value)
    if period.unit == 0:
        str_value += " year"
    elif period.unit == 1:
        str_value += " month"
    if period.value != 1:
        str_value += "s"
    return f"{period.unit}:{period.value}", str_value


def unmap_period(value: str) -> apps.epp_api.Period:
    unit, value = value.split(":", 1)
    return apps.epp_api.Period(
        unit=int(unit),
        value=int(value)
    )


class DomainRegisterForm(forms.Form):
    period = forms.TypedChoiceField(choices=[], required=True, coerce=unmap_period, empty_value=None)
    registrant = forms.ModelChoiceField(queryset=None, required=True)
    admin = forms.ModelChoiceField(queryset=None, label="Admin contact", required=False)
    billing = forms.ModelChoiceField(queryset=None, label="Billing contact", required=False)
    tech = forms.ModelChoiceField(queryset=None, label="Technical contact", required=False)
    intended_use = forms.CharField(max_length=256, label="Intended use", required=True)

    def __init__(self, *args, zone: zone_info.DomainInfo, user, **kwargs):
        super().__init__(*args, **kwargs)
        access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=user.oidc_profile)
        self.fields['period'].choices = map(map_period, zone.pricing.periods)
        self.fields['registrant'].queryset = models.Contact.get_object_list(access_token)
        self.fields['admin'].queryset = models.Contact.get_object_list(access_token)
        self.fields['billing'].queryset = models.Contact.get_object_list(access_token)
        self.fields['tech'].queryset = models.Contact.get_object_list(access_token)
        self.fields['admin'].required = zone.admin_required
        self.fields['billing'].required = zone.billing_required
        self.fields['tech'].required = zone.tech_required

        if not zone.intended_use_required:
            del self.fields['intended_use']

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.label_class = "mt-2"
        self.helper.field_class = "mb-2"
        self.helper.layout = crispy_forms.layout.Layout(
            'period',
            'intended_use',
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Domain contacts',
                crispy_forms.layout.HTML("""
                    <div class="alert alert-info" role="alert">
                        Manage contacts <a href="{% url 'contacts' %}" class="alert-link">here</a>
                    </div>
                """),
                'registrant',
                'admin',
                'billing',
                'tech'
            )
        )
        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Submit order', css_class="btn-block"))


class DomainTransferForm(forms.Form):
    auth_code = forms.CharField(max_length=64, label="Auth code / EPP code / Transfer code")
    registrant = forms.ModelChoiceField(queryset=None, required=True)
    admin = forms.ModelChoiceField(queryset=None, label="Admin contact", required=False)
    billing = forms.ModelChoiceField(queryset=None, label="Billing contact", required=False)
    tech = forms.ModelChoiceField(queryset=None, label="Technical contact", required=False)

    def __init__(self, *args, zone: zone_info.DomainInfo, user, **kwargs):
        super().__init__(*args, **kwargs)
        access_token = django_keycloak_auth.clients.get_active_access_token(oidc_profile=user.oidc_profile)
        self.fields['registrant'].queryset = models.Contact.get_object_list(access_token)
        self.fields['admin'].queryset = models.Contact.get_object_list(access_token)
        self.fields['billing'].queryset = models.Contact.get_object_list(access_token)
        self.fields['tech'].queryset = models.Contact.get_object_list(access_token)
        self.fields['admin'].required = zone.admin_required
        self.fields['billing'].required = zone.billing_required
        self.fields['tech'].required = zone.tech_required

        if not zone.auth_code_for_transfer:
            del self.fields['auth_code']

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.label_class = "mt-2"
        self.helper.field_class = "mb-2"
        self.helper.layout = crispy_forms.layout.Layout(
            'auth_code' if 'auth_code' in self.fields else None,
            crispy_forms.layout.HTML("<hr/>") if 'auth_code' in self.fields else None,
            crispy_forms.layout.Fieldset(
                'Domain contacts',
                crispy_forms.layout.HTML("""
                    <div class="alert alert-info" role="alert">
                        Manage contacts <a href="{% url 'contacts' %}" class="alert-link">here</a>
                    </div>
                """),
                'registrant',
                'admin',
                'billing',
                'tech'
            )
        )
        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Proceed to payment', css_class="btn-block"))


class DomainRenewForm(forms.Form):
    period = forms.TypedChoiceField(choices=[], required=True, coerce=unmap_period, empty_value=None)

    def __init__(self, *args, zone_info, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['period'].choices = map(map_period, zone_info.pricing.periods)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.label_class = "mt-2"
        self.helper.field_class = "mb-2"
        self.helper.layout = crispy_forms.layout.Layout(
            'period',
        )
        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Proceed to payment', css_class="btn-block"))


class AdminDomainCheckForm(forms.Form):
    domain = forms.CharField(max_length=63, label="Domain name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'myawesome.website'}
    ))
    currency = forms.CharField(required=False)
    command = forms.ChoiceField(choices=(
        (apps.epp_api.fee_pb2.Create, "Create"),
        (apps.epp_api.fee_pb2.Renew, "Renew"),
        (apps.epp_api.fee_pb2.Transfer, "Transfer"),
        (apps.epp_api.fee_pb2.Restore, "Restore")
    ), required=False)
    period = forms.TypedChoiceField(choices=(
        (f"0:1", "1 Year"),
        (f"0:2", "2 Years"),
        (f"0:3", "3 Years"),
        (f"0:4", "4 Years"),
        (f"0:5", "5 Years"),
        (f"0:6", "6 Years"),
        (f"0:7", "7 Years"),
        (f"0:8", "8 Years"),
        (f"0:9", "9 Years"),
        (f"0:10", "10 Years"),
    ), required=False, coerce=unmap_period, empty_value=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'domain',
            'currency',
            'command',
            'period'
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Search'))


class AdminDomainTransferForm(forms.Form):
    domain = forms.CharField(max_length=63, label="Domain name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'myawesome.website'}
    ))
    auth_code = forms.CharField(max_length=64)
    period = forms.TypedChoiceField(choices=(
        (None, "---"),
        (f"0:1", "1 Year"),
        (f"0:2", "2 Years"),
        (f"0:3", "3 Years"),
        (f"0:4", "4 Years"),
        (f"0:5", "5 Years"),
        (f"0:6", "6 Years"),
        (f"0:7", "7 Years"),
        (f"0:8", "8 Years"),
        (f"0:9", "9 Years"),
        (f"0:10", "10 Years"),
    ), required=False, coerce=unmap_period, empty_value=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'domain',
            'auth_code',
            'period'
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Transfer'))


class AdminContactCheckForm(forms.Form):
    contact = forms.CharField(max_length=63, label="Registry Contact ID", required=True)
    registry_id = forms.CharField(max_length=63, label="Registry ID", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'contact',
            'registry_id'
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Search'))


class AdminContactGetIDForm(forms.Form):
    contact = forms.UUIDField(label="Contact ID", required=True)
    registry_id = forms.CharField(max_length=63, label="Registry ID", required=True)
    domain = forms.CharField(max_length=255, label="Domain", required=False)
    role = forms.TypedChoiceField(choices=[
        ("", "---"),
        (apps.epp_api.ContactRole.Registrant.value, "Registrant"),
        (apps.epp_api.ContactRole.Admin.value, "Admin"),
        (apps.epp_api.ContactRole.Tech.value, "Tech"),
        (apps.epp_api.ContactRole.Billing.value, "Billing"),
        (apps.epp_api.ContactRole.Reseller.value, "Reseller"),
        (apps.epp_api.ContactRole.OnSite.value, "OnSite"),
    ], coerce=apps.epp_api.ContactRole, empty_value=None, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'contact',
            'registry_id',
            'domain',
            'role',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Get'))


class AdminNominetReleaseForm(forms.Form):
    domain_name = forms.CharField(max_length=255, label="Domain name", required=True)
    registrar_tag = forms.CharField(max_length=255, label="Registrar TAG", required=False)
    registry_id = forms.CharField(max_length=63, label="Registry ID", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'domain_name',
            'registrar_tag',
            'registry_id',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Submit'))


class AdminNominetHandshakeAcceptForm(forms.Form):
    case_id = forms.CharField(max_length=255, label="Case ID", required=True)
    registrant = forms.CharField(max_length=255, label="Registrant", required=False)
    registry_id = forms.CharField(max_length=63, label="Registry ID", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'case_id',
            'registrant',
            'registry_id',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Submit'))


class AdminNominetHandshakeRejectForm(forms.Form):
    case_id = forms.CharField(max_length=255, label="Case ID", required=True)
    registry_id = forms.CharField(max_length=63, label="Registry ID", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'case_id',
            'registry_id',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Submit'))


class HostSearchForm(forms.Form):
    host = forms.CharField(max_length=63, label="Host name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'ns1'}
    ))

    def __init__(self, *args, domain_name: str, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            crispy_forms.bootstrap.AppendedText('host', f".{domain_name}"),
            crispy_forms.layout.Hidden('type', 'host_search')
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Check'))


class HostRegisterForm(forms.Form):
    address = forms.GenericIPAddressField(label="IP Address", required=True, widget=forms.TextInput(
        attrs={'placeholder': '2001:db8:8:4::2'}
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'address',
            crispy_forms.layout.Hidden('type', 'host_create')
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Create'))


class NameSearchForm(forms.Form):
    domain = forms.CharField(label="Your preferred domain", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'myawesome.website'}
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'domain',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Search'))


class PersonalNameSearchForm(forms.Form):
    name = forms.CharField(label="Your name", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'name',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Search'))


class OnlineNameSearchForm(forms.Form):
    online_uri = forms.URLField(label="Your existing online URL (social media, etc)", required=False)
    online_title = forms.CharField(label="Your preferred title", required=False)
    online_description = forms.CharField(label="A brief description", required=False)
    domain = forms.CharField(label="Your preferred domain", required=False, widget=forms.TextInput(
        attrs={'placeholder': 'myawesome.website'}
    ))
    location = forms.CharField(label="Your location", required=False)
    email = forms.EmailField(label="Your email", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.use_custom_control = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10 my-1'
        self.helper.layout = crispy_forms.layout.Layout(
            'online_uri',
            'online_title',
            'online_description',
            'domain',
            'location',
            'email',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Search'))
