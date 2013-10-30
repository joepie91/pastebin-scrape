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
	
	while True: # We want to keep trying until it succeeds...
		try:
			paste = requests.get("http://pastebin.com/raw.php?i=%s" % item["id"]).text
		except Exception, e:
			# TODO: Log error
			print e
			time.sleep(5)
			continue # Retry
		break # Done
		
	item["retrieval_time"] = int(time.time())
	item["paste"] = paste
	
	logger.send(msgpack.packb({"component": "retrieve", "timestamp": int(time.time()), "message": "Downloaded paste body for %s." % item["id"]}))
	
	sender.send(msgpack.packb(item))
	
	time.sleep(1) # Wait a second between each paste retrieval...
