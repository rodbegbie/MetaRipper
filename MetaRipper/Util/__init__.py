def walk(top, topdown=True, onerror=None, followlinks=False):
    import os
    from os.path import join, isdir, islink

    # We may not have read permission for top, in which case we can't
    # get a list of the files the directory contains.  os.path.walk
    # always suppressed the exception then, rather than blow up for a
    # minor reason when (say) a thousand readable directories are still
    # left to visit.  That logic is copied here.
    names = os.listdir(top)

    dirs, nondirs = [], []
    for name in names:
        if isdir(join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)
    
    dirs.sort()
    nondirs.sort()

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        path = join(top, name)
        if followlinks or  not islink(path):
            for x in walk(path, topdown, onerror, followlinks):
                yield x
    if not topdown:
        yield top, dirs, nondirs

