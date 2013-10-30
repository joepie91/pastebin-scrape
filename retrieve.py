import zmq, msgpack, requests, time

context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.connect("ipc:///tmp/pbscrape-tasks")
sender = context.socket(zmq.PUSH)
sender.bind("ipc:///tmp/pbscrape-results")

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
	sender.send(msgpack.packb(item))
	print item
	
	time.sleep(1) # Wait a second between each paste retrieval...
