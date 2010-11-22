from django.conf.urls.defaults import *

urlpatterns = patterns('muxlist.mix.views',
    (r'^(?P<group_name>.*)/xspf$', 'xspf'),
    (r'^(?P<group_name>.*)/$', 'index'),
)
