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

class Ripper:
    def setUpPipeline(self, device):
        self.bin = gst.Pipeline()

        self.cdp = gst.element_factory_make("cdparanoiasrc", "src")
        self.cdp.set_property("device", device)
        self.cdp.set_property("paranoia-mode", 4)

        self.queue = gst.element_factory_make("queue", "queue")
        self.queue.set_property("max-size-time", 120 * gst.SECOND)

        self.flac = gst.element_factory_make("flacenc", "encoder")
       
        self.sink = gst.element_factory_make("filesink", "sink")

        self.bin.add(self.cdp, self.queue, self.flac, self.sink)
        gst.element_link_many(self.cdp, self.queue, self.flac, self.sink)

    def ripTrack(self, trackNo, filename, callbackProgress, callbackComplete):
        print "RIP %s" % trackNo
        self.cdp.set_property("track", trackNo)
        #cdp.set_state(gst.STATE_NULL);
        self.sink.set_state(gst.STATE_NULL);
        self.sink.set_property("location", filename)
        self.cbC = callbackComplete
        self.tNo = trackNo
    
        #bin.set_state(gst.STATE_PAUSED)
        #print "get_state", bin.get_state(gst.CLOCK_TIME_NONE)
    
        #bus.add_signal_watch()
        #bus.connect('message', self.on_message)
        print "GO"
        state_ret = self.bin.set_state(gst.STATE_PLAYING);
        print "STATE!", state_ret
        #print "get_state", bin.get_state(gst.CLOCK_TIME_NONE)
    
        if (state_ret == gst.STATE_CHANGE_ASYNC):
            state_ret = self.bin.get_state(gst.SECOND)
            print "STATE2!", state_ret

        self.done = False
        bus = self.bin.get_bus()
        while (not self.done):
            msg = bus.poll(gst.MESSAGE_EOS | gst.MESSAGE_ERROR, gst.SECOND)
            #print "MSG", msg
            if msg:
                self.on_message(bus, msg)
                break

            state_ret = self.bin.get_state(gst.SECOND)
            #print "STATETICK", state_ret
            time = self.cdp.query_position(gst.FORMAT_TIME)
            print "TIME", time
        print "DUN"


    def on_message(self, bus, msg):
        t = msg.type
        print msg
        if t == gst.MESSAGE_EOS:
            print "HAMMER"
            self.bin.set_state(gst.STATE_NULL)
            print "STOPCDP"
            self.cdp.set_state(gst.STATE_NULL)
            print "STOPQUEUE"
            self.queue.set_state(gst.STATE_NULL)
            print "STOPFLAC"
            self.flac.set_state(gst.STATE_NULL)
            print "STOPSINK"
            self.sink.set_state(gst.STATE_NULL)
            print "TIME"
            self.cbC(self.tNo)
            self.done = True
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

    
