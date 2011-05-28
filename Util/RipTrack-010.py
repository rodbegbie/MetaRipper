import pygst
pygst.require('0.10')
import gst
from time import sleep

def _nano2str(nanos):
    ts = nanos / gst.SECOND
    return '%02d:%02d:%02d.%02d' % (ts / 3600,
                                    ts / 60,
                                    ts % 60,
                                    nanos % gst.SECOND)

def ripTrack(device, trackNo, filename, callbackProgress, callbackComplete):
    print "RIP %s" % trackNo
    cdp = gst.element_factory_make("cdparanoiasrc", "src")
    cdp.set_property("device", device)
    cdp.set_property("paranoia-mode", 4)
    cdp.set_property("track", trackNo)
    cdp.set_state(gst.STATE_NULL);

#    src_pad = cdp.get_pad("src")

    queue = gst.element_factory_make("queue", "queue")
    queue.set_property("max-size-time", 120 * gst.SECOND)

    flac = gst.element_factory_make("flacenc", "encoder")
       
    sink = gst.element_factory_make("filesink", "sink")
    sink.set_state(gst.STATE_NULL);
    sink.set_property("location", filename)

    bin = gst.Pipeline()
    bin.add(cdp, queue, flac, sink)
    gst.element_link_many(cdp, queue, flac, sink)
    
    #bin.set_state(gst.STATE_PAUSED)
    #print bin.get_state(gst.CLOCK_TIME_NONE)
    
    bin.set_state(gst.STATE_PLAYING);
   
    print "GO"
    lastsecs = -1
    bus = bin.get_bus()
#    while 1:
    for x in range(60):
        print "TICK %d" % x
#        sleep(1)
        msg = bus.poll(gst.MESSAGE_EOS | gst.MESSAGE_ERROR, gst.SECOND)
        print msg
        if msg:
            print "DUN"
            break

    print "STOP"
    bin.set_state(gst.STATE_NULL);
    callbackComplete(trackNo)
    print "VERYEND"

#    while bin.iterate():
#        nanos = src_pad.query(gst.QUERY_POSITION, gst.FORMAT_TIME)
#        length = src_pad.query(gst.QUERY_TOTAL, gst.FORMAT_TIME)
#        secs = nanos / gst.SECOND
#        lensecs = length / gst.SECOND
#        if secs <> lastsecs and secs > 0:
#            print "secs %d, lensecs %d" % (secs,lensecs)
#            callbackProgress(trackNo, secs, lensecs)
#            lastsecs = secs

    
