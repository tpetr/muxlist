def dequeue_track(r, group_id):
    user_id, track_id = None, None

    with r.lock('%s_users_lock' % group_id):
        print "entered lock"
        for current_user_id in r.zrange('%s_users' % group_id, 0, -1):
            print "current_user_id: %s" % current_user_id
            track_count = r.llen('%s_%s_queue' % (group_id, current_user_id))
            print "   track_count: %s" % group_id
        
            if track_count == 0:
                r.zrem('%s_users' % group_id, current_user_id)
                print "      removed from zset"
                continue
        
            if track_id == None:
                track_id = r.lpop('%s_%s_queue' % (group_id, current_user_id))
                print "   track_id: %s" % track_id
                r.decr('%s_queued' % group_id)
                user_id = current_user_id
        print "left lock"

        if user_id != None:
            r.zincrby('%s_users' % group_id, user_id, r.zcard('%s_users' % group_id))

    return user_id, track_id
