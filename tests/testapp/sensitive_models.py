from django.db import models
from django.utils.encoding import python_2_unicode_compatible

__all__ = ['Purchase']


@python_2_unicode_compatible
class Purchase(models.Model):
    book = models.ForeignKey('Book')
    buyer_ip = models.GenericIPAddressField()
    purchased_at = models.DateTimeField()

    def __str__(self):
        return "{0} bought {1} at {2}".format(self.buyer_ip, self.book, self.purchased_at)

    class Meta:
        sensitive_fields = {'buyer_ip', 'purchased_at'}
