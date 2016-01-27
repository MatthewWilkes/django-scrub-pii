from django.db import models
from scrubpii import allow_sensitive_fields


allow_sensitive_fields()
class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()

    def __unicode__(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    class Meta:
        sensitive_fields = {'last_name', 'first_name', 'email'}


class Book(models.Model):
    title = models.CharField(max_length=30)
    author = models.ForeignKey(Person)

    def __unicode__(self):
        return "{0} by {1}".format(self.title, self.author)

