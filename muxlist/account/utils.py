from django.template.loader import render_to_string
from django.core.mail import send_mail
from settings import ADMINS

def send_new_user_email(user):
    return send_mail("[muxlist] New user: %s" % user.username, render_to_string('email/new_user.html', {'user': user}), 'trpetr@gmail.com', [a[1] for a in ADMINS])
