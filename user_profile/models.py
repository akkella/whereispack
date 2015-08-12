from django.db import models


class UserProfile(models.Model):
    name = models.CharField('User_name', max_length=50)
    surname = models.CharField('User_surname', max_length=50)
    email = models.EmailField('User_email', null=True, blank=True)
    phone = models.CharField('User_phone', max_length=20, null=True, blank=True)
    password = models.CharField('User_pass', max_length=20)
    date_reg = models.DateField('User_date_registered', auto_now_add=True)

    def __unicode__(self):
        return '%s %s'% (self.surname, self.name)