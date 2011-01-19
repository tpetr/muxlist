from django import forms
from muxlist.music.models import Track, TrackLocation, Artist, Album
from muxlist.mix.models import Group, PlaylistEntry

from muxlist.music.util import get_track_data_from_url, get_track_data_from_file

from django.db.models import Max

import hashlib

import settings
import os
class UploadForm2(forms.Form):
    file = forms.FileField()
    group = forms.ModelChoiceField(label="", queryset=Group.objects.all(), widget=forms.HiddenInput(), required=False)

    def save(self, user):
        f = self.cleaned_data['file']

        if f.content_type != 'audio/mp3':
            raise forms.ValidationError('Not a music file')

        md5 = hashlib.md5()
        for chunk in f.chunks():
            md5.update(chunk)
        mp3_hash = md5.hexdigest()

        try:
            track = Track.objects.get(hash=mp3_hash)
        except Track.DoesNotExist:
            filename = os.path.join(settings.MEDIA_ROOT, 'music/%s.mp3' % mp3_hash)
            fp = open(filename, 'wb+')
            for chunk in f.chunks():
                fp.write(chunk)
            fp.close()

            tl = TrackLocation(url="http://cambridge.tpetr.net:8000/media/music/%s.mp3" % mp3_hash)

            artist_name, album_name, track_name, year, hash = get_track_data_from_file(filename)

            
            if artist_name != '':
                artist = Artist.objects.get_or_create(name=artist_name)[0]
            else:
                artist = None
            
            if album_name != '':
                album = Album.objects.get_or_create(artist=artist, name=album_name)[0]
            else:
                album = None

            track = Track.objects.get_or_create(title=track_name, album=album, year=year, artist=artist, hash=mp3_hash)[0]

            tl.track = track
            tl.save()

        user.get_profile().uploaded_tracks.add(track)

        return track


    

class UploadForm(forms.Form):
    url = forms.URLField()
    group = forms.ModelChoiceField(label="", queryset=Group.objects.all(), widget=forms.HiddenInput(), required=False)

    def save(self, user):
        try:
            tl = TrackLocation.objects.get(url=self.cleaned_data['url'])
            track = tl.track
        except TrackLocation.DoesNotExist:
            tl = TrackLocation(url=self.cleaned_data['url'])

            artist_name, album_name, track_name, year, hash = get_track_data_from_url(self.cleaned_data['url'])

            
            if artist_name != '':
                artist = Artist.objects.get_or_create(name=artist_name)[0]
            else:
                artist = None
            
            if album_name != '':
                album = Album.objects.get_or_create(artist=artist, name=album_name)[0]
            else:
                album = None

            track = Track.objects.get_or_create(title=track_name, album=album, year=year, artist=artist)[0]

            tl.track = track
            tl.save()

        user.get_profile().uploaded_tracks.add(track)


        if self.cleaned_data['group']:
            index = (PlaylistEntry.objects.filter(user=user, group=self.cleaned_data['group']).aggregate(Max('index'))['index__max'] or 0) + 1
            pe = PlaylistEntry(user=user, group=self.cleaned_data['group'], track=track, index=index)
            pe.save()
