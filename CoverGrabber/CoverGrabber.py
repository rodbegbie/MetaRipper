#!/usr/bin/env python
# -*- coding: ANSI_X3.4-1968 -*-
# generated by wxGlade 0.4 on Wed Nov  2 21:11:51 2005

import wx
from CoverGrabberFrame import CoverGrabberFrame

class CoverGrabber(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frame_grabber = CoverGrabberFrame(None, -1, "")
        self.SetTopWindow(frame_grabber)
        frame_grabber.Show()
        return 1

# end of class CoverGrabber

if __name__ == "__main__":
    CoverGrabber = CoverGrabber(0)
    CoverGrabber.MainLoop()