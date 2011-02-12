from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail
from muxlist.account.utils import send_new_user_email

from muxlist.mix.models import Group, _get_redis

from time import time
from math import floor

def user_heartbeat(user_id):
    r = _get_redis()
    last_update = r.get('online_last')
    now = floor(time()) / 60
    r.sadd('online_' % now, user_id)

    if now != last_update:
        r.expire('online_' % now, 60)

User.heartbeat = lambda self: return send_heartbeat(self.id)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    parent = models.ForeignKey('self', blank=True, null=True)
    invites = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.user.__unicode__()

def create_userprofile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        g = Group.objects.get(name='test')
        g.collaborators.add(instance)
        g.save()
        if NEW_USER_NOTIFICATIONS:
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
