def dequeue_track(r, group_id):
    user_id, track_id = None, None
    while track_id == None:
        user_id = r.spop('%s_users' % group_id)
        if user_id == None: break
        track_id = r.lpop('%s_%s_queue' % (group_id, user_id))
        if track_id != None:
            r.sadd('%s_users' % group_id, user_id)
            r.decr('%s_queued' % group_id)

    return user_id, track_id
