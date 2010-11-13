import os
import sys
import urllib
import glob
import json
import random
import traceback
import pickle
import random
from flvtools import flv

category = 'gaming'
limit = 100
channels = []
format = 'jpg'

url = "http://usher.justin.tv/stream/list.json?limit=%s" % (limit * 2)
if category:
    url += "&category=%s" % category    
data = json.loads(urllib.urlopen(url).read())
for row in data:
    channels.append(row['channel'])
random.shuffle(channels)
print "Slicing from following pool of channels (limit %s): %s" % (limit, channels)

seconds = 30.0
prefix = 'frames/'

completed = 0
for channel in channels:
    try:
        data = json.loads(urllib.urlopen("http://usher.justin.tv/find/live_user_%s.json" % channel).read())[0]
        token = data['token']
    except:
        print "Error slicing channel %s:" % channel
        traceback.print_exc()
        continue
    host, app = data['connect'].split('/')[2:]
    stream = data['play']
    fname = 'temp_%i.flv' % random.randint(0,100000)
    try:
        print "Capturing %.2f seconds of channel %s..." % (seconds, channel)
        com = "flvpuller.py -h %s -a %s -s %s -m '%s' -o %s -g %.2f" % (host, app, stream, token, fname, seconds)
        output = os.popen(com).read()
        print "Done."
        print "Examing output file..."
        size = len(open(fname).read())
        if size < (seconds * 10000):
            print "  File too small! (%s bytes)" % size
            continue
        print "Cleaning up old frames..."
        com = "rm %s%s-*.%s" % (prefix, channel, format)
        output = os.popen(com).read()
        print "Done."
        print "Splitting video into individual frames..."
        com = "ffmpeg -i %s -s 320x240 -f image2 %s%s-%%05d.%s" % (fname, prefix, channel, format)
        output = os.popen(com).read()
        print "Done."
        print "Calculating frame delay..."
        frames = len(glob.glob('%s%s-*.%s' % (prefix, channel, format)))
        delay = seconds / frames
        print "Saved %s frames over %.2fs for a frame delay of %.3f" % (frames, seconds, delay)
        print "Done."
        pickle.dump(delay, open(prefix + channel + '.dat', 'w'))
    except:
    	traceback.print_exc()
    finally:
    	os.unlink(fname)
    	print "Deleted temporary file %s." % fname
    completed += 1
    if completed == limit: 
        break
	

