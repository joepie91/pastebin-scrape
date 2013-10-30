import zmq, msgpack, json, os, time

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("ipc:///tmp/pbscrape-results")

try:
	os.makedirs("pastes")
except OSError, e:
	pass

while True:
	item = msgpack.unpackb(socket.recv())
	
	target_dir = time.strftime("%Y-%m-%d")
	
	try:
		os.makedirs("pastes/%s" % target_dir)
	except OSError, e:
		pass
	
	f = open("pastes/%s/%s.txt" % (target_dir, item["id"]), "wb")
	f.write(item["paste"])
	f.close()
	
	del item["paste"] # To prevent writing the paste to the metadata file as well
	
	f = open("pastes/%s/%s.json" % (target_dir, item["id"]), "wb")
	json.dump(item, f)
	f.close()
