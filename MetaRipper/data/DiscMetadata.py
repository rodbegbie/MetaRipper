import os        
from gnosis.xml.pickle import XML_Pickler

SAFE_CHARS = range(65,91) + range(97,123) + range(48,58)

class DiscMetadata(XML_Pickler):
    def __init__ (self):
        self.title = ""
        self.artist = ""
        self.toc = []
        self.mbAlbumId = ""
        self.mbDiscId = ""
        self.mbArtistId = ""
        self.discNumber = (1,1)
        self.releaseDate = None
        self.barcodeType = ""
        self.barcode = ""
        self.country = ""
        self.amazonStore = ""
        self.amazonAsin = ""
        self.ripTime = None
        self.lastUpdateDate = None
        self.tracks = []

class TrackMetadata(XML_Pickler):
    def __init__ (self):
        self.number = 0
        self.title = ""
        self.artist = ""
        self.length = 0
        self.mbArtistId = ""
        self.mbTrackId = ""
        self.mbTrm = ""

def _makeSafe(string):
    retval = ""
    for char in string[:]:
        charint = ord(char)
        if charint in SAFE_CHARS:
            retval = retval + char
        else:
            retval = retval + "_"
    return retval

def _makePath(discmeta):
    fileroot = "/home/rod/flac" #HACK: Shouldn't be hardcoded
    path = os.path.join(fileroot, _makeSafe(discmeta.artist), _makeSafe(discmeta.title))
    if not os.path.exists(path):
        os.makedirs(path)
    return path
    

def makeTrackFilename(discmeta, trackNum):
    path = _makePath(discmeta)
    track = discmeta.tracks[trackNum-1]
    if discmeta.artist == "Various Artists":
        filename = "%02d - %s - %s.flac" % (trackNum, _makeSafe(track.artist), _makeSafe(track.title))
    else:
        filename = "%02d - %s.flac" % (trackNum, _makeSafe(track.title))

    # Tack on the disc number if necessary
#    if discmeta.discNumber[1] <> 1:
#        filename = "%d-%s" % (discmeta.discNumber[0], filename)

    return os.path.join(path, filename)

def makeMetadataFilename(discmeta):
    path = _makePath(discmeta)
    filename = "discmetadata.xml"

    # Tack on the disc number if necessary
#    if discmeta.discNumber[1] <> 1:
#        filename = "%d-%s" % (discmeta.discNumber[0], filename)

    return os.path.join(path, filename)
    