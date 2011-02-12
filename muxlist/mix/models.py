from django.db import models
from django.contrib.auth.models import User
from mix.utils import dequeue_track
import redis, time
from math import floor

from muxlist.music.models import Track

from muxlist.comet import utils as comet_utils
from django.conf import settings

def _get_redis():
    return redis.Redis(host='localhost', port=6379, db=0)

class Group(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)
    collaborators = models.ManyToManyField(User, blank=True, related_name="membership")

    is_active = models.BooleanField(default=False, blank=True)
    is_public = models.BooleanField(default=False, blank=True)
    
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return '/mix/%s' % self.name

    def __unicode__(self):
        return self.name

    def enqueue_track(self, track, user):
        r = _get_redis()

        # enqueue track to user queue
        r.rpush('%s_%s_queue' % (self.id, user.id), track.id)

        # increment total count
        count = r.incr('%s_queued' % self.id)

        # send debug message if in debug mode
        if settings.DEBUG: comet_utils.send_debug("%s enqueued %s" % (user, track), self)

        # add user to group's queue set
        r.sadd('%s_users' % self.id, user.id)

        # send queue update if next song not pushed
        if self.check_for_next_track()[0] == None:
            comet_utils.send_queue_update(count, self)

        # return queue count
        return r.get('%s_queued' % self.id)

    def get_current_track(self):
        r = _get_redis()

        # check for expired
        if not r.exists('%s_current' % self.id): return None, None, None

        # get info
        track_id = r.get('%s_current' % self.id)
        user_id = r.get('%s_current_user' % self.id)
        started_at = r.get('%s_current_start' % self.id)

        # get data from db
        track = Track.objects.get(id=track_id)
        user = User.objects.get(id=user_id)

        return (track, user, started_at)

    def now_playing(self):
        track, user, started_at = self.get_current_track()
        return track.__unicode__()

    def queued_tracks_count(self):
        r = _get_redis()
        return r.get('%s_queued' % self.id)

    def queued_users_count(self):
        r = _get_redis()
        return r.scard('%s_users' % self.id)

    def recalculate_queued(self):
        r = _get_redis()
        count = 0
        for user_id in r.smembers('%s_users' % self.id):
            count += r.llen('%s_%s_queue' % (self.id, user_id))
        r.set('%s_queued' % self.id, count)
        return count

    def next_track(self, r=None):
        r = r or _get_redis()

        # grab a track from someone
        user_id, track_id = dequeue_track(r, self.id)
        if track_id == None: return None, None, None

        # record what time the track started
        started_at = floor(time.time()) + 1 # add a second for RTT and crap

        # set the track as current
        r.set('%s_current' % self.id, track_id)
        r.set('%s_current_user' % self.id, user_id)
        r.set('%s_current_start' % self.id, started_at)

        # grab data from db
        user = User.objects.get(id=user_id)
        track = Track.objects.get(id=track_id)

        # send it out
        comet_utils.send_track_update(track, self, user)

        # set expiration
        r.expire('%s_current' % self.id, track.length)

        return (track, user, started_at)

    def check_for_next_track(self):
        r = _get_redis()

        # don't continue if current song is playing or no queued tracks
        if r.ttl('%s_current' % self.id) > -1: return None, None, None

        # next track!
        return self.next_track(r)
