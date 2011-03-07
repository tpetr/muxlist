from django.template.loader import render_to_string
from django.core.mail import send_mail

import time, redis
import settings
import urllib2
from BeautifulSoup import BeautifulSoup

def get_random_images(count=4):
    r = urllib2.urlopen('http://api.flickr.com/services/rest/?method=flickr.panda.getPhotos&api_key=9d635f5b4d40d2fae5aa0b80812c860b&panda_name=ling+ling&per_page=%s&page=1' % count)
    bs = BeautifulSoup(r.read())
    return ["http://farm%s.static.flickr.com/%s/%s_%s_s_d.jpg" % (photo['farm'], photo['server'], photo['id'], photo['secret']) for photo in bs.findAll('photo')]

def _get_redis():
    return redis.Redis(host='localhost', port=6379, db=0)

def user_online_group(user, group, now=None, r=None):
    now = now or (int(time.time()) / 60)
    r = r or _get_redis()

    for i in xrange(now, now - settings.USER_IDLE_TIME, -1):
        if r.sismember('%i_online_%i' % (group.id, i), user.id):
            return True

    return False
    
def set_user_online_global(user, now=None, r=None):
    now = now or (int(time.time()) / 60)
    r = r or _get_redis()

    global_online_now = 'online_%i' % now

    preexist = r.exists(global_online_now)

    r.sadd(global_online_now, user.id)

    if not preexist:
        r.expire(global_online_now, 300)
   
def set_user_online_group(user, group, now=None, r=None):
    now = now or (int(time.time()) / 60)
    r = r or _get_redis()

    group_online_now = '%i_online_%i' % (group.id, now)
    user_groups = 'user_%i_groups' % user.id

    r.sadd(user_groups, group.id)

    preexist = r.exists(group_online_now)
    r.sadd(group_online_now, user.id)

    if not preexist:
        r.expire(group_online_now, 300)
    
def set_user_offline(user, r=None):
    r = r or _get_redis()

    now = int(time.time()) / 60

    online = False
    groups = []

    # remove from online
    for i in xrange(now, now-settings.USER_IDLE_TIME, -1):
        if r.srem('online_%i' % i, user.id):
            online = True

    # if user was online
    if online:
        # for each group it was in, remove from online
        for group_id in r.smembers('user_%i_groups' % user.id):
            group_id = int(group_id)
            online = False
            for i in xrange(now, now-settings.USER_IDLE_TIME, -1):
                if r.srem('%i_online_%i' % (group_id, i), user.id):
                    online = True
            # if removed, add to list
            if online: groups.append(group_id)

    r.delete('user_%i_groups' % user.id)

    return groups
   

def send_new_user_email(user):
    return send_mail("[muxlist] New user: %s" % user.username, render_to_string('email/new_user.html', {'user': user}), settings.SERVER_EMAIL, [a[1] for a in settings.ADMINS])

def send_invite_request_email(ir):
    return send_mail("[muxlist] Invite request: %s" % ir.email, render_to_string('email/invite_request.html', {'invite_request': ir}), settings.SERVER_EMAIL, [a[1] for a in settings.ADMINS])
