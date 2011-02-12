from django.http import HttpResponse, Http404

def heartbeat(request):
    if not request.is_authenticated(): raise Http404

    request.user.heartbeat()

    return HttpResponse()
