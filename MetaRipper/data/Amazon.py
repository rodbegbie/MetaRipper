from Util import amazon
import urllib
import ImageFile
from data.DiscMetadata import DiscMetadata

amazon.setLicense("1AGTVVHBTYPBQKT7G482")

def getAmazonInfoByUPC(barcode):
    if barcode:
        try:
            res = amazon.searchByUPC(barcode)
        except:
            print "Amazon search failed"
            return None
            
        asin = res[0].Asin
        image = getBestImage([res[0].ImageUrlLarge,
                              res[0].ImageUrlMedium,
                              res[0].ImageUrlSmall])
        
        return ("us", asin, image)

    return None
            
def getAmazonInfoByString(string, store="us"):
    results = []

    try:
        res = amazon.searchByKeyword(string, locale=store, product_line="music")
    except:
        print "Amazon search failed"
        return None
    
    for result in res:
        resultdict = {}
        resultdict["asin"] = result.Asin
        resultdict["image"] = getBestImage([result.ImageUrlLarge,
                                            result.ImageUrlMedium,
                                            result.ImageUrlSmall])
        resultdict["name"] = "%s - %s" % (result.Artists.Artist, result.ProductName)
        print resultdict
        results.append(resultdict)
        
    return (store, results)
            

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
    import gnosis.xml.pickle
    for root, dirs, files in os.walk("/mnt/flac"):
        discmetafile = os.path.join(root, "discmetadata.xml")
        coverjpg = os.path.join(root, "cover.jpg")

        if os.path.exists(discmetafile):
            print "opening %s" % discmetafile
            f = open(discmetafile, "r")
            xml = f.read()
            #print xml
            discmeta = gnosis.xml.pickle.loads(xml)
            f.close()
            
            if discmeta.amazonAsin:
                print u"Skipping %s:  Already have ASIN" % discmeta.title
            else:
                print "Fetching %s" % discmeta.title.decode("ascii",'ignore')
                inf = getAmazonInfoByUPC(discmeta.barcode)
                if not inf:
                    print "Amazon gave me nuffink"
                else:
                    print "got ASIN"
                    discmeta.amazonStore = inf[0]
                    discmeta.amazonAsin = inf[1]
                    if inf[2]:
                        jpg = urllib.urlopen(inf[2]).read()
                        f = open(coverjpg, "wb")
                        f.write(jpg)
                        f.close()
                        print "got cover jpg"
                    
                    os.renames(discmetafile, discmetafile+".bak")

                    print "saving %s" % discmetafile
                    f = open(discmetafile, "w")
                    xml = gnosis.xml.pickle.dumps(discmeta)
                    f.write(xml)
                    f.close()

