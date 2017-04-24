import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("166.111.80.96", 22222))

while True:
    msg = input("input command")
    if msg == "quit":
        break
    s.send(msg)

s.close()
