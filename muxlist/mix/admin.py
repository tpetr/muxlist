from django.contrib import admin
from muxlist.mix.models import Group

def recalculate_queued_count(modeladmin, request, queryset):
    for g in queryset:
        g.recalculate_queued()
recalculate_queued_count.short_description = 'Recalculate queued count'

class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'now_playing', 'queued_tracks']
    actions = [recalculate_queued_count]

admin.site.register(Group, GroupAdmin)
