from django.conf.urls.defaults import *

urlpatterns = patterns('muxlist.restq.views',
    (r'^$', 'index'),
    url(r'^connect$', 'connect', name='connect'),
    url(r'^disconnect$', 'disconnect', name='disconnect'),
    url(r'^subscribe$', 'subscribe', name='subscribe'),
    url(r'^unsubscribe$', 'unsubscribe', name='unsubscribe'),
    url(r'^send$', 'send', name='send'),
)
