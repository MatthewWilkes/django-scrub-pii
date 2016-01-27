from django.db import connection
from django.test import TestCase
from scrubpii.utils import get_sensitive_fields, get_updates_for_model

from tests.testapp.models import Person, Book


class ModelTestCase(TestCase):

    def test_app_is_decorated_with_sensitive_fields(self):
        assert get_sensitive_fields(Person) == {'first_name', 'last_name', 'email'}

    def test_app_with_no_sensitive_fields_is_correctly_decorated(self):
        assert get_sensitive_fields(Book) == set()


class SanitiseQueryTestCase(TestCase):

    def test_query_generated_if_model_has_sensitive_fields(self):
        assert get_updates_for_model(Person) is not None

    def test_query_not_generated_if_model_has_no_sensitive_fields(self):
        assert get_updates_for_model(Book) is None


class RealWorldTestCase(TestCase):

    def setUp(self):
        mw = Person.objects.create(first_name="Matthew", last_name="Wilkes")
        mb = Person.objects.create(first_name="Mary", last_name="Berry")
        cd = Person.objects.create(first_name="Clive", last_name="Dunn")
        ew = Person.objects.create(first_name="Elizabeth", last_name="Weir")
        Book.objects.create(title="Baking things", author=mb)
        Book.objects.create(title="They don't like it up 'em", author=cd)
        Book.objects.create(title="Treaty Negotiations", author=ew)
    
    def test_query_sanitises_data(self):
        books = map(unicode, Book.objects.all())
        assert "Baking things by Mary Berry" in books
        assert "They don't like it up 'em by Clive Dunn" in books
        assert "Treaty Negotiations by Elizabeth Weir" in books
        
        cursor = connection.cursor()
        cursor.execute(get_updates_for_model(Person))

        books = map(unicode, Book.objects.all())
        assert "Baking things by Mary Berry" not in books
        assert "They don't like it up 'em by Clive Dunn" not in books
        assert "Treaty Negotiations by Elizabeth Weir" not in books
        

