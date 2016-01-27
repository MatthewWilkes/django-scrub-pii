from .utils import get_sensitive_fields  # noqa

import django.db.models.options as options

def allow_sensitive_fields():
    """Patches the Django Options class to allow for setting sensitive_fields."""
    # Check for the presence of a marker on the options module that we've run already
    # This lets us be idempotent and also detect when we've hit a conflict with core Django
    if not hasattr(options, '_django_scrub_pii_marker'):
        options._django_scrub_pii_marker = True

        if 'sensitive_fields' in options.DEFAULT_NAMES:
            raise ValueError("sensitive_fields is already defined in Django!")
        options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('sensitive_fields',)
