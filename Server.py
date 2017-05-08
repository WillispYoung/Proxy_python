import json
import socket
import threading
from Modifier import *


class Server(object):
    def __init__(self):
        try:
            data = json.load(open("config.json"))
            self.proxy_address = ("", int(data["proxy_port"]))
            self.server_address = ("", int(data["server_port"]))
        except FileNotFoundError:
            print("config file error")

        self.encrypt_map, self.decrypt_map = load_map("map.txt")

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(20)
        print("server listening", self.server_address)

    def generate_proxy_socket(self):
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.connect(self.proxy_address)
        return proxy


#
# def read_client(client, proxy):
#     while True:
#         try:
#             msg = client.recv(4096)
#             msg = decrypt(msg, key_map)
#             proxy.send(msg)
#         except socket.error: # pls print error msg
#             break
#     client.close()
#     proxy.close()
#
#
# def read_proxy(client, proxy):
#     while True:
#         try:
#             msg = proxy.recv(4096)
#             msg = encrypt(msg, key_map)
#             client.send(msg)
#         except socket.error: # the same
#             break
#     client.close()
#     proxy.close()
#
# # not good
# # this should be changed in future
# def handle_client(client):
#     proxy = get_proxy_connection()
#     threading.Thread(target=read_client, args=(client, proxy)).start()
#     threading.Thread(target=read_proxy, args=(client, proxy)).start()
#
#
# while True:
#     (client, addr) = server.accept()
#     handle_client(client)
