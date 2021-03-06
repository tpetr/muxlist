from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
import tempfile

from muxlist.music.forms import UploadForm, SliceUploadForm
import hashlib
from shutil import copyfile
from muxlist.music.decorators import move_rawdata_to_files
from muxlist.music.models import TrackLocation

from muxlist.mix.models import Group
from muxlist.music.signals import track_uploaded

@login_required
@move_rawdata_to_files
def begin_slice(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if request.method == 'POST':
        form = SliceUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            if form.cleaned_data['group']:
                form.cleaned_data['group'].user_heartbeat(request.user)
            begin_hash = hashlib.md5(form.cleaned_data['file'].read(100)).hexdigest()
            try:
                tl = TrackLocation.objects.get(begin_hash=begin_hash, size=request.META['HTTP_X_FILE_SIZE'])
                if request.user in tl.track.uploaded_by.all():
                    track_uploaded.send(sender=None, track=tl.track, group=group, user=request.user)
                    return HttpResponse()
            except TrackLocation.DoesNotExist:
                return HttpResponse(status=404)
            request.session['begin_hash'] = begin_hash
            return HttpResponse(status=402)
        else:
            return HttpResponse("invalid: %s" % (', '.join(form.errors)), status=500)
    return HttpResponse('Must POST', status=500)

@login_required
@move_rawdata_to_files
def middle_slice(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if request.method == 'POST':
        form = SliceUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            begin_hash = request.session['begin_hash']
            middle_hash = hashlib.md5(form.cleaned_data['file'].read(100)).hexdigest()
            print "size = %s, begin_hash=%s, middle_hash = %s" % (request.META['HTTP_X_FILE_SIZE'], begin_hash, middle_hash)
            try:
                tl = TrackLocation.objects.get(begin_hash=begin_hash, middle_hash=middle_hash, size=request.META['HTTP_X_FILE_SIZE'])
                if request.user in tl.track.uploaded_by.all():
                    track_uploaded.send(sender=None, track=tl.track, group=group, user=request.user)
                    return HttpResponse()
            except TrackLocation.DoesNotExist:
                return HttpResponse(status=404)
            request.session['middle_hash'] = middle_hash
            return HttpResponse(status=402)
        else:
            return HttpResponse("invalid: %s" % (', '.join(form.errors)), status=500)
    return HttpResponse('Must POST', status=500)

@login_required
@move_rawdata_to_files
def end_slice(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if request.method == 'POST':
        form = SliceUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            begin_hash = request.session['begin_hash']
            middle_hash = request.session['middle_hash']
            end_hash = hashlib.md5(form.cleaned_data['file'].read(100)).hexdigest()
            print "size = %s, begin_hash=%s, middle_hash = %s, end_hash = %s" % (request.META['HTTP_X_FILE_SIZE'], begin_hash, middle_hash, end_hash)
            try:
                tl = TrackLocation.objects.get(begin_hash=begin_hash, middle_hash=middle_hash, end_hash=end_hash, size=request.META['HTTP_X_FILE_SIZE'])
                track_uploaded.send(sender=None, track=tl.track, group=group, user=request.user)
                return HttpResponse()
            except TrackLocation.DoesNotExist: pass
            return HttpResponse(status=404)
        else:
            return HttpResponse("invalid: %s" % (', '.join(form.errors)), status=500)
    return HttpResponse('Must POST', status=500)

@login_required
@move_rawdata_to_files
def upload(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if request.method == 'POST':
        form = UploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            track = form.save(user=request.user)
            track_uploaded.send(sender=None, track=track, group=group, user=request.user)
            return HttpResponse()
        else:
            return HttpResponse("invalid: %s" % (', '.join(form.errors)), status=500)
    else:
        form = UploadForm()

    return render_to_response('music/upload.html', {'form': form})
