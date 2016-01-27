UPDATE_QUERY_TEMPLATE = """
    UPDATE {table_name}
    SET {assignments};
"""
ASSIGNMENT_TEMPLATE = "{field_name} = {value_method}"

def get_sensitive_fields(klass):
    return getattr(klass._meta, 'sensitive_fields', set())

def get_updates_for_model(klass):
    fields = []
    sensitive_fields = get_sensitive_fields(klass)
    if not sensitive_fields:
        return None
    for field in sensitive_fields:
        field_object = klass._meta.get_field(field)
        fields.append({'field_name': field, 'value_method': '"#####"'})
    assignments = map(lambda x:ASSIGNMENT_TEMPLATE.format(**x), fields)
    assignments = ",".join(assignments)
    query = UPDATE_QUERY_TEMPLATE.format(table_name=klass._meta.db_table, assignments=assignments)
    return query