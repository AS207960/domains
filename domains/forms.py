from django import forms
from django.urls import reverse
from . import models, apps
import datetime
from django_countries.widgets import CountrySelectWidget
import crispy_forms.helper
import crispy_forms.layout
import crispy_forms.bootstrap


class ContactForm(forms.ModelForm):
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['local_address'].queryset = models.ContactAddress.objects.filter(user=user)
        self.fields['int_address'].queryset = models.ContactAddress.objects.filter(user=user)
        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
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
            )
        )
        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Submit'))

    class Meta:
        model = models.Contact
        fields = "__all__"
        exclude = ("id", "user", "created_date", "updated_date")


class AddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        this_year = datetime.date.today().year
        self.fields['birthday'].widget = forms.SelectDateWidget(years=range(this_year - 99, this_year))
        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.layout = crispy_forms.layout.Layout(
            'description',
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(
                'Contact information',
                'name',
                'organisation',
            ),
            crispy_forms.layout.Fieldset(
                'Personal information',
                crispy_forms.layout.HTML("""
                    <div class="alert alert-info" role="alert">
                        Birthday is required for foreign personal registrants under the .fi domain<br/>
                        National identity number is required for Finnish registrants under the .fi domain<br/>
                    </div>
                """),
                'birthday',
                'identity_number',
            ),
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
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Submit'))

    class Meta:
        model = models.ContactAddress
        fields = "__all__"
        widgets = {'country_code': CountrySelectWidget(
            layout="""
            <div class="input-group input-group-sm">
                {widget}
                <div class="input-group-append">
                    <span class="input-group-text">
                        <img class="country-select-flag" id="{flag_id}" src="{country.flag}">
                    </span
                </div>
            </div>
            """
        )}
        exclude = ("id", "user")


class DomainContactForm(forms.Form):
    contact = forms.ModelChoiceField(queryset=None, label="Set new contact", required=False)
    type = forms.CharField()

    def __init__(self, *args, user, contact_type, domain_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact'].queryset = models.Contact.objects.filter(user=user)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = reverse('update_domain_contact', args=(domain_id,))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.layout = crispy_forms.layout.Layout(
            'contact',
            crispy_forms.layout.Hidden('type', contact_type)
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Save'))

    def set_cur_id(self, cur_id, registry_id):
        reg_contact = models.ContactRegistry.objects.filter(registry_contact_id=cur_id, registry_id=registry_id).first()
        if reg_contact:
            self.fields['contact'].value = reg_contact.contact.id


class DomainHostObjectForm(forms.Form):
    host = forms.CharField(max_length=63, label="Host name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'ns1.example.com'}
    ))

    def __init__(self, *args, user, domain_id, registry_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = reverse('add_domain_host_obj', args=(domain_id,))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.layout = crispy_forms.layout.Layout(
            'host',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Add'))


class DomainHostAddrForm(forms.Form):
    host = forms.CharField(max_length=63, label="Host name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'ns1.example.com'}
    ))
    address = forms.GenericIPAddressField(label="IP Address", required=False, widget=forms.TextInput(
        attrs={'placeholder': '2001:db8:8:4::2'}
    ))

    def __init__(self, *args, domain_id, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = reverse('add_domain_host_addr', args=(domain_id,))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.layout = crispy_forms.layout.Layout(
            'host',
            'address'
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Add'))


class DomainDSDataForm(forms.Form):
    ALGORITHMS = (
        (5, "RSA/SHA-1 (5) INSECURE"),
        (7, "RSASHA1-NSEC3-SHA1 (7) INSECURE"),
        (8, "RSA/SHA-256 (8)"),
        (10, "RSA/SHA-512 (10)"),
        (13, "ECDSA Curve P-256 with SHA-256 (13)"),
        (14, "ECDSA Curve P-384 with SHA-384 (14)"),
        (15, "Ed25519 (15)"),
        (16, "Ed448 (16)"),
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
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.layout = crispy_forms.layout.Layout(
            'key_tag',
            'algorithm',
            'digest_type',
            'digest'
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Add'))


class DomainDNSKeyDataForm(forms.Form):
    ALGORITHMS = (
        (5, "RSA/SHA-1 (5) INSECURE"),
        (7, "RSASHA1-NSEC3-SHA1 (7) INSECURE"),
        (8, "RSA/SHA-256 (8)"),
        (10, "RSA/SHA-512 (10)"),
        (13, "ECDSA Curve P-256 with SHA-256 (13)"),
        (14, "ECDSA Curve P-384 with SHA-384 (14)"),
        (15, "Ed25519 (15)"),
        (16, "Ed448 (16)"),
    )

    flags = forms.IntegerField(min_value=0, max_value=65535, required=True)
    protocol = forms.IntegerField(min_value=0, max_value=255, required=True, initial=3)
    algorithm = forms.TypedChoiceField(choices=ALGORITHMS, coerce=int, empty_value=0, required=True)
    public_key = forms.CharField(required=True)

    def __init__(self, *args, domain_id, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_action = reverse('add_domain_dnskey_data', args=(domain_id,))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.layout = crispy_forms.layout.Layout(
            'flags',
            'protocol',
            'algorithm',
            'public_key'
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Add'))


class DomainSearchForm(forms.Form):
    domain = forms.CharField(max_length=63, label="Domain name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'myawesome.website'}
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.layout = crispy_forms.layout.Layout(
            'domain',
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Search'))


def map_period(period: apps.epp_api.DomainPeriod):
    str_value = str(period.value)
    if period.unit == 0:
        str_value += " year"
    elif period.unit == 1:
        str_value += " month"
    if period.value != 1:
        str_value += "s"
    return f"{period.unit}:{period.value}", str_value


def unmap_period(value: str) -> apps.epp_api.DomainPeriod:
    unit, value = value.split(":", 1)
    return apps.epp_api.DomainPeriod(
        unit=int(unit),
        value=int(value)
    )


class DomainRegisterForm(forms.Form):
    period = forms.TypedChoiceField(choices=[], required=True, coerce=unmap_period, empty_value=None)
    registrant = forms.ModelChoiceField(queryset=None, required=True)
    admin = forms.ModelChoiceField(queryset=None, label="Admin contact", required=False)
    billing = forms.ModelChoiceField(queryset=None, label="Billing contact", required=False)
    tech = forms.ModelChoiceField(queryset=None, label="Technical contact", required=False)

    def __init__(self, *args, zone_info, registry_name, user,  **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['period'].choices = map(map_period, zone_info.periods)
        self.fields['registrant'].queryset = models.Contact.objects.filter(user=user)
        self.fields['admin'].queryset = models.Contact.objects.filter(user=user)
        self.fields['billing'].queryset = models.Contact.objects.filter(user=user)
        self.fields['tech'].queryset = models.Contact.objects.filter(user=user)

        args = [
            'Domain contacts',
            crispy_forms.layout.HTML("""
                    <div class="alert alert-info" role="alert">
                        Manage contacts <a href="{% url 'contacts' %}" class="alert-link">here</a>
                    </div>
                """),
            'registrant'
        ]

        if registry_name in ("nominet", "traficom"):
            pass
        elif registry_name == "switch":
            args.append('tech')
        else:
            args.extend(['admin', 'billing', 'tech'])

        if registry_name == "afilias":
            self.fields['admin'].required = True
            self.fields['billing'].required = True
            self.fields['tech'].required = True

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.layout = crispy_forms.layout.Layout(
            'period',
            crispy_forms.layout.HTML("<hr/>"),
            crispy_forms.layout.Fieldset(*args)
        )
        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Register'))


class DomainRenewForm(forms.Form):
    period = forms.TypedChoiceField(choices=[], required=True, coerce=unmap_period, empty_value=None)

    def __init__(self, *args, zone_info,  **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['period'].choices = map(map_period, zone_info.periods)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.layout = crispy_forms.layout.Layout(
            'period',
        )
        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Renew'))


class HostSearchForm(forms.Form):
    host = forms.CharField(max_length=63, label="Host name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'ns1'}
    ))

    def __init__(self, *args, domain_name: str, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
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
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.layout = crispy_forms.layout.Layout(
            'address',
            crispy_forms.layout.Hidden('type', 'host_create')
        )

        self.helper.add_input(crispy_forms.layout.Submit('submit', 'Create'))
