from django.contrib import admin
from muxlist.music.models import Artist, Album, Track, TrackLocation

admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Track)
admin.site.register(TrackLocation)
