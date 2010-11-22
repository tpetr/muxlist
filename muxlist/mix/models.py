from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)
    collaborators = models.ManyToManyField(User, blank=True, related_name="membership")
    round_robin_count = models.PositiveSmallIntegerField(default=1, blank=True)
    enqueued_tracks = models.PositiveSmallIntegerField(default=0, blank=True)

    is_active = models.BooleanField(default=False, blank=True)
    is_public = models.BooleanField(default=False, blank=True)
    started_on = models.DateTimeField(blank=True)
    current_index = models.PositiveSmallIntegerField(default=1, blank=True)
    
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

class PlaylistEntry(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group, related_name='entries')
    track = models.ForeignKey('music.Track')
    index = models.PositiveSmallIntegerField()

    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s - %s (%s #%s)" % (self.group, self.track, self.user, self.index)

    class Meta:
        ordering = ['group', 'index', 'user__id']
        unique_together = ('group', 'user', 'index')
