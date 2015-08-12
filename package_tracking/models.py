from django.db import models


class PackageTracking(models.Model):
    nomer = models.CharField('Package_nomer', max_length=50)
    guid = models.CharField('Package_guid', max_length=40, primary_key=True)
    datetime = models.DateTimeField('PackageTracking_datetime')
    status = models.ForeignKey('package_status.PackageStatus', verbose_name='PackageTracking_status')
    comment = models.CharField('PackageTracking_comment', max_length=500, null=True, blank=True)
    branch = models.CharField('PackageTracking_branch', max_length=100, null=True, blank=True)

    def __unicode__(self):
        return '%s %s [%s]'% (self.nomer, self.status, self.datetime)