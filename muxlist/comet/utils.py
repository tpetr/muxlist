import stomp
import json

def _get_stomp():
    conn = stomp.Connection()
    conn.start()
    conn.connect()
    return conn
    
def send_debug(msg, group=None):
    conn = _get_stomp()
    msg = json.dumps([{'type': 'debug', 'msg': msg},])
    id = 1
    if group: id = group.id
    conn.send(msg, destination='/group/%s' % id)

def send_chat(msg, user, group):
    conn = _get_stomp()
    msg = json.dumps([{'type': 'chat', 'msg': msg, 'user': user.username},])
    conn.send(msg, destination='/group/%s' % group.id)

def send_track_update(track, group, user=None):
    conn = _get_stomp()
    msg = json.dumps([{'type': 'queue_count', 'value': group.queued_tracks_count()}, {'type': 'track', 'user': user and user.username, 'track': track.__json__()},])
    conn.send(msg, destination='/group/%s' % group.id)

def send_queue_update(count, group):
    conn = _get_stomp()
    msg = json.dumps([{'type': 'queue_count', 'value': count},])
    conn.send(msg, destination='/group/%s' % group.id)

def send_user_join(user, group):
    conn = _get_stomp()
    msg = json.dumps([{'type': 'user_join', 'value': user.username}])
    conn.send(msg, destination='/group/%i' % group.id)

def send_user_leave(user, group):
    conn = _get_stomp()
    msg = json.dumps([{'type': 'user_leave', 'value': user.username}])
    conn.send(msg, destination='/group/%i' % group.id)
