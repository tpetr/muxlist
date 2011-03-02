def dequeue_track(r, group_id):
    user_id, track_id = None, None

    enqueued_users = '%s_users' % group_id
    enqueued_users_next = '%s_users_next' % group_id
    total_enqueued_count = '%s_queued' % group_id

    # dequeue lock
    with r.lock('%s_users_lock' % group_id):
        while track_id == None:
            # peek at most eligible user
            user_id = r.zrange(enqueued_users, 0, 1)

            # if no users, return nothing
            if len(user_id) == 0:
                return None, None
            else:
                user_id = user_id[0]

            # dequeue a track
            track_id = r.lpop('%s_%s_queue' % (group_id, user_id))

            # remove phantom user, shouldn't happen
            if track_id == None:
                r.zrem(enqueued_users, user_id)
                continue

            # decrement total queued count
            r.decr(total_enqueued_count)

            # if user is out of tracks, remove from zset, otherwise update rank
            if r.llen('%s_%s_queue' % (group_id, user_id)) == 0:
                r.zrem(enqueued_users, user_id)
            else:
                smallest = r.zrange(enqueued_users_next, 0, 1)
                if len(smallest) > 0: r.zadd(enqueued_users_next, smallest[0], 1)
                r.zadd(enqueued_users_next, user_id, -1 * r.zcard(enqueued_users))
                r.zinterstore(enqueued_users, [enqueued_users, enqueued_users_next])

            return user_id, track_id

    # should never reach this
    return None, None
