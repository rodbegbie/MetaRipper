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
# EXPRESS OR IMPLIED, AND REALNETWORKS HEREBY DISCLAIMS ALL SUCH WARRANTIES,
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

import wx, sys, os
import dircache, wpath
if sys.platform == "win32":
    import win32file

class PyDirCtrl(wx.TreeCtrl):
    '''This class implements a better directory control class than then one that comes with
       wxWidgets. This one is faster and hopefully less buggy.'''

    def __init__(self, parent, id, pos = wx.DefaultPosition, size=wx.DefaultSize, initialDir=""):
        self.id = id
        self.wp = wpath.wpath()
        self.dirCache = dircache.DirCache()
 
        self.darwinRootVolume = u""

        wx.TreeCtrl.__init__(self, parent, id, pos, size, 
                             wx.TR_HAS_BUTTONS | wx.TR_MULTIPLE | wx.TR_HIDE_ROOT)

        wx.EVT_TREE_ITEM_EXPANDING(self, self.id, self.OnExpanding)

        self.root = self.AddRoot(u"-")
        if sys.platform == "win32":
            mask = win32file.GetLogicalDrives()
            for i in xrange(26):
                if mask >> i & 1:
                   drive = unicode(chr(i + ord('A'))) + u":\\"
                   self.addVolume(drive, drive)
        else:
            if sys.platform == "darwin":
                volumes = self.dirCache.getFiles("/Volumes")
                for v in volumes:
                    if not v.startswith("."):
                        vol = u"/Volumes/%s" % v
                        self.addVolume(v, vol)
                        if self.wp.islink(vol):
                            self.darwinRootVolume = unicode(vol)
            else:
                self.addVolume(u"/", u"/")

        if initialDir:
            self.showPath(initialDir)

    def OnExpanding(self, event):
        self.expand(event.GetItem())

    def expand(self, node):
        child, cookie = self.GetFirstChild(node)
        if self.GetItemText(child) == u"":
           self.Delete(child)
           dir = self.GetPyData(node)
           files = self.dirCache.getFiles(dir)
           for file in files:
               newDir = self.wp.join(dir, file)
               if self.wp.isdir(newDir):
                   if file.startswith("."):
                       continue

                   newChild = self.AppendItem(node, file)
                   self.SetPyData(newChild, newDir)

                   if self.hasSubDirs(newDir):
                       self.AppendItem(newChild, u"")


    def addVolume(self, volumeName, volumeData):
        child = self.AppendItem(self.GetRootItem(), volumeName)
        if child:
           self.SetPyData(child, volumeData)
           self.AppendItem(child, "")

    def getSelectedPaths(self):
        items = self.GetSelections()
        paths = []
        for item in items:
            data = self.GetPyData(item)
            if data:
                if self.darwinRootVolume and data.startswith(self.darwinRootVolume):
                    data = data[len(self.darwinRootVolume):]
                    if not data:
                        data = u"/"
                paths.append(data)
       
        return paths

    def makePathLegal(self, path):
        while not self.wp.isdir(path):
            path, drop = self.wp.split(path)
        return path

    def refreshPath(self, path):

        paths = self.getSelectedPaths()
        savedPath = ''
        if paths:
            savedPath = self.makePathLegal(paths[0])
        path = self.makePathLegal(path)

        node = self.findPath(path)
        if node:
            if self.hasSubDirs(path):
                self.Collapse(node)
                self.DeleteChildren(node)
                self.AppendItem(node, u"")
                self.Expand(node)

        self.dirCache.invalidate(path)
        if savedPath:
            self.showPath(savedPath)

    def showPath(self, path):

        if path == u"/":
            return

        #TODO Translate the path (if start sith / and not /Volume) to a /Volume path for OS X

        node = self.findPath(path)
        if node:
            self.EnsureVisible(node)
            self.SelectItem(node)

    def findPath(self, path):
        node, cookie = self.GetFirstChild(self.root)
        return self.recurseFindPath(node, path)

    def recurseFindPath(self, node, path):


        while node:
            nodePath = self.GetPyData(node)
            if not nodePath:
                return None

            if nodePath == path:
                return node

            if self.dirCache.pathCompare(path, nodePath):
                child, cookie = self.GetFirstChild(node)
                if not child:
                    return node

                nodePath = self.GetPyData(child)
                if not nodePath:
                    self.expand(node)
                    child, cookie = self.GetFirstChild(node)
                    if not child:
                        return None

                    nodePath = self.GetPyData(child)

                return self.recurseFindPath(child, path)

            node = self.GetNextSibling(node)

        return None

    def hasSubDirs(self, path):
        files = self.dirCache.getFiles(path)
        for file in files:
            newDir = self.wp.join(path, file)
            if self.wp.isdir(newDir):
                return True

        return False
