import os        

class DiscMetadata:
    def __init__ (self):
        self.title = ""
        self.artist = ""
        self.toc = []
        self.mbAlbumId = ""
        self.mbDiscId = ""
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

class TrackMetadata:
    def __init__ (self):
        self.number = 0
        self.title = ""
        self.artist = ""
        self.length = 0
        self.mbTrackId = ""
        self.mbTrm = ""

def _makeSafe(string):
    retval = ""
    for char in string[:]:
        charint = ord(char)
        if charint in range(65,91) or charint in range(97,123):
            retval = retval + char
        else:
            retval = retval + "_"
    return retval

def makeTrackFilename(discmeta, trackNum):
    track = discmeta.tracks[trackNum-1]
    fileroot = "/home/rod/flac" #HACK: Shouldn't be hardcoded
    path = os.path.join(fileroot, _makeSafe(discmeta.artist), _makeSafe(discmeta.title))
    if not os.path.exists(path):
        os.makedirs(path)

    if discmeta.artist == "Various Artists":
        filename = "%02d - %s - %s.flac" % (trackNum, _makeSafe(track.artist), _makeSafe(track.title))
    else:
        filename = "%02d - %s.flac" % (trackNum, _makeSafe(track.title))
    return os.path.join(path, filename)
        