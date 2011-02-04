from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    name = models.CharField(max_length=128)

    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.name

class Album(models.Model):
    name = models.CharField(max_length=128)
    artist = models.ForeignKey(Artist, related_name='albums')
    year = models.PositiveSmallIntegerField(blank=True, null=True)

    image = models.URLField(max_length=128, blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return u"%s [%s]" % (self.name, self.year)

class Track(models.Model):
    title = models.CharField(max_length=128)
    album = models.ForeignKey(Album, related_name='tracks', blank=True, null=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    artist = models.ForeignKey(Artist, related_name='tracks', blank=True, null=True)
    length = models.PositiveSmallIntegerField()

    uploaded_by = models.ManyToManyField(User, blank=True, related_name='uploaded_tracks')

    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)

    def get_location(self):
        return self.locations.filter(active=True)[0]
    
    def __unicode__(self):
        return u"%s - %s" % (self.artist.name, self.title)

    def __json__(self):
        return {'title': self.title, 'album': (self.album and self.album.name) or '???', 'artist': (self.artist and self.artist.name) or '???', 'cover_art': (self.album and self.album.image) or None, 'url': self.get_location().url}
    
class TrackLocation(models.Model):
    url = models.URLField(max_length=128)
    track = models.ForeignKey(Track, related_name='locations')

    size = models.PositiveIntegerField()
    hash = models.CharField(max_length=32)
    begin_hash = models.CharField(max_length=32)
    middle_hash = models.CharField(max_length=32)
    end_hash = models.CharField(max_length=32)

    active = models.BooleanField(default=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True, auto_now=True)

    def __unicode__(self):
        return self.url
