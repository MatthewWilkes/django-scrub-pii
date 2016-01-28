from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from scrubpii.utils import get_updates_for_model


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        models = apps.get_models()
        for model in models:
            updates = get_updates_for_model(model)
            if updates:
                print updates
        