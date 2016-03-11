import uuid
from django.db import connection
from django.conf import settings
from django.contrib.auth.hashers import make_password

salt = None

UPDATE_QUERY_TEMPLATE = """
    UPDATE {table_name}
    SET {assignments};
"""
ASSIGNMENT_TEMPLATE = """
        {field_name} = {value_method}"""

FIELD_TYPE_MAPPING = {
    "CharField": {
        "postgresql": "substring(md5(random()::text) FROM 0 FOR 10)",
        "default":    "'###########'",
    },
    "TextField": {
        "default":    ("'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce urna lorem, condimentum ut"
                       " pretium commodo, iaculis eget lacus. In eget lorem varius erat auctor tempor. Pellentesque"
                       " lacinia varius erat, sed eleifend magna consectetur et. Maecenas porttitor varius enim quis"
                       " tincidunt. Maecenas feugiat ipsum a augue iaculis, a volutpat urna egestas. Cras molestie"
                       " mauris non arcu tempor efficitur. Donec at felis lacus. Nulla posuere pretium magna at"
                       " elementum.'"),
    },
    "EmailField": {
        "default":     "'user-' || id || '@example.net'",
    },
    "DateField": {
        "postgresql":  "date '1990-06-02'",
        "sqlite":      "date('1990-06-02')",
    },
    "DateTimeField": {
        "default":    "timestamp '1990-06-02 10:00:00'",
        "sqlite":      "datetime('1990-06-02 10:00:00')",
    },
    "GenericIPAddressField": {
        "postgresql": """CONCAT(
                             '2001:db8:',
                             SUBSTRING(md5(concat({field_name}, '{salt}')) FROM  1 FOR 4), ':',
                             SUBSTRING(md5(concat({field_name}, '{salt}')) FROM  5 FOR 4), ':',
                             SUBSTRING(md5(concat({field_name}, '{salt}')) FROM  9 FOR 4), ':',
                             SUBSTRING(md5(concat({field_name}, '{salt}')) FROM 13 FOR 4), ':',
                             SUBSTRING(md5(concat({field_name}, '{salt}')) FROM 17 FOR 4), ':',
                             SUBSTRING(md5(concat({field_name}, '{salt}')) FROM 21 FOR 4)
                         )::inet""",
        "default":    "'2001:db8::1'"
    },
    "URLField": {
        "default":    "'http://example.com'",
    },
}

FIELD_NAME_MAPPING = {
    "username": {
        "default":     "'user-' || id",
    },
    "password": {
        "default":    "'{0}'".format(make_password('password', hasher='md5')),
    },
}


def get_value_method(field, database='default'):
    field_type_name = type(field).__name__
    if field.column in FIELD_NAME_MAPPING:
        options = OBFUSCATED_SOURCES[field.column]
    elif field_type_name in FIELD_TYPE_MAPPING:
        options = OBFUSCATED_SOURCES[field_type_name]
    else:
        raise NotImplementedError()
    if database in options:
        return options[database]
    return options['default']


def get_sensitive_fields(klass):
    annotated = getattr(klass._meta, 'sensitive_fields', set())
    additional_fields = getattr(settings, 'SCRUB_PII_ADDITIONAL_FIELDS', None)
    if additional_fields is not None:
        class_ref = "{0}.{1}".format(klass._meta.app_label, klass.__name__)
        annotated = annotated.union(additional_fields.get(class_ref, set()))
    return annotated


def get_updates_for_model(klass):
    global salt
    if salt is None:
        salt = uuid.uuid4()

    fields = []
    sensitive_fields = get_sensitive_fields(klass)
    if not sensitive_fields:
        return None
    for field in sensitive_fields:
        field_object = klass._meta.get_field(field)
        value_method = get_value_method(field_object, connection.vendor)
        data = {'table_name': klass._meta.db_table, 'field_name': field, 'salt': salt}
        fields.append({'field_name': field, 'value_method': value_method.format(**data)})
    assignments = map(lambda x: ASSIGNMENT_TEMPLATE.format(**x), fields)
    assignments = ",".join(assignments)
    query = UPDATE_QUERY_TEMPLATE.format(table_name=klass._meta.db_table, assignments=assignments)
    return query
