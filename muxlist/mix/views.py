from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from muxlist.mix.models import Group
from muxlist.music.forms import UploadForm
from django.contrib.auth.decorators import login_required

def index(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if not (group.is_public or (request.user.is_authenticated() and request.user in group.collaborators.all())):
       return HttpResponseRedirect('/account/login?next=%s' % request.path)
    entries = group.entries.all()
    form = UploadForm()
    return render_to_response('mix/group.html', {'group': group, 'entries': entries, 'form': form, 'user': request.user})

def xspf(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if not (group.is_public or (request.user.is_authenticated() and request.user in group.collaborators.all())):
       return HttpResponseRedirect('/account/login?next=%s' % request.path)
    return render_to_response('mix/xspf.xml', {'entries': group.entries.all()}, mimetype="application/xspf+xml")
