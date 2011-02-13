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
    (r'^$', 'muxlist.account.views.launch_page'),
    (r'^thanks/$', 'muxlist.account.views.launch_page_thanks'),
    (r'^invite/send/$', 'muxlist.account.views.send_invite'),
    (r'^invite/(?P<code>[a-zA-Z0-9]+)/$', 'muxlist.account.views.invite'),
    (r'^okay/$', 'muxlist.account.views.okay'),
    (r'^mix/', include('muxlist.mix.urls')),
    (r'^music/', include('muxlist.music.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^account/', include('muxlist.account.urls')),
    (r'^restq/', include('muxlist.restq.urls')),
    (r'^comet/', include('muxlist.comet.urls')),
)
