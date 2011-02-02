import django.dispatch

track_uploaded = django.dispatch.Signal(providing_args=['track', 'group', 'user'])
