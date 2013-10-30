import zmq, msgpack

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("ipc:///tmp/pbscrape-log")

while True:
	entry = msgpack.unpackb(socket.recv())
	
	f = open("scrape.log", "a")
	f.write("[%(component)s]  %(timestamp)s  :  %(message)s\n" % entry)
	f.close()
