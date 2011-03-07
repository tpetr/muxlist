__ALL__ = ('DATABASES', 'MEDIA_URL', 'HOSTNAME', 'DEBUG', 'NEW_USER_NOTIFICATION', 'INVITE_REQUEST_NOTIFICATION')

NEW_USER_NOTIFICATION = True
INVITE_REQUEST_NOTIFICATION = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'muxlist',
        'USER': 'audbly',
        'PASSWORD': 'BuddyTheCat',
    },
}

MEDIA_URL = 'http://muxli.st/media/'

HOSTNAME = 'muxli.st'

DEBUG = True
