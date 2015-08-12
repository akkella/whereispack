from django.db import models


class Courier(models.Model):
    name = models.CharField('Courier_name', max_length=250, unique=True)
    email = models.EmailField('Courier_email')
    phone = models.CharField('Courier_phone', max_length=20, null=True, blank=True)
    address = models.CharField('Courier_address', max_length=200, null=True, blank=True)

    def __unicode__(self):
        return '%s' % self.name