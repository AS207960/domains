import json
from django.http import HttpResponse

from .. import zone_info

def tlds(request):
    available_tlds = list(map(lambda z: z[0], sorted(zone_info.ZONES, key=lambda z: z[0])))

    return HttpResponse(json.dumps(available_tlds), content_type='application/json')
