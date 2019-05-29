def lock_acquire(cur, str, timeout=5):
    get_stmt = (
        "SELECT GET_LOCK('%s',%d)"%(str,timeout,)
    )
    cur.execute(get_stmt)


def lock_release(cur, str):
    release_stmt = (
        "SELECT RELEASE_LOCK('%s')"%(str,)
    )
    cur.execute(release_stmt)
