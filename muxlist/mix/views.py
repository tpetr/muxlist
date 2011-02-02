from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from muxlist.mix.models import Group
from muxlist.music.forms import UploadForm
from django.contrib.auth.decorators import login_required
from muxlist.music.models import Track
from settings import HOSTNAME

import stomp
import json
import time
import redis

from django.contrib.auth.models import User

from muxlist.music.signals import track_uploaded
from django.dispatch import receiver

def debug_enqueue(group_name, user, track): 
    conn = stomp.Connection()
    conn.start()
    conn.connect()
    conn.subscribe(destination='/mix/%s' % group_name, ack='auto')
    msg = json.dumps({'type': 'debug', 'msg': '%s enqueued %s' % (user, track)})
    conn.send(msg, destination='/mix/%s' % group_name)

def send_current_song(group_name, user):
    print "send current song to %s" % user
    r = redis.Redis(host='localhost', port=6379, db=0)
    if not r.exists('%s_current' % group_name):
        return

    track = Track.objects.get(id=r.get('%s_current' % group_name))
    playing_user = User.objects.get(id=r.get('%s_current_user' % group_name))
    print "it's %s" % track
    
    conn = stomp.Connection()
    conn.start()
    conn.connect()
    conn.subscribe(destination='/user/%s' % user.id, ack='auto')
    alb = '???'
    art = ''
    if track.album: alb = track.album.name
    if track.album: atb = track.album.image
    msg = json.dumps({'type': 'song', 'user': playing_user.username, 'artist': track.artist.name, 'album': alb, 'cover_art': art, 'title': track.title, 'url': track.get_location().url, 'time': track.length - r.ttl('%s_current' % group_name)})
    conn.send(msg, destination='/user/%s' % user.id)

def send_next_song(group_name):
    print "send next song"
    r = redis.Redis(host='localhost', port=6379, db=0)
    user_count = r.scard('%s_users' % group_name)
    if user_count == 0:
        print "no tracks to enqueue"
        return

    user_id = None
    track_id = None

    # loop until we find a track
    while track_id == None:
        user_id = r.spop('%s_users' % group_name)
        print "Got user id %s, has %s queued" % (user_id, r.llen('%s_%s_queue' % (group_name, user_id)))
        if user_id == None:
            return # no more users, we're kaput

        track_id = r.lpop('%s_%s_queue' % (group_name, user_id))
        print "Got track id %s" % track_id
        if track_id != None:
            r.sadd('%s_users' % group_name, user_id)

    r.set('%s_current' % group_name, track_id)
    r.set('%s_current_user' % group_name, user_id)
    r.expire('%s_current' % group_name, Track.objects.get(id=track_id).length)

    user = User.objects.get(id=user_id)
    track = Track.objects.get(id=track_id)
    print "Going with %s from %s" % (track, user)
    
    conn = stomp.Connection()
    conn.start()
    conn.connect()
    conn.subscribe(destination='/mix/%s' % group_name, ack='auto')
    alb = '???'
    art = ''
    if track.album: alb = track.album.name
    if track.album: atb = track.album.image
    msg = json.dumps({'type': 'song', 'user': user.username, 'artist': track.artist.name, 'album': alb, 'cover_art': art, 'title': track.title, 'url': track.get_location().url})
    conn.send(msg, destination='/mix/%s' % group_name)

@receiver(track_uploaded, sender=None)
def tu(sender, **kwargs):
    group_name = 'test'
    user = kwargs['user']
    track = kwargs['track']

    r = redis.Redis(host='localhost', port=6379, db=0)
    r.rpush('%s_%s_queue' % (group_name, user.id), track.id)
    debug_enqueue(group_name, user, track)
    r.sadd('%s_users' % group_name, user.id)
    if (r.ttl('%s_current' % group_name) == -1):
        send_next_song(group_name)

def next_song(request, group_name):
    r = redis.Redis(host='localhost', port=6379, db=0)
    if r.ttl('%s_current' % group_name) > 0:
        raise Http404()

    send_next_song(group_name)

    return HttpResponse()

def current_song(request, group_name):
    r = redis.Redis(host='localhost', port=6379, db=0)
    if r.ttl('%s_current' % group_name) > 0:
        send_current_song(group_name, request.user)
    else:
        send_next_song(group_name)
    return HttpResponse()

def force_next(request, group_name):
    pass

def index(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if not (group.is_public or (request.user.is_authenticated() and request.user in group.collaborators.all())):
       return HttpResponseRedirect('/account/login?next=%s' % request.path)
    entries = group.entries.all()
    form = UploadForm()
    return render_to_response('mix/group.html', {'group': group, 'entries': entries, 'form': form, 'user': request.user, 'hostname': HOSTNAME})

def add_message(request, group_name):
    conn = stomp.Connection()
    conn.start()
    conn.connect()
    conn.subscribe(destination='/mix/%s' % group_name, ack='auto')
    msg = json.dumps({"type": "chat", "user": request.user.username,"message":request.REQUEST.get('msg', '(blank)'), "time":time.strftime("%H:%S-%d/%m/%Y")})
    conn.send(msg, destination='/mix/%s' % group_name)
    return HttpResponse('ok')
