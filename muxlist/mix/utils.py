def dequeue_track(r, group_id):
    user_id, track_id = None, None

    # dequeue lock
    with r.lock('%s_users_lock' % group_id):
        while track_id == None:
            # peek at most eligible user
            user_id = r.zrange('%s_users' % group_id, 0, 1)

            # if no users, return nothing
            if len(user_id) == 0:
                return None, None
            else:
                user_id = user_id[0]

            # dequeue a track
            track_id = r.lpop('%s_%s_queue' % (group_id, user_id))

            # remove phantom user, shouldn't happen
            if track_id == None:
                r.zrem('%s_users' % group_id, user_id)
                continue

            # decrement total queued count
            r.decr('%s_queued' % group_id)

            # if user is out of tracks, remove from zset, otherwise update rank
            if r.llen('%s_%s_queue' % group_id, user_id) == 0:
                r.zrem('%s_users' % group_id, user_id)
            else:
                r.zincrby('%_users' % group_id, user_id, r.zcard('%s_users' % group_id))

            return user_id, track_id

    # should never reach this
    return None, None
