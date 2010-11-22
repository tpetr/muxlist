from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from muxlist.music.forms import UploadForm

@login_required
def index(request):
    profile = request.user.get_profile()
    form = UploadForm()
    return render_to_response('music/index.html', {'user': request.user, 'uploaded_tracks': profile.uploaded_tracks.all(), 'favorite_tracks': profile.favorite_tracks.all(), 'form': form, 'groups': request.user.membership.all()})

@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(user=request.user)
            return HttpResponseRedirect(request.REQUEST.get('next', ''))
    else:
        form = UploadForm()

    return render_to_response('music/upload.html', {'form': form})
