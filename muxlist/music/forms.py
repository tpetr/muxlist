from django import forms
from muxlist.music.models import Track, TrackLocation, Artist, Album
from muxlist.mix.models import Group, PlaylistEntry

from muxlist.music.util import get_track_data_from_url, get_track_data_from_file

from django.db.models import Max

import hashlib

import settings
import os

import mad

import urllib2
from BeautifulSoup import BeautifulSoup

AUDIO_MIMETYPES = ('audio/mp3', 'application/mp3', 'audio/mpeg3')

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

        full_md5 = hashlib.md5()
        for chunk in f.chunks():
            full_md5.update(chunk)
        full_hash = full_md5.hexdigest()
            

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
            filename = os.path.join(settings.MEDIA_ROOT, 'music/%s.mp3' % full_hash)
            fp = open(filename, 'wb+')
            for chunk in f.chunks():
                fp.write(chunk)
            fp.close()

            mf = mad.MadFile(filename)
            length = mf.total_time() / 1000

            tl = TrackLocation(url="%smusic/%s.mp3" % (settings.MEDIA_URL, full_hash), size=len(f), begin_hash=begin_hash, middle_hash=middle_hash, end_hash=end_hash, hash=full_hash)

            artist_name, album_name, track_name, year, hash = get_track_data_from_file(filename)

            
            if artist_name != '':
                artist = Artist.objects.get_or_create(name=artist_name)[0]
            else:
                artist = None
            
            if album_name != '':
                album, created = Album.objects.get_or_create(artist=artist, name=album_name)
                if created:
                    r = urllib2.urlopen('http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=b25b959554ed76058ac220b7b2e0a026&artist=%s&album=%s')
                    bs = BeautifulSoup(r.read())
                    album.image = bs.image[1]
                    album.save()
            else:
                album = None

            track = Track.objects.get_or_create(title=track_name, album=album, year=year, artist=artist, length=length)[0]

            tl.track = track
            tl.save()

        track.uploaded_by.add(user)

        return track
