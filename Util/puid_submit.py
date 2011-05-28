#!/usr/bin/python
import sys
from os import walk
import os.path
from tunepimp import tunepimp
from musicbrainz2.utils import extractUuid
from musicbrainz2.webservice import WebService, Query, WebServiceError, TrackFilter

server = 'musicbrainz.org'
username = 'rODbegbie'
password = 'haggis'
batchSize = 20
#encoding = 'windows-1250'
encoding = 'utf-8'

__version__ = '0.0.1'
tp = tunepimp.tunepimp('puid_submit.py', __version__, tunepimp.tpThreadRead | tunepimp.tpThreadAnalyzer)
tp.setMusicDNSClientId('80eaa76658f99dbac1c58cc06aa44779'); 

files = []
for arg in sys.argv[1:]:
    if os.path.isdir(arg):
        for root, dirs, files2 in walk(arg):
            files.extend([os.path.join(root, file) for file in files2])
    elif os.path.isfile(arg):
        files.append(arg)

toSubmit = {}
        
for file in files:
    file = file.decode(encoding)
    fileId = tp.addFile(file, 0)
    print ("Adding %s (%s)" % (file, fileId)).encode('ascii', 'ignore')
    
ws = WebService(host=server, username=username, password=password)
q = Query(ws, clientId='puid_submit.py-%s' % (__version__,))

analyzed = {}

while tp.getNumFiles():
    ret, type, fileId, status = tp.getNotification()
    if not ret:
        continue
    
    print ret,type,fileId,status
    tr = tp.getTrack(fileId)
    tr.lock()
    fileName = tr.getFileName()
    mdata = tr.getLocalMetadata()
    tr.unlock()

    addPUID = None
    
    if status == tunepimp.ePUIDLookup:
        tr.lock()
        puid = tr.getPUID()
        tr.unlock()
        trackId = mdata.trackId
        addPUID = (fileName, puid, trackId) 
    
    elif status in [tunepimp.eUnrecognized, tunepimp.eRecognized, tunepimp.eSaved]:
        trackId = mdata.trackId
        puid = mdata.filePUID
        if len(puid) == 0:
            puid = tr.getPUID()
        if trackId and not analyzed.has_key(fileId):
            if puid:
                addPUID = (fileName, puid, trackId) 
            else:
                tr.lock()
                tr.setStatus(tunepimp.ePending)
                tr.unlock()
                tp.wake(tr)
                analyzed[fileId] = True
        else:
            print ("%s:\n\tNo MB ID (%d)\n" % (fileName,status)).encode('ascii', 'ignore')
            tp.releaseTrack(tr)
            tp.remove(fileId)
            tr = None

    if tr:
        tp.releaseTrack(tr)
    
    if status == tunepimp.eError:
        print ("%s:\n\tError: %s\n" % (fileName, tp.getError())).encode('ascii', 'ignore')
        tp.remove(fileId)
                
    if addPUID:
        try:
		fileName, puid, trackId = addPUID
	        print ("%s:\n\t%s - %s" % (fileName, puid, trackId)).encode('ascii', 'ignore')
	        flt = TrackFilter(puid=puid)
	        result = q.getTracks(flt)
	        found = False
	        for res in result:
	            if extractUuid(res.track.id, 'track') == trackId:
	                found = True
	        if not found:
	            toSubmit[trackId] = puid
	            print
	        else:
	            print "\tAlready in MB, skipping.\n"
	except:
		print "EXCEPTION THROWN LOOKING UP TRACK ID"
        tp.remove(fileId)
    
    if len(toSubmit) >= batchSize or (tp.getNumFiles() == 0 and len(toSubmit) > 0):
        print "Submitting %d PUIDs to MusicBrainz...\n" % (len(toSubmit),)
        q.submitPuids(toSubmit) 
        toSubmit = {}

