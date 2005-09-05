from Util import amazon
import urllib
import ImageFile
from DiscMetadata import DiscMetadata

amazon.setLicense("1AGTVVHBTYPBQKT7G482")

def getAmazonInfoByUPC(discmeta):
    if discmeta.country == "US":
        if discmeta.barcode:
            try:
                res = amazon.searchByUPC(discmeta.barcode)
            except:
                print "Amazon search failed"
                return None
                
            asin = res[0].Asin
            image = getBestImage(res[0].ImageUrlLarge,
                                 res[0].ImageUrlMedium,
                                 res[0].ImageUrlSmall)
            
            return ("us", asin, image)

    return None
            

def getBestImage(imageUrls):
    for url in imageUrls:
        sizes = getsizes(url)
        if sizes[1]:
            if sizes[1] <> (1,1):
                return url
    
    return None
        

def getsizes(uri):
    # get file size *and* image size (None if not known)
    file = urllib.urlopen(uri)
    size = file.headers.get("content-length")
    if size: size = int(size)
    p = ImageFile.Parser()
    while 1:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            return size, p.image.size
            break
    file.close()
    return size, None
    
    
    
if __name__ == "__main__":
    import os
    for root, dirs, files in os.walk("/home/rod/flac"):
        discmetafile = os.path.join(root, "discmetadata.xml")
        coverjpg = os.path.join(root, "cover.jpg")

        if os.path.exists(discmetafile):
            discmeta = DiscMetadata()
            print "opening %s" % discmetafile
            f = open(discmetafile, "r")
            xml = f.read()
            print xml
            DiscMetadata.loads(discmeta, xml)
            f.close()
            
            if discmeta.amazonAsin:
                print "Skipping %s:  Already have ASIN" % discmeta.title
            else:
                print "Fetching %s" % discmeta.title                
                inf = getAmazonInfoByUPC(discmeta)
                if inf:
                    discmeta.amazonStore = inf[0]
                    discmeta.amazonAsin = inf[1]
                    if inf[2]:
                        jpg = urllib.urlopen(inf[2]).read()
                        f = open(coverjpg, "wb")
                        f.write(jpg)
                        f.close()
                        print "Wrote jpg"
                    
                    f = open(discmetafile, "w")
                    xml = discmeta.dumps()
                    f.write(xml)
                    f.close()
                    