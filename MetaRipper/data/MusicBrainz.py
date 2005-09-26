from DiscMetadata import DiscMetadata, TrackMetadata
import logging
import musicbrainz
q = musicbrainz
from tunepimp import tunepimp
tp = tunepimp.tunepimp('MetaRipper', '0.0.1');

import re
DISC_NUM_REGEX = re.compile(r".*\s+\([Dd]isc (\d+)")

def searchMbForDisc(device):
    mb = musicbrainz.mb()
    mb.SetDepth(2)
    mb.SetDevice(device)

    mb.Query(q.MBQ_GetCDTOC)
    cdid = mb.GetResultData(q.MBE_TOCGetCDIndexId)        
    numTracks = mb.GetResultInt(q.MBE_TOCGetLastTrack)
    toc = {}
    toc["first_track"] = 1
    toc["num_tracks"] = numTracks
    toc["length"] = mb.GetResultInt1(q.MBE_TOCGetTrackSectorOffset, 1)
    offsets = []
    for ii in range (2, numTracks + 2):
        trackOffset = mb.GetResultInt1(q.MBE_TOCGetTrackSectorOffset, ii)
        offsets.append(trackOffset)
    toc["offsets"] = offsets
    logging.debug("toc: %s" % str(toc))
    
    logging.info("querying musicbrainz.org to see if this cd is on there...")
    mb.QueryWithArgs(q.MBQ_GetCDInfoFromCDIndexId, [cdid])
    
    numFound = mb.GetResultInt(q.MBE_GetNumAlbums)

    if numFound == 0:
        return (mb, toc, numFound, (mb.GetWebSubmitURL(),))
    else:
        return (mb, toc, numFound, (cdid, numTracks))
    
def searchMbByDiscId(discId):
    mb = musicbrainz.mb()
    mb.SetDepth(4)

    logging.info("querying musicbrainz.org to see if this cd is on there...")
    mb.QueryWithArgs(q.MBQ_GetAlbumById, [discId])
    
    numFound = mb.GetResultInt(q.MBE_GetNumAlbums)

    if numFound == 0:
        print "*** DISC ID NO LONGER VALID ***"
        return None
    else:
        return mb
    
def getDiscNames(mb, numDiscs):
    names = []
    for i in range (1, numDiscs + 1):
        mb.Select1(q.MBS_SelectAlbum, i)
        albumName = mb.GetResultData(q.MBE_AlbumGetAlbumName)
        names.append(albumName)
        mb.Select(q.MBS_Back);
    return names

def createDiscMetadata(mb, disc, cdid, numTracks, toc):
    discMeta = DiscMetadata()            
    mb.Select1(q.MBS_SelectAlbum, disc)            
    album = mb.GetResultData(q.MBE_AlbumGetAlbumName)
    albid = mb.GetIDFromURL(mb.GetResultData(q.MBE_AlbumGetAlbumId))
    artId = mb.GetIDFromURL(mb.GetResultData(q.MBE_AlbumGetAlbumArtistId))
    if artId != q.MBI_VARIOUS_ARTIST_ID:
        artist = mb.GetResultData1(q.MBE_AlbumGetArtistName, 1 + ((disc-1) * numTracks))
        artistSort = mb.GetResultData1(q.MBE_AlbumGetArtistSortName, 1 + ((disc-1) * numTracks))
        va = False
    else:
        artist = "Various Artists"
        artistSort = "Various Artists"
        va = True

    discNumMatches = DISC_NUM_REGEX.findall(album)
    if discNumMatches:
        discNum = int(discNumMatches[0][0])
    else:
        discNum = 1
        
    discMeta.title = album
    discMeta.artist = artist
    discMeta.artistSort = artistSort
    discMeta.mbDiscId = cdid
    discMeta.toc = toc
    discMeta.mbAlbumId = albid
    discMeta.mbArtistId = artId
    discMeta.discNumber = (discNum, discNum)
    
    logging.info("\t%s / %s" % (artist, album))
    for ii in range(1 + ((disc-1) * numTracks), mb.GetResultInt1(q.MBE_AlbumGetNumTracks, disc) + 1):
        name = mb.GetResultData1(q.MBE_AlbumGetTrackName, ii)
        if va:
            artist = mb.GetResultData1(q.MBE_AlbumGetArtistName, ii)
            artistSort = mb.GetResultData1(q.MBE_AlbumGetArtistSortName, ii)
            artId = mb.GetIDFromURL(mb.GetResultData1(q.MBE_AlbumGetArtistId, ii))
        dura = mb.GetResultInt1(q.MBE_AlbumGetTrackDuration, ii)
        trackURI = mb.GetResultData1(q.MBE_AlbumGetTrackId, ii)
        trackId = mb.GetIDFromURL(trackURI)
        track = mb.GetOrdinalFromList(q.MBE_AlbumGetTrackList, trackURI)
        trackMeta = TrackMetadata()
        trackMeta.title = name
        trackMeta.artist = artist
        trackMeta.artistSort = artistSort
        trackMeta.number = track
        trackMeta.length = int(dura)
        trackMeta.mbTrackId = trackId
        trackMeta.mbArtistId = artId
        discMeta.tracks.append(trackMeta)
        dura = "%d:%02d" % divmod(int(dura / 1000), 60)
        
        logging.info("\t%02d - %s - %s (%s)" % (track, artist, name, dura))
                        
    return discMeta

