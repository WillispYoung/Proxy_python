import socket
import threading
from Modifier import *

# make these configurable
proxy_address = ("", 3128)
server_address = ("", 33333)
key_map = load_map("map.txt")


def get_proxy_connection():
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET and sock config should also be loaded from config file
    proxy.connect(proxy_address)
    return proxy


def read_client(client, proxy):
    while True:
        try:
            msg = client.recv(4096)
            msg = decrypt(msg, key_map)
            proxy.send(msg)
        except socket.error: # pls print error msg
            break
    client.close()
    proxy.close()


def read_proxy(client, proxy):
    while True:
        try:
            msg = proxy.recv(4096)
            msg = encrypt(msg, key_map)
            client.send(msg)
        except socket.error: # the same
            break
    client.close()
    proxy.close()

# not good
# this should be changed in future
def handle_client(client):
    proxy = get_proxy_connection()
    threading.Thread(target=read_client, args=(client, proxy)).start()
    threading.Thread(target=read_proxy, args=(client, proxy)).start()

# why put these code here
# and configurable again
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(server_address)
server.listen(20)
print("server listening", server_address)

while True:
    (client, addr) = server.accept()
    handle_client(client)
