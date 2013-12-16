import zmq, msgpack, requests, time

context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.connect("ipc:///tmp/pbscrape-tasks")
sender = context.socket(zmq.PUSH)
sender.connect("ipc:///tmp/pbscrape-results")
logger = context.socket(zmq.PUSH)
logger.connect("ipc:///tmp/pbscrape-log")

while True:
	item = msgpack.unpackb(receiver.recv())
	
	gone = False
	
	while True: # We want to keep trying until it succeeds...
		try:
			response = requests.get("http://pastebin.com/raw.php?i=%s" % item["id"])
			if response.status_code == 404:
				# Gone...
				gone = True
				break
			elif "text/html" in response.headers["Content-Type"]:
				# We most likely got an "under heavy load" message or similar; sleep a while and retry
				logger.send(msgpack.packb({"component": "retrieve", "timestamp": int(time.time()), "message": "Hit a text/html response for raw.php, servers most likely overloaded, sleeping..."}))
				time.sleep(10)
				continue # Retry
			paste = response.text
		except Exception, e:
			# TODO: Log error
			print e
			time.sleep(5)
			continue # Retry
		
		if response.status_code == 403:
			logger.send(msgpack.packb({"component": "retrieve", "timestamp": int(time.time()), "message": "Got throttled, sleeping..."}))
			time.sleep(600)
			continue # Retry
			
		break # Done
		
	if gone:
		logger.send(msgpack.packb({"component": "retrieve", "timestamp": int(time.time()), "message": "Paste %s gone, skipping..." % item["id"]}))
		continue # Next!
	item["retrieval_time"] = int(time.time())
	item["paste"] = paste
	
	logger.send(msgpack.packb({"component": "retrieve", "timestamp": int(time.time()), "message": "Downloaded paste body for %s." % item["id"]}))
	
	sender.send(msgpack.packb(item))
	
	time.sleep(1.3) # Wait a second between each paste retrieval...
