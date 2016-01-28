from django.db import models
from scrubpii import allow_sensitive_fields


with allow_sensitive_fields():
    class Person(models.Model):
        first_name = models.CharField(max_length=30)
        last_name = models.CharField(max_length=30)
        date_of_birth = models.DateField()
        email = models.EmailField()

        def __unicode__(self):
            return "{0} {1}".format(self.first_name, self.last_name)

        class Meta:
            sensitive_fields = {'last_name', 'first_name', 'email', 'date_of_birth'}


class Book(models.Model):
    title = models.CharField(max_length=30)
    author = models.ForeignKey(Person)

    def __unicode__(self):
        return "{0} by {1}".format(self.title, self.author)


with allow_sensitive_fields():
    # Test that importing from another models file works, as recommended by README
    from .sensitive_models import *  # noqa
