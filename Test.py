import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("47.88.19.184", 33333))
print(s.getpeername(), s.getsockname())
