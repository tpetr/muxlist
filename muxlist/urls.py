from django.conf.urls.defaults import *
import os, sys

ROOT_PATH = os.path.abspath("%s/../" % os.path.dirname(__file__))

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = []

if 'django.core.management.commands.runserver' in sys.modules:
    urlpatterns += patterns('', (r'static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(ROOT_PATH, 'static/')}))
    urlpatterns += patterns('', (r'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(ROOT_PATH, 'media/')}))

urlpatterns += patterns('',
    (r'^mix/', include('muxlist.mix.urls')),
    (r'^music/', include('muxlist.music.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^account/', include('muxlist.account.urls')),
)
