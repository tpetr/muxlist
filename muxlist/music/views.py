from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
import tempfile

from muxlist.music.forms import UploadForm, UploadForm2
import hashlib
from shutil import copyfile
from django.core.files.uploadedfile import TemporaryUploadedFile

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

@login_required
def upload2(request):
    if request.method == 'POST':
	if 'HTTP_X_FILE_NAME' in request.META:
            tf = TemporaryUploadedFile('rawdata', request.META['HTTP_X_FILE_TYPE'], int(request.META['CONTENT_LENGTH']), None)
            chunk = ' '
            while len(chunk) > 0:
                chunk = request.read(1024)
                tf.write(chunk)
            tf.seek(0)
            request.FILES['file'] = tf
        try:
            form = UploadForm2(data=request.POST, files=request.FILES)
            if form.is_valid():
                track = form.save(user=request.user)
                return HttpResponse(track.id)
        except Exception, e:
            print "Exception: %s" % e
            raise e
    else:
        form = UploadForm2()

    return render_to_response('music/upload2.html', {'form': form})
