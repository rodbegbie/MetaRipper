import gst

def error_cb(bin, element, error, debug):
    print error
    raise SystemExit

def convert():
    src = gst.element_factory_make("filesrc", "src")
    src.set_property("location", "/home/rod/01.flac")
    src_pad = src.get_pad("src")

    flac = gst.element_factory_make("flacdec", "decoder")
       
    mp3 = gst.element_factory_make("lame", "encoder")
    
    sink = gst.element_factory_make("filesink", "sink")
    sink.set_property("location", "/home/rod/test.mp3")

    bin = gst.Pipeline()
    bin.add_many(src,flac,mp3,sink)
    gst.element_link_many(src,flac,mp3,sink)
    bin.connect("error", error_cb)
    
    bin.set_state(gst.STATE_PAUSED)
    
    res = bin.set_state(gst.STATE_PLAYING);
    while bin.iterate():
        pass
    
if __name__ == "__main__":
    convert()