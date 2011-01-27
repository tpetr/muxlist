from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
import tempfile

from muxlist.music.forms import UploadForm, SliceUploadForm
import hashlib
from shutil import copyfile
from muxlist.music.decorators import move_rawdata_to_files
from muxlist.music.models import TrackLocation

@login_required
def index(request):
    profile = request.user.get_profile()
    form = UploadForm()
    return render_to_response('music/index.html', {'user': request.user, 'uploaded_tracks': profile.uploaded_tracks.all(), 'favorite_tracks': profile.favorite_tracks.all(), 'form': form, 'groups': request.user.membership.all()})

@login_required
@move_rawdata_to_files
def begin_slice(request):
    if request.method == 'POST':
        form = SliceUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            begin_hash = hashlib.md5(form.cleaned_data['file'].read(100)).hexdigest()
            print "size = %s, begin_hash = %s" % (request.META['HTTP_X_FILE_SIZE'], begin_hash)
            try:
                tl = TrackLocation.objects.get(begin_hash=begin_hash, size=request.META['HTTP_X_FILE_SIZE'])
                if request.user in tl.track.uploaded_by.all():
                    return HttpResponse(tl.track.id)
            except TrackLocation.DoesNotExist:
                return HttpResponse(status=404)
            request.session['begin_hash'] = begin_hash
            return HttpResponse(status=402)
        else:
            raise Http404('Unknown song')
    return HttpResponse('Must POST', status=500)

@login_required
@move_rawdata_to_files
def middle_slice(request):
    if request.method == 'POST':
        form = SliceUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            begin_hash = request.session['begin_hash']
            middle_hash = hashlib.md5(form.cleaned_data['file'].read(100)).hexdigest()
            print "size = %s, begin_hash=%s, middle_hash = %s" % (request.META['HTTP_X_FILE_SIZE'], begin_hash, middle_hash)
            try:
                tl = TrackLocation.objects.get(begin_hash=begin_hash, middle_hash=middle_hash, size=request.META['HTTP_X_FILE_SIZE'])
                if request.user in tl.track.uploaded_by.all():
                    return HttpResponse(tl.track.id)
            except TrackLocation.DoesNotExist:
                return HttpResponse(status=404)
            request.session['middle_hash'] = middle_hash
            return HttpResponse(status=402)
        else:
            raise Http404('Unknown song')
    return HttpResponse('Must POST', status=500)

@login_required
@move_rawdata_to_files
def end_slice(request):
    if request.method == 'POST':
        form = SliceUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            begin_hash = request.session['begin_hash']
            middle_hash = request.session['middle_hash']
            end_hash = hashlib.md5(form.cleaned_data['file'].read(100)).hexdigest()
            print "size = %s, begin_hash=%s, middle_hash = %s, end_hash = %s" % (request.META['HTTP_X_FILE_SIZE'], begin_hash, middle_hash, end_hash)
            try:
                tl = TrackLocation.objects.get(begin_hash=begin_hash, middle_hash=middle_hash, end_hash=end_hash, size=request.META['HTTP_X_FILE_SIZE'])
                return HttpResponse(tl.track.id)
            except TrackLocation.DoesNotExist: pass
            return HttpResponse(status=404)
        else:
            raise Http404('Unknown song')
    return HttpResponse('Must POST', status=500)

@login_required
@move_rawdata_to_files
def upload(request):
    if request.method == 'POST':
        form = UploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            track = form.save(user=request.user)
            return HttpResponse(track.id)
        else:
            return HttpResponse("invalid", status=500)
    else:
        form = UploadForm()

    return render_to_response('music/upload.html', {'form': form})
