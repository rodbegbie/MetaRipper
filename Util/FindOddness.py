import os,sys
from Util import walk

if __name__ == "__main__":
    root = "/mnt/tera/flac/"
    if sys.argv:
    	root = sys.argv[1]
    for root, dirs, files in walk(root, followlinks=True):
        mp3dir = root.replace("/flac/", "/mp3/")
        print (root)
        
        coverfilename = os.path.join(root, "cover.jpg")

        tracknums = {}
        for file in files:
            if file.endswith(".flac") or file.endswith(".mp3"):
                if file[0] in "0123456789":
                    tracknum = int(file[:2])
                    if tracknum in tracknums:
                        print "***DUPLICATE TRACKNUM %d!\n%s\n%s\n" % (tracknum, tracknums[tracknum], file)
                    else:
                        tracknums[tracknum] = file
            elif file not in ["cover.jpg", "discmetadata.xml", "discmetadata.xml.bak"]:
                print "***WEIRD FILE!\n%s\n" % file

        if tracknums and max(tracknums.keys()) > len(tracknums.keys()):
            print "***FOUND %d FILES, MAXTRACKNUM %d\n" % (len(tracknums.keys()), max(tracknums.keys()))
        if not tracknums and not dirs:
            print "***NO MUSIC FILES FOUND AND NO SUBDIRS\n"
