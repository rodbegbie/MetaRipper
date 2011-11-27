import pygst
pygst.require('0.10')
import gst
import os,sys
from eyeD3 import Tag, FrameHeader, TextFrame, UTF_8_ENCODING

from data.MusicBrainz import *
from Util import walk
from time import sleep

def error_cb(bin, element, error, debug):
    print error
    raise SystemExit

def convert(flacfile, mp3file):
    print "Converting %s... " % flacfile
    src = gst.element_factory_make("filesrc", "src")
    src.set_property("location", flacfile)
    #src_pad = src.get_pad("src")

    flac = gst.element_factory_make("flacdec", "decoder")

    mp3 = gst.element_factory_make("lame", "encoder")
    mp3.set_property("bitrate", 192)
    #mp3.set_property("quality", 2)
    #mp3.set_property("vbr", 4)
    #mp3.set_property("vbr-quality", 2)

    id3 = gst.element_factory_make("id3v2mux", "tagger")

    #xing = gst.element_factory_make("xingmux", "vbrfixer")

    sink = gst.element_factory_make("filesink", "sink")
    sink.set_property("location", mp3file)

    bin = gst.Pipeline()
    bin.add(src,flac,mp3,id3,sink)
    gst.element_link_many(src,flac,mp3,id3,sink)
    #bin.connect("error", error_cb)

    bin.set_state(gst.STATE_PLAYING)

    print "GO"
    bus = bin.get_bus()
    while 1:
        msg = bus.poll(gst.MESSAGE_EOS | gst.MESSAGE_ERROR, gst.SECOND)
        if msg:
            print msg
            print "DUN"
            break

    print "STOP"
    bin.set_state(gst.STATE_NULL);

    print "Done.\n"

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

        metaUpdateTime = os.path.getmtime(discmetafile)

        coverfilename = os.path.join(root, "cover.jpg")

        cover = False
        if os.path.exists(coverfilename):
            cover = True
            coverUpdateTime = os.path.getmtime(coverfilename)

        mp3CoverFilename = os.path.join(mp3dir, "cover.jpg")
        if cover and ((not os.path.exists(mp3CoverFilename)) \
                 or (os.path.getmtime(mp3CoverFilename) < coverUpdateTime)):
            print "Copying cover.jpg"
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
                #    if os.path.getmtime(mp3file) > metaUpdateTime:
                #        continue
                    #if os.path.getmtime(flacfile) <= os.path.getmtime(mp3file):
                    conv = False

                if conv:
                    convert(flacfile,mp3file)

                tag.link(mp3file)
                gotMB = False
                trackNum = int(file[0:2])

                for frame in tag.frames:
                    if frame.header.id == 'UFID':
                        gotMB = True
                        break

                if not gotMB:
                    try:
                        print "Adding MB info to MP3 ID3 tags"
                        writeTags(mp3file, discMeta, trackNum)
                    except:
                        print "failed doing the tagwriting thing:",  sys.exc_info()[0]
                        writeTags(mp3file, discMeta, trackNum)

                # Reload the tags now that TunePimp's done its stuff
                tag = Tag()
                tag.link(mp3file)
                gotCover = False
                gotTPOS = False
                gotTYER = False
                gotTPE2 = False
                gotTSO2 = False
                needsUpdate = False

                for frame in tag.frames:
                    if frame.header.id == 'APIC':
                        gotCover = True
                    if frame.header.id == 'TPOS':
                        gotTPOS = True
                    if frame.header.id == 'TPE2':
                        gotTPE2 = True
                    if frame.header.id == 'TSO2':
                        gotTSO2 = True

                if cover and not gotCover:
                    tag.link(mp3file)
                    print "Adding cover to MP3 ID3 tags"
                    tag.addImage(3, coverfilename, u"cover")
                    needsUpdate = True

                if not gotTPE2:
                    print "Updating TPE2 fields"
                    tpe2Header = FrameHeader(tag.header)
                    tpe2Header.id = "TPE2"
                    tpe2 = TextFrame(tpe2Header)
                    tpe2.text = discMeta.artist
                    tag.frames.append(tpe2)
                    needsUpdate = True

                if not gotTPOS:
                    print "Updating TPOS/TRCK fields"
                    tposHeader = FrameHeader(tag.header)
                    tposHeader.id = "TPOS"
                    tpos = TextFrame(tposHeader)
                    tpos.text = "%d/%d" % discMeta.discNumber
                    tag.frames.append(tpos)

                    # Also update the TRCK to be in x/y format
                    tag.frames["TRCK"][0].text = "%d/%d" % (trackNum, len(discMeta.tracks))
                    needsUpdate = True

                if not gotTSO2:
                    try:
                        print "Updating TSO2 fields"
                        tpe2Header = FrameHeader(tag.header)
                        tpe2Header.id = "TSO2"
                        tpe2 = TextFrame(tpe2Header)
                        tpe2.text = discMeta.artistSort
                        tag.frames.append(tpe2)
                        needsUpdate = True
                    except:
                        print "SOMETHING WENT BAD :("

                if discMeta.releaseDate and not tag.getDate():
                    print "Setting release year"
                    tag.setDate(discMeta.releaseDate)
                    needsUpdate = True

                if hasattr(discMeta, "genre") and discMeta.genre and not tag.getGenre():
                    print "Setting genre"
                    tag.setGenre(discMeta.genre)
                    needsUpdate = True

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
