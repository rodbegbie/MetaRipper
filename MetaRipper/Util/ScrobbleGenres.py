from data.AudioScrobbler import getArtistTopTag

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
            print ("%s - %s" % (discmeta.artist, discmeta.title)).encode("ascii", "ignore")
            
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
