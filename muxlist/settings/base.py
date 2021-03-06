# Django settings for muxlist project.
import os, sys

ROOT_PATH = os.path.abspath("%s/../../" % os.path.dirname(__file__))
if os.path.join(ROOT_PATH, 'lib/') not in sys.path:
    sys.path.insert(0, os.path.join(ROOT_PATH, 'lib/'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Tom Petr', 'trpetr@gmail.com'),
)

NEW_USER_NOTIFICATION = False
INVITE_REQUEST_NOTIFICATION = False

USER_IDLE_TIME = 5

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(ROOT_PATH, 'etc/muxlist.sqlite'),
    }
}

LOGIN_REDIRECT_URL = '/dashboard/'

SERVER_EMAIL = 'no-reply@muxli.st'
EMAIL_SUBJECT_PREFIX = '[muxlist] '

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'zoq9j7es_0rnr7cu6vwv^+@mkw%jz47$j!h7x0c$4ml8_k0olc'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'muxlist.urls'

TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, 'templates/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'muxlist.music',
    'muxlist.mix',
    'muxlist.account',
    'muxlist.comet',
    'registration',
)

AUTH_PROFILE_MODULE = 'account.UserProfile'
ACCOUNT_ACTIVATION_DAYS = 7

LOGIN_URL = '/account/login'

HOSTNAME = 'localhost'

AWS_ACCESS_KEY = '1GDBYBN31QAR4P85HQG2'
AWS_ACCESS_KEY_ID = '1GDBYBN31QAR4P85HQG2'
AWS_SECRET_ACCESS_KEY = 'rcU7fQs/fOys/lQIJcNPZ65bk7kpyGJb5POommIV'

EMAIL_BACKEND = 'django_ses.SESBackend'
