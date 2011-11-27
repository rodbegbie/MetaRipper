from DiscMetadata import DiscMetadata, TrackMetadata
import logging
from musicbrainz2 import disc, model
import musicbrainz2.webservice as ws
from musicbrainz2.utils import extractUuid
from tunepimp import tunepimp
tp = tunepimp.tunepimp('MetaRipper', '0.0.1');

import re
DISC_NUM_REGEX = re.compile(r".*\s+\([Dd]isc (\d+)")

def searchMbForDisc(device):
    d = disc.readDisc(device)
    cdid = d.id
    numTracks = d.getLastTrackNum()
    toc = {}
    toc["first_track"] = 1
    toc["num_tracks"] = numTracks
    toc["length"] = d.sectors
    toc["offsets"] = [x for (x,y) in d.getTracks()]
    logging.debug("toc: %s" % str(toc))

    logging.info("querying musicbrainz.org to see if this cd is on there...")
    q = ws.Query()
    rf = ws.ReleaseFilter(discId=cdid)
    releases = [result.getRelease() for result in q.getReleases(rf)]

    numFound = len(releases)

    if numFound == 0:
        return (toc, numFound, (disc.getSubmissionUrl(d),), None)
    else:
        return (toc, numFound, (cdid, numTracks), releases)

def searchMbByDiscId(discId):
    q = ws.Query()
    rf = ws.ReleaseFilter(discId=cdid)
    releases = [result.getRelease() for result in q.getReleases(rf)]

    numFound = len(releases)

    if numFound == 0:
        print "*** DISC ID NO LONGER VALID ***"
        return None
    else:
        return releases

def getDiscNames(releases):
    names = [release.title for release in releases]
    return names

def createDiscMetadata(release, cdid, numTracks, toc):
    discMeta = DiscMetadata()

    album = release.title
    albid = extractUuid(release.id, 'release')
    artId = extractUuid(release.artist.id, 'artist')

    artist = release.artist.name
    artistSort = release.artist.sortName
    discMeta.variousArtists = (release.artist.id == model.VARIOUS_ARTISTS_ID)

    releaseYear = None

    for event in release.releaseEvents:
        releaseDate = event.date
        releaseCountry = event.country

        thisReleaseYear = int(releaseDate[0:4])
        if releaseYear == None or thisReleaseYear < releaseYear:
            releaseYear = thisReleaseYear

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
    discMeta.releaseDate = releaseYear

    lastArtist = None
    logging.info("\t%s / %s" % (artist, album))
    trackNum = 0
    for track in release.tracks:
        trackNum += 1
        name = track.title
        artist = track.artist.name if track.artist else artist
        artistSort = track.artist.sortName if track.artist else artistSort
        artId = extractUuid(track.artist.id, 'artist') if track.artist else artId
        dura = track.duration if track.duration else 0
        trackURI = track.id
        trackId = extractUuid(trackURI, 'track')
        trackMeta = TrackMetadata()
        trackMeta.title = name
        trackMeta.artist = artist
        if lastArtist and artist <> lastArtist:
            discMeta.variousArtists = True
        lastArtist = artist
        trackMeta.artistSort = artistSort
        trackMeta.number = trackNum
        trackMeta.length = dura
        trackMeta.mbTrackId = trackId
        trackMeta.mbArtistId = artId
        discMeta.tracks.append(trackMeta)
        dura = "%d:%02d" % divmod(int(dura / 1000), 60)

        logging.info("\t%02d - %s - %s (%s)" % (trackNum, artist, name, dura))

    return discMeta

