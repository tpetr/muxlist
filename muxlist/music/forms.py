from django import forms
from muxlist.music.models import Track, TrackLocation, Artist, Album
from muxlist.mix.models import Group

from muxlist.music.utils import get_track_data_from_url, get_track_data_from_file, upload_to_s3

from muxlist.comet.utils import send_debug

from django.db.models import Max

import hashlib

import settings
import os

import mad

import urllib2
from BeautifulSoup import BeautifulSoup

AUDIO_MIMETYPES = ('audio/mp3', 'application/mp3', 'audio/mpeg3', 'audio/mpeg')

class SliceUploadForm(forms.Form):
    file = forms.FileField()
    group = forms.ModelChoiceField(label="", queryset=Group.objects.all(), widget=forms.HiddenInput(), required=False)

    def clean_file(self):
        if self.cleaned_data['file'].content_type not in AUDIO_MIMETYPES:
            raise forms.ValidationError("Must be MP3")
        return self.cleaned_data['file']

class UploadForm(forms.Form):
    file = forms.FileField()
    group = forms.ModelChoiceField(label="", queryset=Group.objects.all(), widget=forms.HiddenInput(), required=False)

    def clean_file(self):
        if self.cleaned_data['file'].content_type not in AUDIO_MIMETYPES:
            raise forms.ValidationError('Must be MP3')
        return self.cleaned_data['file']

    def save(self, user):
        f = self.cleaned_data['file']
        g = Group.objects.get(name='test')
        if settings.DEBUG: send_debug('Calculating full hash', g)

        full_md5 = hashlib.md5()
        for chunk in f.chunks():
            full_md5.update(chunk)
        full_hash = full_md5.hexdigest()

        if settings.DEBUG: send_debug('Done, calculating part hashes', g)

        f.seek(0)
        begin_hash = hashlib.md5(f.read(100)).hexdigest()
        f.seek((len(f)/2)-50)
        middle_hash = hashlib.md5(f.read(100)).hexdigest()
        f.seek(len(f)-100)
        end_hash = hashlib.md5(f.read(100)).hexdigest()

        try:
            tl = TrackLocation.objects.get(hash=full_hash, size=len(f))
            track = tl.track
        except TrackLocation.DoesNotExist:
            if settings.DEBUG: send_debug('uploading to s3', g);
            try:
                url = upload_to_s3(f, full_hash)
            except Exception, e:
                if settings.DEBUG: send_debug('exception: %s' % e, g)
            if settings.DEBUG: send_debug('done, getting length', g)

            f.seek(0)
            mf = mad.MadFile(f)
            length = mf.total_time() / 1000

            tl = TrackLocation(url=url, size=len(f), begin_hash=begin_hash, middle_hash=middle_hash, end_hash=end_hash, hash=full_hash)

            artist_name, album_name, track_name, year, hash = get_track_data_from_file(f.temporary_file_path())

            
            if artist_name != '':
                artist = Artist.objects.get_or_create(name=artist_name)[0]
            else:
                artist = None
            
            if album_name != '':
                album, created = Album.objects.get_or_create(artist=artist, name=album_name)
                if created:
                    try:
                        r = urllib2.urlopen('http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=72553de16666cad1c8f7e319292e9123&artist=%s&album=%s' % (artist_name.replace(' ', '%20'), album_name.replace(' ', '%20')))
                        bs = BeautifulSoup(r.read())
                        album.image = bs.album.image.nextSibling.nextSibling.nextSibling.nextSibling.contents[0]
                        album.save()
                    except: pass
            else:
                album = None

            track = Track.objects.get_or_create(title=track_name, album=album, year=year, artist=artist, length=length)[0]

            tl.track = track
            tl.save()

        track.uploaded_by.add(user)

        return track
