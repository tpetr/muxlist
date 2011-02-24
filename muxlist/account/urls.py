from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'account/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'account/logout.html', 'next_page': '/'}),
)
