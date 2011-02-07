from django.contrib import admin
from muxlist.account.models import InviteRequest, Invite, UserProfile

admin.site.register(InviteRequest)
admin.site.register(Invite)
admin.site.register(UserProfile)
