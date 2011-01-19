from fabric.api import local, abort, run, cd, env, sudo
from fabric.utils import warn
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from datetime import date
import os

def dest_required(func):
    def decorator(*args, **kwargs):
        if not getattr(env, 'ready', False):
            abort('Command must be after valid destination (i.e. fab prod start_fcgi)')
        else:
            return func(*args, **kwargs)

    decorator.__doc__ = func.__doc__
    return decorator

def prod():
    'Points commands to production server'
    env.hosts = ['tpetr@muxli.st']
    env.directory = '/home/tpetr/repos/muxlist/'
    env.manage = os.path.join(env.directory, 'muxlist/manage.py')
    env.socket = os.path.join(env.directory, 'bin/fastcgi.socket')
    env.pidfile = os.path.join(env.directory, 'etc/django.pid')
    env.nginx = os.path.join(env.directory, 'etc/nginx/')
    env.target = 'prod'
    env.ready = True

@dest_required
def start_fcgi():
    'Start the Django FastCGI daemon'

    if exists(env.pidfile):
        abort('PID file already exists (%(pidfile)s), fcgi already running?' % env)
    else:
        run('%(manage)s runfcgi method=threaded socket=%(socket)s pidfile=%(pidfile)s' % env)
        run('chmod a+w %(socket)s' % env)

@dest_required
def stop_fcgi():
    'Stop the Django FastCGI daemon'

    if not exists(env.pidfile):
        warn('PID file does not exist (%(pidfile)s), you may have to manually kill the fcgi process' % env)
    else:
        run('kill -term `cat %(pidfile)s`' % env)
        run('rm %(pidfile)s' % env)

@dest_required
def maintenance():
    'Replace website with maintenance page'

    if exists('%(nginx)s/%(target)s.conf' % env):
        run('rm %(nginx)s/%(target)s.conf' % env)

    run('ln -s %(nginx)s/%(target)s_maintenance.conf %(nginx)s/%(target)s.conf' % env)

    sudo('nginx -s reload')

@dest_required
def online():
    'Replace maintenance page with normal site'

    if exists('%(nginx)s/%(target)s.conf' % env):
        run('rm %(nginx)s/%(target)s.conf' % env)

    run('ln -s %(nginx)s/%(target)s_django.conf %(nginx)s/%(target)s.conf' % env)

    sudo('nginx -s reload')

@dest_required
def publish():
    'Push changes to server'
    maintenance()

    stop_fcgi()

    with cd(env.directory):
        run('git stash > /dev/null')
        run('git pull')
        run('git stash pop > /dev/null')

    start_fcgi()

    online()
