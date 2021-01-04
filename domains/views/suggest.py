import ipaddress
from django.shortcuts import render
from .. import verisign, forms


def get_ip(request):
    net64_net = ipaddress.IPv6Network("2a0d:1a40:7900:6::/96")
    addr = ipaddress.ip_address(request.META['REMOTE_ADDR'])
    if isinstance(addr, ipaddress.IPv6Address):
        if addr.ipv4_mapped:
            addr = addr.ipv4_mapped
        if addr in net64_net:
            addr = ipaddress.IPv4Address(addr._ip & 0xFFFFFFFF)
    return addr


def suggest_name(request):
    suggestions = None
    error = None

    if request.method == "POST" or "domain" in request.GET:
        if request.method == "POST":
            form = forms.NameSearchForm(request.POST)
        else:
            form = forms.NameSearchForm(request.GET)
        if form.is_valid():
            ip_addr = get_ip(request)
            try:
                suggestions = verisign.suggests(
                    form.cleaned_data["domain"], str(ip_addr),
                    iso_code=request.country.iso_code,
                    username=request.user.username if request.user.is_authenticated else None
                )
            except verisign.VerisignError as e:
                error = e.message
    else:
        form = forms.NameSearchForm()

    return render(request, "domains/domain_suggest.html", {
        "name_form": form,
        "suggestions": suggestions,
        "error": error
    })


def suggest_personal_name(request):
    suggestions = None
    error = None

    if request.method == "POST":
        form = forms.PersonalNameSearchForm(request.POST)
        if form.is_valid():
            name_parts = form.cleaned_data['name'].split(" ")
            if len(name_parts) == 1:
                first_name = name_parts[0]
                middle_names = None
                last_name = None
            elif len(name_parts) == 2:
                first_name = name_parts[0]
                middle_names = None
                last_name = name_parts[1]
            else:
                first_name = name_parts[0]
                middle_names = name_parts[1:-1]
                last_name = name_parts[-1]
            try:
                suggestions = verisign.suggest_personal_names(
                    first_name, last_name, middle_names,
                    iso_code=request.country.iso_code,
                    username=request.user.username if request.user.is_authenticated else None
                )
            except verisign.VerisignError as e:
                error = e.message
    else:
        form = forms.PersonalNameSearchForm()
        if request.user.is_authenticated:
            try:
                suggestions = verisign.suggest_personal_names(
                    request.user.first_name, request.user.last_name,
                    iso_code=request.country.iso_code,
                    username=request.user.username if request.user.is_authenticated else None
                )
            except verisign.VerisignError as e:
                error = e.message

    return render(request, "domains/domain_suggest_personal.html", {
        "name_form": form,
        "suggestions": suggestions,
        "error": error
    })


def suggest_online(request):
    suggestions = None
    error = None

    if request.method == "POST":
        form = forms.OnlineNameSearchForm(request.POST)
        if form.is_valid():
            try:
                suggestions = verisign.online_presence(
                    online_uri=form.cleaned_data.get("online_uri"),
                    online_title=form.cleaned_data.get("online_title"),
                    online_description=form.cleaned_data.get("online_description"),
                    preferred_name=form.cleaned_data.get("domain"),
                    location=form.cleaned_data.get("location"),
                    email=form.cleaned_data.get("email"),
                    iso_code=request.country.iso_code,
                    username=request.user.username if request.user.is_authenticated else None
                )
            except verisign.VerisignError as e:
                error = e.message
    else:
        form = forms.OnlineNameSearchForm()

    return render(request, "domains/domain_suggest_online.html", {
        "name_form": form,
        "suggestions": suggestions,
        "error": error
    })
