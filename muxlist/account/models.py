from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail
from muxlist.account.utils import send_new_user_email

from muxlist.mix.models import Group, _get_redis

from time import time

import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    parent = models.ForeignKey('self', blank=True, null=True)
    invites = models.PositiveSmallIntegerField(default=0)
    picture_75 = models.URLField(blank=True, null=True)
    picture_20 = models.URLField(blank=True, null=True)

    def __unicode__(self):
        return self.user.__unicode__()

def create_userprofile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        try:
            g = Group.objects.get(name='test')
            g.collaborators.add(instance)
            g.save()
        except Group.DoesNotExist:
            pass
        if settings.NEW_USER_NOTIFICATION:
            send_new_user_email(instance)

models.signals.post_save.connect(create_userprofile, sender=User)

class Invite(models.Model):
    owner = models.ForeignKey(User)
    email = models.EmailField()
    code = models.CharField(max_length=32, unique=True, db_index=True)

    def __unicode__(self):
        return u"%s - %s" % (self.owner, self.email)

    class Meta:
        unique_together = ('owner', 'email')

class InviteRequest(models.Model):
    email = models.EmailField(max_length=128, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.email
