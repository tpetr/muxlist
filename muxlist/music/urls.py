from django.conf.urls.defaults import *

urlpatterns = patterns('muxlist.music.views',
    (r'^$', 'index'),
    (r'^begin_slice/?$', 'begin_slice'),
    (r'^middle_slice/?$', 'middle_slice'),
    (r'^end_slice/?$', 'end_slice'),
    (r'^upload/?$', 'upload'),
)
