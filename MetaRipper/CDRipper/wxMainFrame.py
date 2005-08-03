# -*- coding: ANSI_X3.4-1968 -*-
# generated by wxGlade 0.3.5.1 on Sun May 29 16:39:49 2005

CD_DEVICE="/dev/cdroms/cdrom0"

import wx
# begin wxGlade: dependencies
import wx.grid
# end wxGlade

from data.DiscMetadata import DiscMetadata, TrackMetadata, makeTrackFilename
from data.MusicBrainz import searchMb, createDiscMetadata, writeTags
from Util.RipTrack import ripTrack
import logging, thread, webbrowser
from time import sleep


class wxMainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: wxMainFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.panel_buttons = wx.Panel(self.panel_1, -1)
        self.panel_progress = wx.Panel(self.panel_1, -1)
        self.panel_tracks = wx.Panel(self.panel_1, -1)
        self.panel_info = wx.Panel(self.panel_1, -1)
        self.sizer_3_staticbox = wx.StaticBox(self.panel_tracks, -1, "Tracks")
        self.panel_2 = wx.Panel(self.panel_info, -1)
        self.label_1 = wx.StaticText(self.panel_info, -1, "CD Title:")
        self.label_cdTitle = wx.StaticText(self.panel_info, -1, "label_2")
        self.label_3 = wx.StaticText(self.panel_info, -1, "CD Artist")
        self.label_cdArtist = wx.StaticText(self.panel_info, -1, "label_4")
        self.label_5 = wx.StaticText(self.panel_info, -1, "MB Disc ID:")
        self.button_mbdisc = wx.Button(self.panel_info, -1, "mbDiscId", style=wx.BU_EXACTFIT)
        self.label_6 = wx.StaticText(self.panel_info, -1, "Release Date:")
        self.label_releaseDate = wx.StaticText(self.panel_info, -1, "label_7")
        self.label_8 = wx.StaticText(self.panel_info, -1, "Barcode:")
        self.text_ctrl_barcode = wx.TextCtrl(self.panel_info, -1, "", style=wx.TE_PROCESS_ENTER)
        self.label_9 = wx.StaticText(self.panel_info, -1, "Disc No")
        self.text_ctrl_discNum = wx.TextCtrl(self.panel_2, -1, "")
        self.label_10 = wx.StaticText(self.panel_2, -1, "of")
        self.text_ctrl_discOf = wx.TextCtrl(self.panel_2, -1, "")
        self.label_11 = wx.StaticText(self.panel_info, -1, "Country:")
        self.choice_country = wx.Choice(self.panel_info, -1, choices=["UK", "US", "Other"])
        self.grid_tracks = wx.grid.Grid(self.panel_tracks, -1, size=(1, 1))
        self.label_2 = wx.StaticText(self.panel_progress, -1, "Track Progress:")
        self.gauge_track = wx.Gauge(self.panel_progress, -1, 100, style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
        self.label_4 = wx.StaticText(self.panel_progress, -1, "Disc Progress:")
        self.gauge_disc = wx.Gauge(self.panel_progress, -1, 100, style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
        self.button_refresh = wx.Button(self.panel_buttons, -1, "&Refresh")
        self.button_rip = wx.Button(self.panel_buttons, -1, "&Rip")
        self.button_eject = wx.Button(self.panel_buttons, -1, "&Eject")
        self.button_exit = wx.Button(self.panel_buttons, -1, "E&xit")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: wxMainFrame.__set_properties
        self.SetTitle("MetaRipper - CDRipper")
        self.button_mbdisc.SetForegroundColour(wx.Colour(0, 0, 255))
        self.button_mbdisc.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 1, ""))
        self.text_ctrl_barcode.SetSize((110, 25))
        self.text_ctrl_discNum.SetSize((40, 25))
        self.text_ctrl_discOf.SetSize((40, 25))
        self.choice_country.SetSelection(0)
        self.grid_tracks.CreateGrid(10, 3)
        self.grid_tracks.SetRowLabelSize(25)
        self.grid_tracks.SetColLabelSize(20)
        self.grid_tracks.EnableEditing(0)
        self.grid_tracks.EnableDragRowSize(0)
        self.grid_tracks.EnableDragGridSize(0)
        self.grid_tracks.SetSelectionMode(wx.grid.Grid.wxGridSelectRows)
        self.grid_tracks.SetColLabelValue(0, "Name")
        self.grid_tracks.SetColSize(0, 200)
        self.grid_tracks.SetColLabelValue(1, "Artist")
        self.grid_tracks.SetColSize(1, 200)
        self.grid_tracks.SetColLabelValue(2, "Length")
        self.grid_tracks.SetColSize(2, 60)
        self.grid_tracks.SetSize((500, 300))
        self.panel_tracks.SetSize((348, 318))
        self.button_refresh.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: wxMainFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(3, 1, 0, 0)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_2 = wx.FlexGridSizer(2, 2, 0, 0)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.HORIZONTAL)
        grid_sizer_3 = wx.FlexGridSizer(7, 2, 0, 0)
        grid_sizer_4 = wx.FlexGridSizer(1, 3, 0, 5)
        grid_sizer_3.Add(self.label_1, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.label_cdTitle, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.label_3, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.label_cdArtist, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.label_5, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.button_mbdisc, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.label_6, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.label_releaseDate, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.label_8, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.text_ctrl_barcode, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.label_9, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_4.Add(self.text_ctrl_discNum, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_4.Add(self.label_10, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_4.Add(self.text_ctrl_discOf, 0, wx.FIXED_MINSIZE, 0)
        self.panel_2.SetAutoLayout(True)
        self.panel_2.SetSizer(grid_sizer_4)
        grid_sizer_4.Fit(self.panel_2)
        grid_sizer_4.SetSizeHints(self.panel_2)
        grid_sizer_3.Add(self.panel_2, 1, wx.EXPAND, 0)
        grid_sizer_3.Add(self.label_11, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_3.Add(self.choice_country, 0, wx.FIXED_MINSIZE, 0)
        self.panel_info.SetAutoLayout(True)
        self.panel_info.SetSizer(grid_sizer_3)
        grid_sizer_3.Fit(self.panel_info)
        grid_sizer_3.SetSizeHints(self.panel_info)
        grid_sizer_3.AddGrowableCol(1)
        grid_sizer_1.Add(self.panel_info, 1, wx.EXPAND, 0)
        sizer_3.Add(self.grid_tracks, 1, wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 5)
        self.panel_tracks.SetAutoLayout(True)
        self.panel_tracks.SetSizer(sizer_3)
        grid_sizer_1.Add(self.panel_tracks, 1, wx.EXPAND, 0)
        grid_sizer_2.Add(self.label_2, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_2.Add(self.gauge_track, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        grid_sizer_2.Add(self.label_4, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_2.Add(self.gauge_disc, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        self.panel_progress.SetAutoLayout(True)
        self.panel_progress.SetSizer(grid_sizer_2)
        grid_sizer_2.Fit(self.panel_progress)
        grid_sizer_2.SetSizeHints(self.panel_progress)
        grid_sizer_2.AddGrowableCol(1)
        grid_sizer_1.Add(self.panel_progress, 1, wx.EXPAND, 0)
        sizer_2.Add(self.button_refresh, 0, wx.ALL|wx.FIXED_MINSIZE, 5)
        sizer_2.Add(self.button_rip, 0, wx.ALL|wx.FIXED_MINSIZE, 5)
        sizer_2.Add(self.button_eject, 0, wx.ALL|wx.FIXED_MINSIZE, 5)
        sizer_2.Add(self.button_exit, 0, wx.ALL|wx.FIXED_MINSIZE, 5)
        self.panel_buttons.SetAutoLayout(True)
        self.panel_buttons.SetSizer(sizer_2)
        sizer_2.Fit(self.panel_buttons)
        sizer_2.SetSizeHints(self.panel_buttons)
        grid_sizer_1.Add(self.panel_buttons, 1, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, 0)
        self.panel_1.SetAutoLayout(True)
        self.panel_1.SetSizer(grid_sizer_1)
        grid_sizer_1.Fit(self.panel_1)
        grid_sizer_1.SetSizeHints(self.panel_1)
        grid_sizer_1.AddGrowableRow(1)
        grid_sizer_1.AddGrowableCol(0)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()
        # end wxGlade
        wx.EVT_BUTTON(self, self.button_mbdisc.GetId(), self.onMBDisc)
        wx.EVT_BUTTON(self, self.button_eject.GetId(), self.onEject)
        wx.EVT_BUTTON(self, self.button_refresh.GetId(), self.onRefresh)
        wx.EVT_BUTTON(self, self.button_rip.GetId(), self.onRip)
        wx.EVT_BUTTON(self, self.button_exit.GetId(), self.onExit)
        wx.EVT_TEXT_ENTER(self, self.text_ctrl_barcode.GetId(), self.checkBarcode)
 
    def _ripProgress(self, trackNo, secs):
        trackLength = float(self.discMeta.tracks[trackNo-1].length) / 1000
        trackPercent = int((secs / trackLength) * 100)
        
        numTracks = float(len(self.discMeta.tracks))
        discPercent = ((trackNo-1) / numTracks) * 100
        discPercent = int(discPercent + (trackPercent/numTracks))
        
        wx.CallAfter(self.gauge_track.SetValue, trackPercent)
        wx.CallAfter(self.gauge_disc.SetValue, discPercent)

    def _ripComplete(self, trackNo):
        self._ripping = False
        
    def onMBDisc(self, event):
        url = "http://musicbrainz.org/album/%s.html" % self.discMeta.mbAlbumId
        webbrowser.open_new(url)
    
    def onRip(self, event):
        thread.start_new_thread(self._ripThread,())
        
    def _ripThread(self):
        for trackNum in range(1, len(self.discMeta.tracks) + 1):
            filename = makeTrackFilename(self.discMeta, trackNum)
            logging.info("Ripping to %s" % filename)
            ripTrack(CD_DEVICE, trackNum, filename, self._ripProgress, self._ripComplete)
            writeTags(filename, self.discMeta, trackNum)
        self._eject()
        
    def onEject(self, event):
        self._eject()
        
    def onExit(self, event):
        self.Close(True)

    def checkBarcode(self, event):
        import Util.Barcode as Barcode
        bc = self.text_ctrl_barcode.GetValue()
        if not Barcode.validateBarcode(bc):
            wx.MessageDialog(self, "That barcode is wrong!", "Barcode Error", wx.OK | wx.ICON_HAND).ShowModal()
        else:
            if bc.find("0") == 0 or len(bc) == 12:
                self.choice_country.SetSelection(1)
            else:
                self.choice_country.SetSelection(0)

    def onRefresh(self, event):
        discMeta = None
        self._ripping = False
        (mb, toc, numFound, info) = searchMb(CD_DEVICE)
        if numFound == 1:
            numTracks = info[0]
            cdid = info[1]
            discMeta = createDiscMetadata(mb, 1, cdid, numTracks, toc)
        elif numFound == 0:    
            logging.info("CD Not Found")
            button = wx.MessageDialog(self,
                                      "Add CD to MusicBrainz?", "CD Not Found", 
                                      wx.YES_NO | wx.YES_DEFAULT |
                                      wx.ICON_QUESTION).ShowModal()

            if button == wx.ID_YES:
                url = info[0]
                if url:
                    print "opening web browser to '%s'..." % url
                    webbrowser.open_new(url)
            else:
                self._eject()
        else:
            # Display Choice
            pass
            
        if discMeta:
            self.updateDisplay(discMeta)
    
    def updateDisplay(self, discMeta):
        self.discMeta = discMeta
        self._setInfoLabel(self.label_cdTitle, discMeta.title)
        self._setInfoLabel(self.label_cdArtist, discMeta.artist)
        self._setInfoLabel(self.button_mbdisc, discMeta.mbAlbumId)
        self.text_ctrl_discNum.SetValue(str(discMeta.discNumber[0]))
        self.text_ctrl_discOf.SetValue(str(discMeta.discNumber[1]))
        self.grid_tracks.DeleteRows(0, self.grid_tracks.GetNumberRows())
        i = 0
        for trackMeta in discMeta.tracks:
            self.grid_tracks.AppendRows()
            self.grid_tracks.SetCellValue(i, 0, trackMeta.title)
            self.grid_tracks.SetCellValue(i, 1, trackMeta.artist)
            self.grid_tracks.SetCellValue(i, 2, "%d:%02d" % divmod(trackMeta.length / 1000, 60))
            i += 1
            
        self.text_ctrl_barcode.SetFocus()
        

    def _eject(self):
        import os
        os.system("eject")

    def _setInfoLabel(self, label, text):
        text = text.replace("&", "&&")  # Display ampersands in labels
        if text != label.GetLabel():
            label.SetLabel(text)
            self.panel_info.GetSizer().SetItemMinSize(label, label.GetBestSize())
        
# end of class wxMainFrame


