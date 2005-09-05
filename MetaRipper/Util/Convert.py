import gst
import os
import pyid3lib

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
    for root, dirs, files in os.walk("/home/rod/flac"):
        mp3dir = root.replace("/flac/", "/mp3/")
        if not os.path.exists(mp3dir):
            os.makedirs(mp3dir)
            
        if os.path.exists(os.path.join(root, "cover.jpg")) and not os.path.exists(os.path.join(mp3dir, "cover.jpg")):
            cin = open(os.path.join(root, "cover.jpg"), "rb")
            cout = open(os.path.join(mp3dir, "cover.jpg"), "wb")
            coverjpg = cin.read()
            cout.write(coverjpg)
            cin.close()
            cout.close()
            cover = True
        else:
            cover = False
            
        for file in files:
            if file.endswith(".flac"):
                flacfile = os.path.join(root,file)
                mp3file = flacfile.replace(".flac", ".mp3").replace("/flac/", "/mp3/")
                conv = True
                if os.path.exists(mp3file):
                    print "%s already there" % mp3file
                    mp3date = os.path.getmtime(mp3file)
                    flacdate = os.path.getmtime(flacfile)
                    if flacdate < mp3date:
                        conv = False
                
                if conv:
                    #print "Woudl convert %s to %s" %  (flacfile, mp3file)
                    convert(flacfile,mp3file)
    
                if cover:
                    print "Adding cover to MP3 ID3 tags"
                    tag = pyid3lib.tag(mp3file)
                    d = { 'frameid': 'APIC',
                          'mimetype': 'image/jpeg',
                          'picturetype': 3,
                          'description': 'cover',
                          'data': coverjpg,
                        }
                    tag.append(d)
                    tag.update()