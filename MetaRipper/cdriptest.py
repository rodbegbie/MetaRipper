import sys
import gst

def handoff_cb(sender, *args):
    print sender.get_name(), args

def main(args):
    cdp = gst.element_factory_make("cdparanoia", "ripper")
    cdp.set_property("device", "/dev/cdroms/cdrom0")
    cdp.set_property("paranoia-mode", 255)
    track_format = gst.format_get_by_nick("track")
    src_pad = cdp.get_pad("src")

#    tags = gst.TagList()
#    tags["title"] = "Kill Yr Boyfriend"
#    tags["artist"] = "Bis"
#    tags["track-number"] = "16"
#    tags["track-count"] = "19"
#    tags["album"] = "Radio One yadadadada"
    flac = gst.element_factory_make("flacenc", "encoder")
    flac.tag_setter_add(gst.TAG_MERGE_REPLACE_ALL, "title", "Kill Yr Boyfriend")

#    flac.connect("handoff", handoff_cb)
       
    sink = gst.element_factory_make("filesink", "sink")
#    sink = gst.element_factory_make("osssink", "sink")
    sink.set_property("location", "/home/rod/test.flac")
#    sink.connect("handoff", handoff_cb)

    bin = gst.Pipeline()
    bin.add_many(cdp, flac, sink)
    gst.element_link_many(cdp, flac, sink)
    
    bin.set_state(gst.STATE_PAUSED)
    
    seek = gst.event_new_segment_seek(track_format | gst.SEEK_METHOD_SET | gst.SEEK_FLAG_FLUSH, 15, 16)
    src_pad.send_event(seek)
    
    res = bin.set_state(gst.STATE_PLAYING);
    assert res
    
    while bin.iterate():
        pass
    
    res = bin.set_state(gst.STATE_NULL)
    assert res

if __name__ == '__main__':
    sys.exit(main(sys.argv))