import urllib2
import socket
from time import sleep

url = "http://scholar.thucloud.com"
req = urllib2.Request(url)
res = urllib2.urlopen(req)
# print res.getcode()
# print res.geturl()
# print res.info()
# print res.read()

content = "HTTP/1.1 200 OK\n" + res.info() + res.read()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 22222))

while True:
	s, _ = server.accept()

	sleep(0.2)
	s.send(content)
	s.close()
