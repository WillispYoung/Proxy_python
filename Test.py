import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("166.111.80.96", 22222))

msg = input("input command")
s.send(bytes(msg, encoding="utf-8"))
s.close()
