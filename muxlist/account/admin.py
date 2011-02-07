from django.contrib import admin
from muxlist.account.models import InviteRequest, Invite, UserProfile
import hashlib

def send_invite(modeladmin, request, queryset):
    for r in queryset:
        h = hashlib.md5("%s%sfunkyfresh" % (request.user.id, r.email))
        Invite.objects.create(owner=request.user, email=r.email, code=h.hexdigest())
        r.delete()
send_invite.short_description = "Send invites"

class InviteRequestAdmin(admin.ModelAdmin):
    actions = [send_invite]

admin.site.register(InviteRequest, InviteRequestAdmin)
admin.site.register(Invite)
admin.site.register(UserProfile)
