from DiscMetadata import DiscMetadata, TrackMetadata
import logging
import musicbrainz
q = musicbrainz
from tunepimp import tunepimp
tp = tunepimp.tunepimp('MetaRipper', '0.0.1');

import re
DISC_NUM_REGEX = re.compile(r"(.*)\s+\([Dd]isc (\d+)\)")

def searchMb(device):
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
    if numFound == 1:
        return (mb, toc, numFound, (cdid, numTracks))
    elif numFound == 0:
        return (mb, toc, numFound, (mb.GetWebSubmitURL(),))
    #TODO: If more than one found, return list.
    

def createDiscMetadata(mb, disc, cdid, numTracks, toc):
    discMeta = DiscMetadata()            
    logging.info("Yes and here's the info:")
    mb.Select1(q.MBS_SelectAlbum, 1)            
    album = mb.GetResultData(q.MBE_AlbumGetAlbumName)
    albid = mb.GetIDFromURL(mb.GetResultData1(q.MBE_AlbumGetAlbumId, disc))
    artId = mb.GetIDFromURL(mb.GetResultData(q.MBE_AlbumGetAlbumArtistId))
    if artId != q.MBI_VARIOUS_ARTIST_ID:
        artist = mb.GetResultData1(q.MBE_AlbumGetArtistName, 1)
        va = False
    else:
        artist = "Various Artists"
        va = True

    discNumMatches = DISC_NUM_REGEX.findall(album)
    if discNumMatches:
        album = discNumMatches[0][0]
        discNum = int(discNumMatches[0][1])
    else:
        discNum = 1
        
    discMeta.title = album
    discMeta.artist = artist
    discMeta.mbDiscId = cdid
    discMeta.toc = toc
    discMeta.mbAlbumId = albid
    discMeta.mbArtistId = artId
    discMeta.discNumber = (discNum, discNum)
    
    logging.info("\t%s / %s" % (artist, album))
    for ii in range(1, mb.GetResultInt(q.MBE_AlbumGetNumTracks) + 1):
        name = mb.GetResultData1(q.MBE_AlbumGetTrackName, ii)
        if va:
            artist = mb.GetResultData1(q.MBE_AlbumGetArtistName, ii)
            artId = mb.GetIDFromURL(mb.GetResultData1(q.MBE_AlbumGetArtistId, ii))
        dura = mb.GetResultInt1(q.MBE_AlbumGetTrackDuration, ii)
        trackURI = mb.GetResultData1(q.MBE_AlbumGetTrackId, ii)
        trackId = mb.GetIDFromURL(trackURI)
        track = mb.GetOrdinalFromList(q.MBE_AlbumGetTrackList, trackURI)
        trackMeta = TrackMetadata()
        trackMeta.title = name
        trackMeta.artist = artist
        trackMeta.number = track
        trackMeta.length = int(dura)
        trackMeta.mbTrackId = trackId
        trackMeta.mbArtistId = artId
        discMeta.tracks.append(trackMeta)
        dura = "%d:%02d" % divmod(int(dura / 1000), 60)
        
        logging.info("\t%02d - %s - %s (%s)" % (track, artist, name, dura))
                        
    return discMeta

def writeTags(filename, discMeta, trackNum):
    fileId = tp.addFile(filename)
    
    tp.setMoveFiles(False)
    tp.setRenameFiles(False)
    tr = tp.getTrack(fileId);
    tr.lock()
    mdata = tr.getServerMetadata()
    mdata.album = discMeta.title
    mdata.albumId = discMeta.mbAlbumId
    mdata.variousArtist = (discMeta.mbArtistId == q.MBI_VARIOUS_ARTIST_ID)

    trackMeta = discMeta.tracks[trackNum-1]
    mdata.artist = trackMeta.artist
    mdata.artistId = trackMeta.mbArtistId
    mdata.track = trackMeta.title
    mdata.trackId = trackMeta.mbTrackId
    mdata.trackNum = trackMeta.number
    tr.setStatus(tunepimp.eRecognized)
    tr.setServerMetadata(mdata)
    tr.unlock()                   
    tp.releaseTrack(tr);
    tp.writeTags([fileId],)
    