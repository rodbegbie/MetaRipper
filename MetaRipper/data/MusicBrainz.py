from DiscMetadata import DiscMetadata, TrackMetadata
import logging
import musicbrainz
q = musicbrainz
from tunepimp import tunepimp
tp = tunepimp.tunepimp('MetaRipper', '0.0.1');

import re
DISC_NUM_REGEX = re.compile(r".*\s+\([Dd]isc (\d+)")

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

    if numFound == 0:
        return (mb, toc, numFound, (mb.GetWebSubmitURL(),))
    else:
        return (mb, toc, numFound, (cdid, numTracks))
    
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
    logging.info("Yes and here's the info:")
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
    