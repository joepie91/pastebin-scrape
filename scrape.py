import zmq, time, requests, lxml.html, msgpack

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind("ipc:///tmp/pbscrape-tasks")
logger = context.socket(zmq.PUSH)
logger.connect("ipc:///tmp/pbscrape-log")

last_list = []

while True:
	try:
		page = requests.get("http://pastebin.com/archive").text
	except Exception, e:
		# TODO: Log HTTP error
		time.sleep(30)
		continue
		
	if "temporarily blocked your computer" in page:
		logger.send(msgpack.packb({"component": "scrape", "timestamp": int(time.time()), "message": "Got throttled, sleeping..."}))
		time.sleep(600)
		continue
		
	basetime = int(time.time())
		
	xml = lxml.html.fromstring(page)
	
	pastes = xml.xpath("//table[@class='maintable']/tr")
	new_list = []
	found = 0
	
	for paste in pastes:
		try:
			title, filetype = paste.xpath("td/a/text()")
		except ValueError, e:
			continue # Not a valid entry
			
		paste_id = paste.xpath("td[1]/a/@href")[0][1:]
		ago = paste.xpath("td[2]/text()")[0]
		
		new_list.append(paste_id)
		
		if paste_id not in last_list:
			found += 1
			socket.send(msgpack.packb({"id": paste_id, "type": filetype, "title": title, "base_time": basetime, "ago": ago}))
	
	logger.send(msgpack.packb({"component": "scrape", "timestamp": int(time.time()), "message": "Scraped metadata for %d new pastes." % found}))
	
	last_list = new_list
	
	time.sleep(1 * 60)
