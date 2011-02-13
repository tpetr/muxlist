from django.template.loader import render_to_string
from django.core.mail import send_mail
from settings import ADMINS

import time, redis
import settings

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
    return send_mail("[muxlist] New user: %s" % user.username, render_to_string('email/new_user.html', {'user': user}), 'trpetr@gmail.com', [a[1] for a in ADMINS])
