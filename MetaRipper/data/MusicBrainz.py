from DiscMetadata import DiscMetadata, TrackMetadata
import logging
import musicbrainz
q = musicbrainz

import re
discNumRegex = re.compile(r"(.*)\s+\([Dd]isc (\d+)\)")

def searchMb():
    mb = musicbrainz.mb()
    mb.SetDepth(2)

    mb.Query(q.MBQ_GetCDTOC)
    cdid = mb.GetResultData(q.MBE_TOCGetCDIndexId)        
    numTracks = mb.GetResultInt(q.MBE_TOCGetLastTrack)
    toc = [1, numTracks]
    for ii in range (1, numTracks + 1):
        trackOffset = mb.GetResultInt1(q.MBE_TOCGetTrackSectorOffset, ii)
        toc.append(trackOffset)
    logging.debug("toc: %s" % str(toc))
    
    logging.info("querying musicbrainz.org to see if this cd is on there...")
    mb.QueryWithArgs(q.MBQ_GetCDInfoFromCDIndexId, [cdid])
    
    numFound = mb.GetResultInt(q.MBE_GetNumAlbums)
    if numFound == 1:
        return (mb, toc, numFound, (cdid, numTracks))
    elif numFound == 0:
        return (mb, toc, numFound, mb.GetWebSubmitURL())
    #TODO: If more than one found, return list.
    

def createDiscMetadata(mb, disc, cdid, numTracks, toc):
    discMeta = DiscMetadata()            
    print "Yes and here's the info:"
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

    discNumMatches = discNumRegex.findall(album)
    if discNumMatches:
        title = discNumMatches[0]
        discNum = int(discNumMatches[1])
    else:
        discNum = 1
        
    discMeta.title = album
    discMeta.artist = artist
    discMeta.mbDiscId = cdid
    discMeta.toc = toc
    discMeta.mbAlbumId = albid
    discMeta.discNumber = (discNum, discNum)
    
    print "\t%s / %s" % (artist, album)
    for ii in range(1, mb.GetResultInt(q.MBE_AlbumGetNumTracks) + 1):
        name = mb.GetResultData1(q.MBE_AlbumGetTrackName, ii)
        if va:
            artist = mb.GetResultData1(q.MBE_AlbumGetArtistName, ii)
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
        discMeta.tracks.append(trackMeta)
        dura = "%d:%02d" % divmod(int(dura / 1000), 60)
        
        print "\t%02d - %s - %s (%s)" % (track, artist, name, dura)
                        
    return discMeta