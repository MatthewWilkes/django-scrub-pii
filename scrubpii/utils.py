import uuid
from django.db import connection
from django.contrib.auth.hashers import make_password

salt = None

UPDATE_QUERY_TEMPLATE = """
    UPDATE {table_name}
    SET {assignments};
"""
ASSIGNMENT_TEMPLATE = """
        {field_name} = {value_method}"""

OBFUSCATED_SOURCES = {
    "CharField": {
        "postgresql": "substring(md5(random()::text) FROM 0 FOR 10)",
        "default":    "'###########'",
    },
    "EmailField": {
        "sqlite":     "'user-' || id || '@example.net'",
        "default":    "concat('user-', id, '@example.net')",
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
    "username": {
        "sqlite":     "'user-' || id",
        "default":    "concat('user-', id)",
    },
    "password": {
        "default":    "'{0}'".format(make_password('password', hasher='md5')),
    }
}


def get_value_method(field, database='default'):
    try:
        options = OBFUSCATED_SOURCES[field.column]
    except KeyError:
        options = OBFUSCATED_SOURCES[type(field).__name__]
    if database in options:
        return options[database]
    return options['default']


def get_sensitive_fields(klass):
    return getattr(klass._meta, 'sensitive_fields', set())


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
