from django.conf.urls.defaults import *

urlpatterns = patterns('muxlist.mix.views',
    (r'^(?P<group_name>.*)/add/$', 'add_message'),
    (r'^(?P<group_name>.*)/next/$', 'next_track'),
    (r'^(?P<group_name>.*)/force-next/$', 'next_track_force'),
    (r'^(?P<group_name>.*)/current/$', 'current_track'),
    (r'^(?P<group_name>.*)/$', 'index'),
)
