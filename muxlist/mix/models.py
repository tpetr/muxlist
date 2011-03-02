from django.db import models
from django.contrib.auth.models import User
from mix.utils import dequeue_track
import redis, time

from muxlist.music.models import Track
from muxlist.account.utils import set_user_online_global, set_user_online_group, user_online_group

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

    def user_heartbeat(self, user):
        r = _get_redis()
        now = int(time.time()) / 60

        if not user_online_group(user, self, now, r):
            comet_utils.send_user_join(user, self)

        set_user_online_global(user, now, r)
        set_user_online_group(user, self, now, r)

    def get_users_online(self):
        r = _get_redis()

        now = int(time.time()) / 60

        return User.objects.filter(id__in=r.sunion(['%i_online_%i' % (self.id, i) for i in xrange(now-settings.USER_IDLE_TIME+1, now+1)]))

    def get_users_online_count(self):
        r = _get_redis()

        now = int(time.time()) / 60

        r.sunionstore('%i_online_cache' % self.id, ['%i_online_%i' % (self.id, i) for i in xrange(now-settings.USER_IDLE_TIME+1, now+1)])
        return r.scard('%i_online_cache' % self.id)
        

    def enqueue_track(self, track, user):
        r = _get_redis()

        # enqueue track to user queue
        r.rpush('%s_%s_queue' % (self.id, user.id), track.id)

        # increment total count
        count = r.incr('%s_queued' % self.id)

        # send debug message if in debug mode
        if settings.DEBUG: comet_utils.send_debug("%s enqueued %s" % (user, track), self)

        # add user to group's queue set
        r.zadd('%s_users' % self.id, user.id, 0)

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
        user_id, track_id = None, None

        with r.lock('%s_dequeue_lock' % self.id):
            # grab a track from someone
            user_id, track_id = dequeue_track(r, self.id)
            if track_id == None: return None, None, None

            # record what time the track started
            started_at = int(time.time()) + 1 # add a second for RTT and crap

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

        current_lock = '%s_current_lock' % self.id

        # don't continue if current song is playing or no queued tracks
        if r.ttl('%s_current' % self.id) > -1:
            comet_utils.send_debug("returning null bceause %s_current's ttl = %s" % (self.id, r.ttl('%s_current' % self.id)), self)
            return None, None, None

        if r.exists(current_lock):
            comet_utils.send_debug("returning null bceause of lock")
            return None, None, None

        r.set(current_lock, 1)

        try:
            # next track!
            results = self.next_track(r)
        finally:
            r.delete(current_lock)

        return results
