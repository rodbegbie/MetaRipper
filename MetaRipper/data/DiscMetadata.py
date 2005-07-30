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