def updateDiscMetadata(mb, discMeta):
    mb.Select1(q.MBS_SelectAlbum, 1)            
    album = mb.GetResultData(q.MBE_AlbumGetAlbumName)
    albid = mb.GetIDFromURL(mb.GetResultData(q.MBE_AlbumGetAlbumId))
    artId = mb.GetIDFromURL(mb.GetResultData(q.MBE_AlbumGetAlbumArtistId))
    if artId != q.MBI_VARIOUS_ARTIST_ID:
        artistSort = mb.GetResultData1(q.MBE_AlbumGetArtistSortName, 1)
        artist = mb.GetResultData1(q.MBE_AlbumGetArtistName, 1)
        va = False
    else:
        artist = "Various Artists"
        artistSort = "Various Artists"
        va = True

    discchanges = False

    if not hasattr(discMeta, "artistSort"):
        discMeta.artistSort = discMeta.artist
    
    pieces = [    
        ("title", album),
        ("artist", artist),
        ("artistSort", artistSort),
        ("mbArtistId", artId)
    ]
    
    for (discpiecename, newpiece) in pieces:
        discpiece = getattr(discMeta, discpiecename)
        if discpiece <> newpiece:
            print "Changing %s to %s" % (discpiece, newpiece)
            setattr(discMeta, discpiecename, newpiece)
            discchanges = True
    
    anytrackchanges = False
    
    for ii in range(1, mb.GetResultInt1(q.MBE_AlbumGetNumTracks, 1) + 1):
        name = mb.GetResultData1(q.MBE_AlbumGetTrackName, ii)
        if va:
            artist = mb.GetResultData1(q.MBE_AlbumGetArtistName, ii)
            artistSort = mb.GetResultData1(q.MBE_AlbumGetArtistSortName, ii)
            artId = mb.GetIDFromURL(mb.GetResultData1(q.MBE_AlbumGetArtistId, ii))
        dura = mb.GetResultInt1(q.MBE_AlbumGetTrackDuration, ii)
        trackURI = mb.GetResultData1(q.MBE_AlbumGetTrackId, ii)
        trackId = mb.GetIDFromURL(trackURI)
        track = mb.GetOrdinalFromList(q.MBE_AlbumGetTrackList, trackURI)

        trackMeta = discMeta.tracks[ii-1]
        if not hasattr(trackMeta, "artistSort"):
            trackMeta.artistSort = trackMeta.artist
        
        pieces = [
            ("title", name),
            ("artist", artist),
            ("artistSort", artistSort),
            ("mbTrackId", trackId),
            ("mbArtistId", artId)
        ]

        thistrackchanges = False
        for (trackpiecename, newpiece) in pieces:
            trackpiece = getattr(trackMeta, trackpiecename)
            if trackpiece <> newpiece:
                print "Changing %s to %s" % (trackpiece, newpiece)
                setattr(trackMeta, trackpiecename, newpiece)
                thistrackchanges = True
        
        if thistrackchanges:
            discMeta.tracks[ii-1] = trackMeta
            anytrackchanges = True

    if (discchanges or anytrackchanges):
        return (discMeta, discchanges)
    else:
        return (None, False)

def writeTags(filename, discMeta, trackNum):
    tp.setMoveFiles(False)
    tp.setRenameFiles(False)
    tp.setWriteID3v1(True)
    tp.setClearTags(True)
    tp.setID3Encoding(tunepimp.eUTF8)
    fileId = tp.addFile(filename)
    tr = tp.getTrack(fileId);
    tr.lock()
    mdata = tr.getServerMetadata()
    mdata.album = discMeta.title
    mdata.albumId = discMeta.mbAlbumId
    mdata.variousArtist = (discMeta.mbArtistId == q.MBI_VARIOUS_ARTIST_ID)
   
    trackMeta = discMeta.tracks[trackNum-1]
    mdata.artist = trackMeta.artist
    if hasattr(trackMeta, "artistSort"):
        mdata.sortName = trackMeta.artistSort
    mdata.artistId = trackMeta.mbArtistId
    mdata.track = trackMeta.title
    mdata.trackId = trackMeta.mbTrackId
    mdata.trackNum = trackMeta.number
    tr.setStatus(tunepimp.eRecognized)
    tr.setServerMetadata(mdata)
    tr.unlock()                   
    tp.releaseTrack(tr);
    tp.writeTags([fileId],)
    
