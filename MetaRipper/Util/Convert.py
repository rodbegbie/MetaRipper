import gst
import os
import eyeD3
from data.MusicBrainz import *

def error_cb(bin, element, error, debug):
    print error
    raise SystemExit

def convert(flacfile, mp3file):
    print "Converting %s... " % flacfile
    src = gst.element_factory_make("filesrc", "src")
    src.set_property("location", flacfile)
    src_pad = src.get_pad("src")

    flac = gst.element_factory_make("flacdec", "decoder")
       
    mp3 = gst.element_factory_make("lame", "encoder")
    mp3.set_property("bitrate", 192)
    mp3.set_property("quality", 2)
    
    sink = gst.element_factory_make("filesink", "sink")
    sink.set_property("location", mp3file)

    bin = gst.Pipeline()
    bin.add_many(src,flac,mp3,sink)
    gst.element_link_many(src,flac,mp3,sink)
    bin.connect("error", error_cb)
    
    bin.set_state(gst.STATE_PAUSED)
    
    res = bin.set_state(gst.STATE_PLAYING);
    while bin.iterate():
        pass
    print "Done.\n"
    
if __name__ == "__main__":
    import gnosis.xml.pickle    
    tag = eyeD3.Tag()
    for root, dirs, files in os.walk("/home/rod/flac"):
        mp3dir = root.replace("/flac/", "/mp3/")
        if not os.path.exists(mp3dir):
            os.makedirs(mp3dir)

        discmetafile = os.path.join(root, "discmetadata.xml")

        if os.path.exists(discmetafile):
            f = open(discmetafile, "r")
            xml = f.read()
            discmeta = gnosis.xml.pickle.loads(xml)
            f.close()
            
        coverfilename = os.path.join(root, "cover.jpg")

        cover = False
        if os.path.exists(coverfilename):
            cover = True
            
        if cover and not os.path.exists(os.path.join(mp3dir, "cover.jpg")):
            cin = open(coverfilename, "rb")
            cout = open(os.path.join(mp3dir, "cover.jpg"), "wb")
            cout.write(cin.read())
            cin.close()
            cout.close()
            
        for file in files:
            if file.endswith(".flac"):
                flacfile = os.path.join(root,file)
                mp3file = flacfile.replace(".flac", ".mp3").replace("/flac/", "/mp3/")
                conv = True
                if os.path.exists(mp3file):
                    print "%s already there" % mp3file
                    if os.path.getmtime(flacfile) < os.path.getmtime(mp3file):
                        conv = False
                
                if conv:
                    convert(flacfile,mp3file)

                tag.link(mp3file)
                gotMB = False
                gotCover = False
                
                for frame in tag.frames:
                    if frame.header.id == 'UFID':
                        gotMB = True
                    if frame.header.id == 'APIC':
                        gotCover = True

                if not gotMB:
                    try:
                        print "Adding MB info to MP3 ID3 tags"
                        trackNum = int(file[0:2])
                        writeTags(mp3file, discmeta, trackNum)
                    except:
                        print "failed doing the tagwriting thing"
    
                if cover and not gotCover:
                    tag.link(mp3file)
                    print "Adding cover to MP3 ID3 tags"
                    tag.addImage(3, coverfilename, u"cover")
                    tag.update()