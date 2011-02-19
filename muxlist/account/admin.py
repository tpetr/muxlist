from django.contrib import admin
from muxlist.account.models import InviteRequest, Invite, UserProfile
import hashlib
from django.core.mail import send_mail
from django.template.loader import render_to_string
from settings import HOSTNAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ROOT_PATH
from boto.ses import SESConnection
import os, urllib2

from muxlist.account.utils import get_random_images

from PIL import Image


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

def set_random_image_missing(modeladmin, request, queryset):
    profiles = queryset.filter(picture_75=None)
    urls = get_random_images(len(profiles))
    for profile, url in zip(profiles, urls):
        r = urllib2.urlopen(url)
        fp = open(os.path.join(ROOT_PATH, 'static/profile/%s_75.jpg' % profile.user.username), "wb")
        fp.write(r.read())
        fp.close()
        im = Image.open(os.path.join(ROOT_PATH, 'static/profile/%s_75.jpg' % profile.user.username))
        im.thumbnail((20,20), Image.ANTIALIAS)
        im.save(os.path.join(ROOT_PATH, 'static/profile/%s_20.jpg' % profile.user.username))
        profile.picture_75 = "/static/profile/%s_75.jpg" % profile.user.username
        profile.picture_20 = "/static/profile/%s_20.jpg" % profile.user.username
        profile.save()
set_random_image_missing.short_description = "Set random profile picture where missing"

def set_random_image(modeladmin, request, queryset):
    profiles = queryset.all()
    urls = get_random_images(len(profiles))
    for profile, url in zip(profiles, urls):
        r = urllib2.urlopen(url)
        fp = open(os.path.join(ROOT_PATH, 'static/profile/%s_75.jpg' % profile.user.username), "wb")
        fp.write(r.read())
        fp.close()
        im = Image.open(os.path.join(ROOT_PATH, 'static/profile/%s_75.jpg' % profile.user.username))
        im.thumbnail((20,20), Image.ANTIALIAS)
        im.save(os.path.join(ROOT_PATH, 'static/profile/%s_20.jpg' % profile.user.username))
        profile.picture_75 = "/static/profile/%s_75.jpg" % profile.user.username
        profile.picture_20 = "/static/profile/%s_20.jpg" % profile.user.username
        profile.save()
set_random_image.short_description = "Set random profile picture"

class UserProfileAdmin(admin.ModelAdmin):
    actions = [set_random_image, set_random_image_missing]

admin.site.register(InviteRequest, InviteRequestAdmin)
admin.site.register(Invite)
admin.site.register(UserProfile, UserProfileAdmin)
