try:
    from django.apps import apps
except ImportError:
    from django.db import models as apps
from django.core.management.base import BaseCommand, CommandError
from scrubpii.utils import get_updates_for_model


class Command(BaseCommand):
    can_import_settings = True
    output_transaction = True

    def handle(self, *args, **options):
        models = apps.get_models()
        script = ""
        for model in models:
            updates = get_updates_for_model(model)
            if updates:
                script += updates
        return script
