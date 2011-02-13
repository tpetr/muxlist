from django.conf.urls.defaults import *

urlpatterns = patterns('muxlist.comet.views',
    (r'^disconnect/$', 'disconnect'),
)
