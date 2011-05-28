import os        
from gnosis.xml.pickle import XML_Pickler

SAFE_CHARS = range(65,91) + range(97,123) + range(48,58)

class DiscMetadata(XML_Pickler):
    def __init__ (self):
        self.title = ""
        self.artist = ""
        self.artistSort = ""
        self.variousArtists = False
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
        self.genre = ""
        self.ripTime = None
        self.lastUpdateDate = None
        self.tracks = []

class TrackMetadata(XML_Pickler):
    def __init__ (self):
        self.number = 0
        self.title = ""
        self.artist = ""
        self.artistSort = ""
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

def makePath(discmeta, overwrite=False, append=False):
    fileroot = "/mnt/flac" #HACK: Shouldn't be hardcoded
    path = os.path.join(fileroot, _makeSafe(discmeta.artistSort), _makeSafe(discmeta.title))
    if os.path.exists(path) and not overwrite:
        if not append:
            return None
        else:
            i = 1            
            while True:
                newTitle = "%s %d" % (discmeta.title, i)
                path = os.path.join(fileroot, _makeSafe(discmeta.artistSort), _makeSafe(newTitle))
                if not os.path.exists(path):
                    os.makedirs(path)
                    return path
                i = i + 1
                
    if not os.path.exists(path):
        os.makedirs(path)
        pass
        
    return path
    
def makeTrackFilename(path, discmeta, trackNum):
    track = discmeta.tracks[trackNum-1]
    if discmeta.variousArtists:
        filename = "%02d-%s-%s.flac" % (trackNum, _makeSafe(track.artist), _makeSafe(track.title))
    else:
        filename = "%02d-%s.flac" % (trackNum, _makeSafe(track.title))

    return os.path.join(path, filename)

def makeMetadataFilename(path, discmeta):
    filename = "discmetadata.xml"
    return os.path.join(path, filename)
    
