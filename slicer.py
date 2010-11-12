import os
import urllib
import json
import random
import traceback
from flvtools import flv

data = json.loads(urllib.urlopen("http://usher.justin.tv/find/live_user_officecam.json").read())[0]
token = data['token']
host, app = data['connect'].split('/')[2:]
stream = data['play']
fname = 'temp_%i.flv' % random.randint(0,100000)
try:
	com = "flvpuller.py -h %s -a %s -s %s -m '%s' -o %s" % (host, app, stream, token, fname)
	output = os.popen(com).read()
except:
	traceback.print_exc()
finally:
	os.unlink(fname)
	print "Deleted temporary file %s." % fname
	

