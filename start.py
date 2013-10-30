#!/usr/bin/env python2

import sys, subprocess
errors = False

try:
	import zmq
except ImportError, e:
	sys.stderr.write("You are missing ZeroMQ; `pip install pyzmq`\n")
	errors = True

try:
	import zmq
except ImportError, e:
	sys.stderr.write("You are missing msgpack; `pip install msgpack-python`\n")
	errors = True

try:
	import zmq
except ImportError, e:
	sys.stderr.write("You are missing requests; `pip install requests`\n")
	errors = True

try:
	import lxml.html
except ImportError, e:
	sys.stderr.write("You are missing lxml (needs 2.0 or higher); `pip install lxml`\n")
	errors = True

if errors == False:
	subprocess.call(["/bin/sh", "_start.sh"])
	
	sys.stdout.write("pastebin-scrape is now running. Run `python retrieve.py` to add additional retrieval workers.\n")
