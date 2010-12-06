from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from muxlist.mix.models import Group
from muxlist.music.forms import UploadForm
from django.contrib.auth.decorators import login_required
from muxlist.music.models import Track

import stomp
import json
import time

def index(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if not (group.is_public or (request.user.is_authenticated() and request.user in group.collaborators.all())):
       return HttpResponseRedirect('/account/login?next=%s' % request.path)
    entries = group.entries.all()
    form = UploadForm()
    return render_to_response('mix/group.html', {'group': group, 'entries': entries, 'form': form, 'user': request.user, 'tracks': request.user.get_profile().uploaded_tracks.all()})

def xspf(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if not (group.is_public or (request.user.is_authenticated() and request.user in group.collaborators.all())):
       return HttpResponseRedirect('/account/login?next=%s' % request.path)
    return render_to_response('mix/xspf.xml', {'entries': group.entries.all()}, mimetype="application/xspf+xml")

def add_message(request, group_name):
    conn = stomp.Connection()
    conn.start()
    conn.connect()
    conn.subscribe(destination='/mix/%s' % group_name, ack='auto')
    msg = json.dumps({"type": "chat", "user": request.user.username,"message":request.REQUEST.get('msg', '(blank)'), "time":time.strftime("%H:%S-%d/%m/%Y")})
    conn.send(msg, destination='/mix/%s' % group_name)
    return HttpResponse('ok')

def add_song(request, group_name):
    conn = stomp.Connection()
    conn.start()
    conn.connect()
    conn.subscribe(destination='/mix/%s' % group_name, ack='auto')
    track = Track.objects.get(id=request.REQUEST['id'])
    msg = json.dumps({'type': 'song', 'user': request.user.username, 'artist': track.artist.name, 'title': track.title, 'url': track.get_location().url})
    conn.send(msg, destination='/mix/%s' % group_name)
    return HttpResponse('ok')
