import stomp
import json

def _get_stomp():
    conn = stomp.Connection()
    conn.start()
    conn.connect()
    return conn
    
def send_debug(msg, group):
    conn = _get_stomp()
    msg = json.dumps({'type': 'debug', 'msg': msg})
    conn.send(msg, destination='/group/%s' % group.id)

def send_chat(msg, user, group):
    conn = _get_stomp()
    msg = json.dumps({'type': 'chat', 'msg': msg, 'user': user.username})
    conn.send(msg, destination='/group/%s' % group.id)

def send_track_update(track, group, user=None):
    conn = _get_stomp()
    msg = json.dumps({'type': 'track', 'user': user and user.username, 'track': track.__json__()})
    conn.send(msg, destination='/group/%s' % group.id)

def send_queue_update(count, group):
    conn = _get_stomp()
    msg = json.dumps({'type': 'queue', 'count': count})
    conn.send(msg, destination='/group/%s' % group.id)
