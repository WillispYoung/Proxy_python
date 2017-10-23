import json
import socket
import threading
from Modifier import *


class Server(object):
    def __init__(self):
        try:
            data = json.load(open("init/config.json"))
            self.proxy_address = ("", data["server"]["proxy_port"])
            self.server_address = ("", data["server"]["listen_port"])
        except IOError:
            print("config file error")

        self.encrypt_map, self.decrypt_map = load_map("init/map")

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(20)
        print("server listen on", self.server_address[1])

    def generate_proxy_socket(self):
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.connect(self.proxy_address)
        return proxy

    def read_client(self, client_socket, proxy_socket):
        while True:
            try:
                msg = client_socket.recv(4096)
                msg = decrypt(msg, self.decrypt_map)
                proxy_socket.send(msg)
            except socket.error:
                break
        client_socket.close()
        proxy_socket.close()

    def read_proxy(self, client_socket, proxy_socket):
        while True:
            try:
                msg = proxy_socket.recv(4096)
                msg = encrypt(msg, self.encrypt_map)
                client_socket.send(msg)
            except socket.error:
                break
        client_socket.close()
        proxy_socket.close()

    def handle_client(self, client):
        proxy = self.generate_proxy_socket()
        client.settimeout(30)
        proxy.settimeout(30)

        t1 = threading.Thread(target=self.read_client, args=(client, proxy))
        t2 = threading.Thread(target=self.read_proxy, args=(client, proxy))
        t1.setDaemon(True)
        t2.setDaemon(True)
        t1.start()
        t2.start()

    def run(self):
        while True:
            (client, addr) = self.server_socket.accept()
            self.handle_client(client)


if __name__ == "__main__":
    s = Server()
    s.run()
