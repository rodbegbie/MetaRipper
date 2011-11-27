import os,sys
from eyeD3 import Tag, FrameHeader, TextFrame, UTF_8_ENCODING

from Util import walk
from time import sleep

if __name__ == "__main__":
    import gnosis.xml.pickle    
    tag = Tag()
    root = "/mnt/tera/flac/"
    if sys.argv:
    	root = sys.argv[1]
    for root, dirs, files in walk(root, followlinks=True):
        mp3dir = root.replace("/flac/", "/mp3/")
        if not os.path.exists(mp3dir):
            os.makedirs(mp3dir)

        discmetafile = os.path.join(root, "discmetadata.xml")

        if not os.path.exists(discmetafile):
            continue
        else:
            f = open(discmetafile, "r")
            xml = f.read()
            discMeta = gnosis.xml.pickle.loads(xml)
            f.close()

        print "\n---------------------"
        print ("%s - %s" % (discMeta.artist, discMeta.title)).encode("ascii", "ignore")
        
        for file in files:
            if file.endswith(".flac"):
	        import glob
                flacfile = os.path.join(root,file)
		mp3glob = glob.glob(os.path.join(root.replace("/flac/", "/mp3/"), file[:3] + "*.mp3"))
		try:
                    mp3file = mp3glob[0]
		except IndexError:
		    print "%s - mp3 not there :(" % flacfile
		    continue
		print mp3file

                tag.link(mp3file)
                
		gotTSO2 = False
                needsUpdate = False
                
                for frame in tag.frames:
                    if frame.header.id == 'TSO2':
                        gotTSO2 = True
                        
                if not gotTSO2:
		    try:
                        print "Updating TSO2 fields"
                        tpe2Header = FrameHeader(tag.header)
                        tpe2Header.id = "TSO2"
                        tpe2 = TextFrame(tpe2Header)
                        tpe2.text = discMeta.artistSort if 'artistSort' in dir(discMeta) else discMeta.artist
                        tag.frames.append(tpe2)
	       	        needsUpdate = True
                    except:
		        print "SOMETHING WENT BAD :("
                    
                if needsUpdate:
                    try:
		    	tag.setTextEncoding(UTF_8_ENCODING)
                        tag.update()
                    except:
                        print "FAILED first time -- trying again"
			try:
                            sleep(1.0)
                            tag.update()
			except:
			    print "MEGA FAIL!"