def updateDiscMetadata(discMeta):
    mb.Select1(q.MBS_SelectAlbum, 1)
    album = mb.GetResultData(q.MBE_AlbumGetAlbumName)
    albid = mb.GetIDFromURL(mb.GetResultData(q.MBE_AlbumGetAlbumId))
    artId = mb.GetIDFromURL(mb.GetResultData(q.MBE_AlbumGetAlbumArtistId))
    releaseYear = None

    try:
        numReleases = mb.GetResultInt(q.MBE_AlbumGetNumReleaseDates)
        for i in xrange(1, numReleases + 1):
            mb.Select1(q.MBS_SelectReleaseDate, i)
            releaseDate = mb.GetResultData(q.MBE_ReleaseGetDate)
            releaseCountry = mb.GetResultData(q.MBE_ReleaseGetCountry)

            thisReleaseYear = int(releaseDate[0:4])
            if releaseYear == None or thisReleaseYear < releaseYear:
                releaseYear = thisReleaseYear

            mb.Select(musicbrainz.MBS_Back)

    except musicbrainz.MusicBrainzError:
        print "error getting date"

    if not hasattr(discMeta, "variousArtists"):
        discMeta.variousArtists = False

    if artId != q.MBI_VARIOUS_ARTIST_ID:
        artistSort = mb.GetResultData(q.MBE_TrackGetArtistSortName)
        artist = mb.GetResultData(q.MBE_TrackGetArtistName)
    else:
        artist = "Various Artists"
        artistSort = "Various Artists"
        discMeta.variousArtists = True

    discchanges = False
    dirchange = False

    if not hasattr(discMeta, "artistSort"):
        discMeta.artistSort = discMeta.artist

    pieces = [
        ("title", album, True),
        ("artist", artist, False),
        ("artistSort", artistSort, True),
        ("mbArtistId", artId, False),
        ("releaseDate", releaseYear, False)
    ]

    for (discpiecename, newpiece, needsrenaming) in pieces:
        discpiece = getattr(discMeta, discpiecename)
        if discpiece <> newpiece:
            print "Changing %s to %s" % (discpiece, newpiece)
            setattr(discMeta, discpiecename, newpiece)
            discchanges = True
            dirchange = dirchange or needsrenaming

    anytrackchanges = False
    lastArtist = None
    for ii in range(1, mb.GetResultInt1(q.MBE_AlbumGetNumTracks, 1) + 1):
        name = mb.GetResultData1(q.MBE_AlbumGetTrackName, ii)
        artist = mb.GetResultData1(q.MBE_AlbumGetArtistName, ii)
        artistSort = mb.GetResultData1(q.MBE_AlbumGetArtistSortName, ii)
        artId = mb.GetIDFromURL(mb.GetResultData1(q.MBE_AlbumGetArtistId, ii))
        dura = mb.GetResultInt1(q.MBE_AlbumGetTrackDuration, ii)
        trackURI = mb.GetResultData1(q.MBE_AlbumGetTrackId, ii)
        trackId = mb.GetIDFromURL(trackURI)
        track = mb.GetOrdinalFromList(q.MBE_AlbumGetTrackList, trackURI)

        if lastArtist and artist <> lastArtist:
            discMeta.variousArtists = True
        lastArtist = artist

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
                print "Changing %s - %s to %s" % (trackpiecename, trackpiece, newpiece)
                setattr(trackMeta, trackpiecename, newpiece)
                thistrackchanges = True

        if thistrackchanges:
            discMeta.tracks[ii-1] = trackMeta
            anytrackchanges = True

    if (discchanges or anytrackchanges):
        return (discMeta, dirchange)
    else:
        return (None, False)

def writeTags(filename, discMeta, trackNum):
    print "FILENAME", filename
    tp.setMoveFiles(False)
    tp.setRenameFiles(False)
    tp.setWriteID3v1(True)
    tp.setClearTags(True)
    tp.setID3Encoding(tunepimp.eUTF8)
    fileId = tp.addFile(filename)
    tr = tp.getTrack(fileId);
    tr.lock()
    mdata = tr.getServerMetadata()
    mdata.album = discMeta.title.encode("utf-8")
    mdata.albumId = discMeta.mbAlbumId
    # mdata.albumArtistId = discMeta.mbArtistId
    mdata.variousArtist = discMeta.variousArtists
    if discMeta.releaseDate:
        mdata.releaseYear = discMeta.releaseDate

    trackMeta = discMeta.tracks[trackNum-1]
    mdata.artist = trackMeta.artist.encode("utf-8")
    if hasattr(trackMeta, "artistSort"):
        mdata.sortName = trackMeta.artistSort.encode("utf-8")
    mdata.artistId = trackMeta.mbArtistId
    mdata.track = trackMeta.title.encode("utf-8")
    mdata.trackId = trackMeta.mbTrackId
    mdata.trackNum = trackMeta.number
    tr.setStatus(tunepimp.eRecognized)
    tr.setServerMetadata(mdata)
    tr.unlock()
    tp.releaseTrack(tr);
    tp.writeTags([fileId],)
    noti = tp.getNotification()
    from time import sleep
    i = 0
    while noti[1] <> 3:
        print noti
    	i = i + 1
	if i == 1000:
	    raise Exception("Taking too long to save")
        sleep(0.1)
        noti = tp.getNotification()

