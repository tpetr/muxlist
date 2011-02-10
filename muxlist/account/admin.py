from django.contrib import admin
from muxlist.account.models import InviteRequest, Invite, UserProfile
import hashlib
from django.core.mail import send_mail
from django.template.loader import render_to_string
from settings import HOSTNAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from boto.ses import SESConnection

def send_invite(modeladmin, request, queryset):
    for r in queryset:
        h = hashlib.md5("%s%sfunkyfresh" % (request.user.id, r.email))
        i = Invite.objects.create(owner=request.user, email=r.email, code=h.hexdigest())
        r.delete()
        c = SESConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        send_mail("[muxlist] You're invited!", render_to_string('email/invite.html', {'hostname': HOSTNAME, 'invite': i}), 'trpetr@gmail.com', [i.email])
send_invite.short_description = "Send invites"

class InviteRequestAdmin(admin.ModelAdmin):
    actions = [send_invite]

admin.site.register(InviteRequest, InviteRequestAdmin)
admin.site.register(Invite)
admin.site.register(UserProfile)
