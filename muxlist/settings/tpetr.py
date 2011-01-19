__ALL__ = ('DATABASES', 'MEDIA_URL')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'muxlist'
        'USER': 'audbly',
        'PASSWORD': 'BuddyTheCat',
    },
}

MEDIA_URL = 'http://muxli.st/media/'
