#!/usr/bin/env python
# ***** BEGIN LICENSE BLOCK *****
# Version: RCSL 1.0/RPSL 1.0/GPL 2.0
#
# Portions Copyright (c) 1995-2002 RealNetworks, Inc. All Rights Reserved.
# Portions Copyright (c) 2004 Robert Kaye. All Rights Reserved.
#
# The contents of this file, and the files included with this file, are
# subject to the current version of the RealNetworks Public Source License
# Version 1.0 (the "RPSL") available at
# http://www.helixcommunity.org/content/rpsl unless you have licensed
# the file under the RealNetworks Community Source License Version 1.0
# (the "RCSL") available at http://www.helixcommunity.org/content/rcsl,
# in which case the RCSL will apply. You may also obtain the license terms
# directly from RealNetworks.  You may not use this file except in
# compliance with the RPSL or, if you have a valid RCSL with RealNetworks
# applicable to this file, the RCSL.  Please see the applicable RPSL or
# RCSL for the rights, obligations and limitations governing use of the
# contents of the file.
#
# This file is part of the Helix DNA Technology. RealNetworks is the
# developer of the Original Code and owns the copyrights in the portions
# it created.
#
# This file, and the files included with this file, is distributed and made
# available on an 'AS IS' basis, WITHOUT WARRANTY OF ANY KIND, EITHER
# EXPRESS OR IMPLIED,G AND REALNETWORKS HEREBY DISCLAIMS ALL SUCH WARRANTIES,
# INCLUDING WITHOUT LIMITATION, ANY WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE, QUIET ENJOYMENT OR NON-INFRINGEMENT.
#
# Technology Compatibility Kit Test Suite(s) Location:
#    http://www.helixcommunity.org/content/tck
#
# --------------------------------------------------------------------
#
# picard is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# picard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with picard; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Contributor(s):
#   Robert Kaye
#
#
# ***** END LICENSE BLOCK *****
import sys, os, locale, copy, wx, locale
import wpath

class DirCache(object):

    dirSep = u"/"
    if sys.platform == 'win32':
        dirSep = u"\\"
  
    def __init__(self):
        self.wp = wpath.wpath()
        self.dirCache = {}

    def getFiles(self, path):

        path = self.addTrailingSep(path)
        try:
            cacheTime, files = self.dirCache[path]
            del self.dirCache[path]
        except KeyError:
            cacheTime, files = -1, []

        try:
            mTime = self.wp.stat(path).st_mtime
        except os.error:
            return []

        if mTime != cacheTime:
            try:
                files = self.wp.listdir(path)
            except os.error:
                return []

            for i in xrange(len(files)):
                if files[i].__class__.__name__ == "str":
                    files[i] = unicode(files[i], 'utf-8', 'replace')

            if sys.platform == 'win32':
                # case insensitive sorting on windows. this is much more natural for every windows user
                files.sort(lambda x, y: cmp(x.lower(), y.lower()))
            else:
                # case sensitive sorting on all other systems
                files.sort()

        self.dirCache[path] = mTime, files
        return files

    def invalidate(self, path):

        for dir in self.dirCache.keys():
            if self.pathCompare(dir, path):
                try:
                    del self.dirCache[dir]
                except:
                    pass

    def pathCompare(self, full, partial):

        if full == partial or partial == self.dirSep:
            return True

        full = self.addTrailingSep(full)
        partial = self.addTrailingSep(partial)

        return full.startswith(partial)

    def addTrailingSep(self, path):

        if not path.endswith(self.dirSep) and path != self.dirSep:
            path = path + self.dirSep

        return path
