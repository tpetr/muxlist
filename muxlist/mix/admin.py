from django.contrib import admin
from muxlist.mix.models import Group, PlaylistEntry

class PlaylistEntryAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'index', 'track')

admin.site.register(Group)
admin.site.register(PlaylistEntry, PlaylistEntryAdmin)
