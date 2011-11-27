import xml.etree.cElementTree as ET
import urllib
from time import sleep
#from musicbrainz import MBI_VARIOUS_ARTIST_ID

def getArtistTopTag(artistName, mbArtistId):
    if mbArtistId == "89ad4ac3-39f7-470e-963a-56509c546377": #MBI_VARIOUS_ARTIST_ID:
        return None
    
    artistName = artistName.replace("&","and")
    artistName = artistName.encode('utf-8')
    url = "http://ws.audioscrobbler.com/1.0/artist/%s/toptags.xml" % urllib.quote(artistName)
    print url
    try:
        sleep(0.5)
        data = urllib.urlopen(url).read()
        xml = ET.fromstring(data)
        retval = None
        MAX_TAGS=5
        tags = xml.findall("tag/name")
        if len(tags) == 0:
            return None
    
        if len(tags) > MAX_TAGS:
            tags = tags[:MAX_TAGS]
            
        tags = [tag.text.lower() for tag in tags]
        tags.sort()
            
        return "/".join(tags)
    except:
        print "EXCEPTION!!!!!!!!"
        import traceback,sys
        traceback.print_exc()
        return None

