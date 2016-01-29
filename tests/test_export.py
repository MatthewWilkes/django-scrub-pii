import datetime
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.core.management import call_command
from django.db import connection
from django.test import TestCase
import pytest
from scrubpii import allow_sensitive_fields
from scrubpii.utils import get_sensitive_fields, get_updates_for_model

from tests.testapp.models import Person, Book, Purchase


class ModelTestCase(TestCase):

    def test_app_is_decorated_with_sensitive_fields(self):
        assert get_sensitive_fields(Person) == {'first_name', 'last_name', 'email', 'date_of_birth'}

    def test_app_with_no_sensitive_fields_is_correctly_decorated(self):
        assert get_sensitive_fields(Book) == set()


class SanitiseQueryTestCase(TestCase):

    def test_query_generated_if_model_has_sensitive_fields(self):
        assert get_updates_for_model(Person) is not None

    def test_query_not_generated_if_model_has_no_sensitive_fields(self):
        assert get_updates_for_model(Book) is None


@pytest.mark.django_db
class RealWorldTestCase(TestCase):

    def setUp(self):
        Person.objects.create(first_name="Matthew",
                              last_name="Wilkes",
                              email="matt@example.com",
                              date_of_birth=datetime.date(1986, 7, 19))
        mb = Person.objects.create(first_name="Mary",
                                   last_name="Berry",
                                   email="mary@example.com",
                                   date_of_birth=datetime.date(1935, 3, 24))
        cd = Person.objects.create(first_name="Clive",
                                   last_name="Dunn",
                                   email="clive@example.com",
                                   date_of_birth=datetime.date(1920, 1, 9))
        ew = Person.objects.create(first_name="Elizabeth",
                                   last_name="Weir",
                                   email="liz@example.com",
                                   date_of_birth=datetime.date(1948, 2, 20))
        bt = Book.objects.create(title="Baking things", author=mb)
        Book.objects.create(title="They don't like it up 'em", author=cd)
        tn = Book.objects.create(title="Treaty Negotiations", author=ew)
        Purchase.objects.create(book=bt, buyer_ip="192.0.2.1", purchased_at=datetime.datetime(2016, 1, 10, 12, 15))
        Purchase.objects.create(book=tn, buyer_ip="192.0.2.21", purchased_at=datetime.datetime(2013, 10, 4, 22, 48))

    def test_query_sanitises_character_data(self):
        books = ["{0}".format(book) for book in Book.objects.all()]
        assert "Baking things by Mary Berry" in books
        assert "They don't like it up 'em by Clive Dunn" in books
        assert "Treaty Negotiations by Elizabeth Weir" in books

        cursor = connection.cursor()
        cursor.execute(get_updates_for_model(Person))

        books = ["{0}".format(book) for book in Book.objects.all()]
        assert "Baking things by Mary Berry" not in books
        assert "They don't like it up 'em by Clive Dunn" not in books
        assert "Treaty Negotiations by Elizabeth Weir" not in books

    def test_query_sanitises_IP_data(self):
        first_purchase = Purchase.objects.get(book__title="Baking things")
        second_purchase = Purchase.objects.get(book__title="Treaty Negotiations")

        assert first_purchase.buyer_ip == "192.0.2.1"
        assert second_purchase.buyer_ip == "192.0.2.21"

        cursor = connection.cursor()
        cursor.execute(get_updates_for_model(Purchase))

        first_purchase = Purchase.objects.get(book__title="Baking things")
        second_purchase = Purchase.objects.get(book__title="Treaty Negotiations")
        assert first_purchase.buyer_ip != "192.0.2.1"
        assert second_purchase.buyer_ip != "192.0.2.21"

    def test_query_sanitises_date_data(self):
        first_purchase = Purchase.objects.get(book__title="Baking things")
        second_purchase = Purchase.objects.get(book__title="Treaty Negotiations")
        clive = Person.objects.get(first_name="Clive")

        assert first_purchase.purchased_at > second_purchase.purchased_at
        assert clive.date_of_birth == datetime.date(1920, 1, 9)

        cursor = connection.cursor()
        cursor.execute(get_updates_for_model(Purchase))
        cursor.execute(get_updates_for_model(Person))

        first_purchase = Purchase.objects.get(book__title="Baking things")
        second_purchase = Purchase.objects.get(book__title="Treaty Negotiations")
        clive = Person.objects.get(pk=clive.pk)

        assert first_purchase.purchased_at == second_purchase.purchased_at
        assert clive.date_of_birth != datetime.date(1920, 1, 9)

    def test_query_sanitises_passwords(self):
        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import check_password

        User._meta.sensitive_fields = {'email', 'username', 'password'}

        admin = User.objects.create_user(username="admin", email="admin@example.org", password="secrets!")
        editor = User.objects.create_user(username="editor", email="editor@example.org", password="ilovehorses")
        assert check_password("secrets!", admin.password)
        assert check_password("ilovehorses", editor.password)

        cursor = connection.cursor()
        cursor.execute(get_updates_for_model(User))

        # Refresh users from DB
        admin = User.objects.get(pk=admin.pk)
        editor = User.objects.get(pk=editor.pk)

        assert admin.email == 'user-1@example.net'
        assert editor.email == 'user-2@example.net'
        assert check_password("password", admin.password)
        assert check_password("password", editor.password)

    def test_export_script(self):
        out = StringIO()
        call_command('get_sensitive_data_removal_script', stdout=out)
        script = out.getvalue().strip()
        # Check transactionality
        assert script.startswith("BEGIN;")
        assert script.endswith("COMMIT;")
        # Check person model
        assert 'UPDATE testapp_person' in script
        assert 'email = ' in script
        assert 'last_name = ' in script
        assert 'first_name = ' in script
        assert 'date_of_birth = ' in script
        # Check Purchase model
        assert 'UPDATE testapp_purchase' in script
        assert 'purchased_at = ' in script
        assert 'buyer_ip = ' in script

    def test_futureproofing(self):
        import django.db.models.options as options
        options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('sensitive_fields',)
        with pytest.raises(Exception):
            with allow_sensitive_fields():
                pass
