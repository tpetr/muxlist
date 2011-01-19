from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse

import json

restq_info = json.dumps(dict([(name, "http://localhost:8000/restq/%s" % name) for name in ('connect', 'disconnect', 'subscribe', 'unsubscribe', 'send')]))

def index(request):
    if request.META.get('REMOTE_ADDR', '') != '127.0.0.1':
        raise Http404()
    return HttpResponse(restq_info)

def send(request):
    print "send"
    return HttpResponse("{}")

def connect(request):
    print "connect"
    return HttpResponse("{}")

def disconnect(request):
    print "disconnect"
    return HttpResponse("{'allow': 'yes'}")

def subscribe(request):
    print "subscribe"
    return HttpResponse("{}")

def unsubscribe(request):
    print "unsubscribe"
    return HttpResponse("{'allow': 'yes'}")
