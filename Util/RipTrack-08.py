import gst
import logging
import thread
from time import sleep

def _nano2str(nanos):
    ts = nanos / gst.SECOND
    return '%02d:%02d:%02d.%02d' % (ts / 3600,
                                    ts / 60,
                                    ts % 60,
                                    nanos % gst.SECOND)

def ripTrack(device, trackNo, filename, callbackProgress, callbackComplete):
    cdp = gst.element_factory_make("cdparanoia", "ripper")
    cdp.set_property("device", device)
    cdp.set_property("paranoia-mode", 4)
    cdp.set_property("abort-on-skip", True)
    track_format = gst.format_get_by_nick("track")
    src_pad = cdp.get_pad("src")

    flac = gst.element_factory_make("flacenc", "encoder")
       
    sink = gst.element_factory_make("filesink", "sink")
    sink.set_property("location", filename)

    bin = gst.Pipeline()
    bin.add_many(cdp, flac, sink)
    gst.element_link_many(cdp, flac, sink)
    
    bin.set_state(gst.STATE_PAUSED)
    
    seek = gst.event_new_segment_seek(track_format | gst.SEEK_METHOD_SET | gst.SEEK_FLAG_FLUSH,
                                      trackNo - 1, trackNo)
    src_pad.send_event(seek)
    
    res = bin.set_state(gst.STATE_PLAYING);
    
    lastsecs = -1
    while bin.iterate():
        nanos = src_pad.query(gst.QUERY_POSITION, gst.FORMAT_TIME)
        length = src_pad.query(gst.QUERY_TOTAL, gst.FORMAT_TIME)
        secs = nanos / gst.SECOND
        lensecs = length / gst.SECOND
        if secs <> lastsecs and secs > 0:
            #print "secs %d, lensecs %d, rate %f" % (secs,lensecs, rate)
            callbackProgress(trackNo, secs, lensecs)
            lastsecs = secs

    res = bin.set_state(gst.STATE_NULL)
    callbackComplete(trackNo)
    
