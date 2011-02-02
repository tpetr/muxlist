from django.conf.urls.defaults import *

urlpatterns = patterns('muxlist.mix.views',
    (r'^(?P<group_name>.*)/add/$', 'add_message'),
    (r'^(?P<group_name>.*)/next/$', 'next_song'),
    (r'^(?P<group_name>.*)/current/$', 'current_song'),
    (r'^(?P<group_name>.*)/$', 'index'),
)
