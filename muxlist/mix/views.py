from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from muxlist.mix.models import Group
from muxlist.music.forms import UploadForm
from django.contrib.auth.decorators import login_required
from muxlist.music.models import Track
from settings import HOSTNAME
from django.utils.html import escape

from muxlist.comet import utils as comet_utils
import json
import time

from django.contrib.auth.models import User

from muxlist.music.signals import track_uploaded
from django.dispatch import receiver

def heartbeat(request, group_name):
    if not request.user.is_authenticated(): raise Http404

    group = get_object_or_404(Group, name=group_name)

    group.user_heartbeat(request.user)

    return HttpResponse(json.dumps({'type': 'heartbeat', 'users': [u.username for u in group.get_users_online()]}))

@receiver(track_uploaded, sender=None)
def tu(sender, **kwargs):
    group = kwargs['group']
    user = kwargs['user']
    track = kwargs['track']

    group.enqueue_track(track, user)

def next_track(request, group_name):
    # get group
    group = get_object_or_404(Group, name=group_name)

    group.user_heartbeat(request.user)

    # check for next track
    if group.check_for_next_track()[0] == None: return HttpResponse(status=402)

    return HttpResponse()

def next_track_force(request, group_name):
    # get group
    group = Group.objects.get(name=group_name)

    # TODO: check for some kind of creds

    # user heartbeat
    group.user_heartbeat(request.user)

    comet_utils.send_chat('I just hit next. :-P', request.user, group)

    # next track!
    return HttpResponse(group.next_track())

def current_track(request, group_name):
    # get group
    group = Group.objects.get(name=group_name)
    
    # must be valid user
    if not (group.is_public or (request.user.is_authenticated() and request.user in group.collaborators.all())):
        return HttpResponse(status=401)

    group.user_heartbeat(request.user)

    frames = [{'type': 'heartbeat', 'users': [u.username for u in group.get_users_online()]}]

    # get current track
    track, user, started_at = group.get_current_track()

    # flip out it nothing's playing
    if track != None:
        frames.append({'type': 'track', 'track': track.__json__(), 'user': user.username, 'time': time.time() - float(started_at)})


    # return current track info
    return HttpResponse(json.dumps(frames))

def index(request, group_name):
    # get group
    group = get_object_or_404(Group, name=group_name)

    # if the group isnt public and the user isn't a collaborator, make them login
    if not (group.is_public or (request.user.is_authenticated() and request.user in group.collaborators.all())):
       return HttpResponseRedirect('/account/login?next=%s' % request.path)

    # render page
    return render_to_response('mix/group.html', {'group': group, 'user': request.user, 'session_key': request.session.session_key, 'hostname': HOSTNAME})

def add_message(request, group_name):
    # must be POST
    if request.method != 'POST': raise Http404()

    # must contain message
    if 'msg' not in request.POST: return HttpResponse(status=500)

    # get group
    group = get_object_or_404(Group, name=group_name)

    # must be valid user
    if not (group.is_public or (request.user.is_authenticated() and request.user in group.collaborators.all())):
        return HttpResponse(status=401)

    group.user_heartbeat(request.user)

    # send chat
    comet_utils.send_chat(escape(request.POST['msg']), request.user, group)

    return HttpResponse()
