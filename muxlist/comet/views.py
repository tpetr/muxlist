from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from muxlist.mix.models import Group, _get_redis
import json, time

from muxlist.comet.utils import send_user_leave
from muxlist.account.utils import set_user_offline

import settings

class LightweightGroup(object):
    def __init__(self, group_id):
        self.id = group_id

def disconnect(request):
    if not request.user.is_authenticated(): raise Http404

    user = request.user

    for group_id in set_user_offline(user):
        send_user_leave(user, LightweightGroup(int(group_id)))

    return HttpResponse()
