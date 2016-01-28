from .utils import get_sensitive_fields  # noqa

import django.db.models.options as options


class allow_sensitive_fields(object):
    """Patches the Django Options class to allow for setting sensitive_fields."""

    def __enter__(self):
        self.original_names = options.DEFAULT_NAMES
        if 'sensitive_fields' in options.DEFAULT_NAMES:
            raise ValueError("sensitive_fields is already defined in Django!")
        options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('sensitive_fields',)

    def __exit__(self, type, value, traceback):
        options.DEFAULT_NAMES = self.original_names
