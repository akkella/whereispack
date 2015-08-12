from django.db import models


class Package(models.Model):
    nomer = models.CharField('Package_nomer', max_length=50)
    courier = models.ForeignKey('courier.Courier', verbose_name='Package_courier')
    user = models.ForeignKey('user_profile.UserProfile', verbose_name='Package_user')
    guid = models.CharField('Package_guid', max_length=40)

    def __unicode__(self):
        return '%s %s (%s)'% (self.nomer, self.courier, self.user)