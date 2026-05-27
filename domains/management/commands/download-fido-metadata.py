from django.core.management.base import BaseCommand
from django.conf import settings
import webauthn.metadata
import json

class Command(BaseCommand):
    help = 'Download FIDO metadata to data store'

    def handle(self, *args, **options):
        metadata = webauthn.metadata.get_metadata()
        with open(settings.FIDO_METADATA_FILE, "w") as f:
            json.dump(metadata, f)