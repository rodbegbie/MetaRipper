import os,sys
from data.MusicBrainz import *
from data.DiscMetadata import *
from Util import walk

if __name__ == "__main__":
    import gnosis.xml.pickle    
    for root, dirs, files in walk("/mnt/tera/flac/Supergrass",followlinks=True):
        discmetafile = os.path.join(root, "discmetadata.xml")

        if os.path.exists(discmetafile):
            f = open(discmetafile, "r")
            xml = f.read()
            discmeta = gnosis.xml.pickle.loads(xml)
            f.close()
        else:
            continue
            
        print "\n\n======================================"
        print ("Checking %s - %s" % (discmeta.artist, discmeta.title)).encode("ascii", "ignore")

	try:
	    mb = searchMbByDiscId(discmeta.mbAlbumId)
	except:
	    print "***** MB SEARCH FAILED *****"
	    sys.stdout.flush()
	    continue
        
        if not mb:
            print "***** DISC ID NO LONGER VALID FOR: '%s' *****" % discmeta.title
	    sys.stdout.flush()
            continue
        
        (newDiscMeta, dirchange) = updateDiscMetadata(mb, discmeta)
        
        if not newDiscMeta:
            print "OK"
	    justUpdateTags = True
	    sys.stdout.flush()
            continue
        else:
            print "***** ALBUM NEEDS UPDATERING! *****"
	    justUpdateTags = False
        
        if False: #!!!dirchange:
            newpath = makePath(newDiscMeta, False, True)
            coverjpg = os.path.join(root, 'cover.jpg')
            if os.path.exists(coverjpg):
                print "moving cover.jpg"
                newcoverjpg = os.path.join(newpath, 'cover.jpg')
                os.renames(coverjpg, newcoverjpg)
            mp3dir = root.replace("/flac/", "/mp3/")
            newmp3dir = newpath.replace("/flac/", "/mp3/")
            coverjpg = os.path.join(mp3dir, 'cover.jpg')
            if os.path.exists(coverjpg):
                print "moving MP3 cover.jpg"
                newcoverjpg = os.path.join(newmp3dir, 'cover.jpg')
                os.renames(coverjpg, newcoverjpg)
        else:
            newpath = root

        for file in files:
            if file.endswith(".flac"):
                trackNum = int(file[0:2])
                flacfile = os.path.join(root,file)
                mp3file = flacfile.replace(".flac", ".mp3").replace("/flac/", "/mp3/")
                newflacfile = makeTrackFilename(newpath, discmeta, trackNum)
                newmp3file = newflacfile.replace(".flac", ".mp3").replace("/flac/", "/mp3/")
		if len(newmp3file) > 150:
		    print "SHORTENING ", newmp3file
		    newmp3file = newmp3file[:146] + ".mp3"
                    
                if flacfile <> newflacfile:
                    print "Moving %s to %s" % (flacfile, newflacfile)
                    os.renames(flacfile, newflacfile)
               
	        try:
                    writeTags(newflacfile, discmeta, trackNum)
		except:
		    print "failed doing the tagwriting thing:", sys.exc_info()[0]

                if os.path.exists(mp3file):
                    try:
                        print "Updating ID3 tags for %s" % mp3file
                        writeTags(mp3file, discmeta, trackNum)
                    except:
                        print "failed doing the tagwriting thing:",  sys.exc_info()[0]
                    if mp3file <> newmp3file:
                        print "Moving MP3 file %s" % mp3file
                        os.renames(mp3file, newmp3file)
        
	if not justUpdateTags:
	    print "Saving new metadata file"
            newdiscmetafile = makeMetadataFilename(newpath, "discmetadata.xml")
            if os.path.exists(discmetafile+".bak"):
                os.unlink(discmetafile+".bak")
            os.renames(discmetafile, newdiscmetafile+".bak")
            f = open(newdiscmetafile, "w")
            xml = gnosis.xml.pickle.dumps(discmeta)
            f.write(xml)
            f.close()        
                
	sys.stdout.flush()
    print "**** ALL DONE! ****"
