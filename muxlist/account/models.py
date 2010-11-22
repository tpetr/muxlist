from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    parent = models.ForeignKey('self', blank=True, null=True)
    uploaded_tracks = models.ManyToManyField('music.Track', blank=True, related_name='uploader')
    favorite_tracks = models.ManyToManyField('music.Track', blank=True, related_name='favorited')

    def __unicode__(self):
        return user.__unicode__(self)

def create_userprofile(sender, instance, created, **kwargs):
    if created:
        print "Making userprofile"
        UserProfile.objects.create(user=instance)

models.signals.post_save.connect(create_userprofile, sender=User)

class Invite(models.Model):
    owner = models.ForeignKey(User)
    code = models.CharField(max_length=16, unique=True, db_index=True)

    def __unicode__(self):
        return u"%s - %s" % (self.owner, self.code)
