import wx, os, sys, copy
import pydirctrl

class GrabberDirCtrl(pydirctrl.PyDirCtrl):
    
    selections = []
    menuRefreshId = wx.NewId()

    def __init__(self, parent, id):
        pydirctrl.PyDirCtrl.__init__(self, parent, id, initialDir="/home/rod/flac")
        self.frame = parent
        self.id = id

#        wx.EVT_TREE_BEGIN_DRAG(self, self.id, self.OnBeginDrag)
        wx.EVT_TREE_SEL_CHANGED(self, self.id, self.OnSelChanged)
#        wx.EVT_RIGHT_DOWN(self, self.OnRightDown)
#        wx.EVT_MENU(self, self.menuRefreshId, self.OnRefresh)

#        wx.PostEvent(self.frame, events.ShowDirectoryEvent(config.persistDirControlPath))
        wx.WakeUpIdle()

    def OnSelChanged(self, event):

        paths = self.getSelectedPaths()
        if len(paths) == 0:
            return

        self.frame.loadMetadata(paths[0])

#    def OnBeginDrag(self, event): 
#
#        selections = self.getSelectedPaths()
#        if len(selections) > 1:
#            dropText = u"dirs:"
#            for path in selections:
#               dropText = dropText + path + u"\n"
#            dropText = dropText[:len(dropText)-1]
#
#            tdo = wx.PyTextDataObject(dropText)
#        else:
#            selPath = selections[0]
#            if wpath.wpath(self.config).isdir(selPath):
#                tdo = wx.PyTextDataObject(u"dir:" + selPath)
#            else:
#                event.Veto()
#                return
#
#        event.Allow()
#        tds = albumpanel.TaggerDropSource(self, self.albumPanel) 
#        tds.SetData(tdo) 
#        tds.DoDragDrop(True) 
#        event.Skip()
#
#    def OnRightDown(self, event):
#        item, flags = self.HitTest(wx.Point(event.m_x, event.m_y))
#        if item:
#            self.SelectItem(item)
#            popupMenu = wx.Menu()
#            popupMenu.Append(self.menuRefreshId, u"Refresh")
#            self.PopupMenuXY(popupMenu, event.m_x, event.m_y)
    def OnRefresh(self, event):
        sel = self.GetSelections()
        assert len(sel) == 1

        path = self.GetPyData(sel[0])
        if path:
            self.refreshPath(path) 
