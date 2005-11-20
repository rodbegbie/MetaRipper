import cElementTree as ET
import urllib
from time import sleep
from musicbrainz import MBI_VARIOUS_ARTIST_ID

def getArtistTopTag(artistName, mbArtistId):
    if mbArtistId == MBI_VARIOUS_ARTIST_ID:
        return None
    
    artistName = artistName.replace("&","and")
    artistName = artistName.encode('utf-8')
    url = "http://ws.audioscrobbler.com/1.0/artist/%s/toptags.xml" % urllib.quote(artistName)
    print url
    try:
        sleep(0.5)
        data = urllib.urlopen(url).read()
        xml = ET.fromstring(data)
#        print ET.tostring(xml)
#        print "Is this it?  %s" % xml.find("tag/name").text
        tag = xml.find("tag/name")
        if tag <> None:
            return tag.text.lower()
        return None
    except:
        print "EXCEPTION!!!!!!!!"
        import traceback,sys
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import os
    import gnosis.xml.pickle
    
    artistTags = {}
    
    for root, dirs, files in os.walk("/mnt/flac"):
        discmetafile = os.path.join(root, "discmetadata.xml")

        if os.path.exists(discmetafile):
            #print "opening %s" % discmetafile
            f = open(discmetafile, "r")
            xml = f.read()
            #print xml
            discmeta = gnosis.xml.pickle.loads(xml)
            f.close()
            
            print "\n---------------------"
            print "%s - %s" % (discmeta.artist, discmeta.title)
            
            if hasattr(discmeta, "genre") and discmeta.genre:
                print u"Already have genre"
            else:
                genre = artistTags.get(discmeta.artist, None)
                if not genre:
                    print "Fetching from Scrobbler..."
                    genre = getArtistTopTag(discmeta.artist, discmeta.mbArtistId)
                    if genre:
                        artistTags[discmeta.artist] = genre
                    else:
                        print "Scrobbler gave me nuffink"

                if genre:
                    print "got genre: %s" % genre
                    discmeta.genre = genre
                    
                    os.renames(discmetafile, discmetafile+".bak")

                    print "saving %s" % discmetafile
                    f = open(discmetafile, "w")
                    xml = gnosis.xml.pickle.dumps(discmeta)
                    f.write(xml)
                    f.close()
