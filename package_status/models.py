from django.db import models


class PackageStatus(models.Model):
    courier = models.ManyToManyField('courier.Courier', verbose_name='Courier_status')
    status = models.CharField('Package_status', max_length=50)

    def __unicode__(self):
        return '%s (%s)'% (self.status, self.courier)