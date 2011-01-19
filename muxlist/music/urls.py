from django.conf.urls.defaults import *

urlpatterns = patterns('muxlist.music.views',
    (r'^$', 'index'),
    (r'^upload/?$', 'upload'),
    (r'^upload2/?$', 'upload2'),
)
