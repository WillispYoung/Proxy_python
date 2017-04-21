import socket
import select
import threading

server_address = ("localhost", 4129)
client_address = ("localhost", 3333)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 4129))

data = bytearray([1, 2, 3, 4, 5, 6])

client.send(data)
msg = client.recv(256)
print("msg from server: ", msg)

client.close()
