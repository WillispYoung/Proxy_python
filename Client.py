import sys
import json
import socket
import select
import threading
from Modifier import *


class Client(object):
    # encrypt_map
    # decrypt_map
    # server_address
    # control_socket_address
    # listen_list

    def __init__(self):
        try:
            data = json.load(open("config.json"))
            self.server_address = (data["server_ip"], int(data["server_port"]))
            self.control_socket_address = ("", int(data["control_socket_port"]))

        except IOError:
            print("config file error")

        self.encrypt_map, self.decrypt_map = load_map("map.txt")

        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket(self.control_socket_address)
        self.control_socket.listen(10)

        self.listen_list = [self.control_socket]

    def generate_server_socket(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect(self.server_address)
        return server

    def add_listen_port(self, port):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind(("", port))
        listen_socket.listen(20)
        self.listen_list.append(listen_socket)
        return listen_socket

    def read_user(self, user_socket, server_socket):
        while True:
            try:
                msg = user_socket.recv(4096)
                msg = encrypt(msg, self.encrypt_map)
                server_socket.send(msg)
            except socket.error as e:
                print(e)
                break
        user_socket.close()
        server_socket.close()

    def read_server(self, user_socket, server_socket):
        while True:
            try:
                msg = server_socket.recv(4096)
                msg = decrypt(msg, self.decrypt_map)
                user_socket.send(msg)
            except socket.error as e:
                print(e)
                break
        user_socket.close()
        server_socket.close()

    # use thread pool instead
    def handle_user(self, user_socket):
        server = self.generate_server_socket()
        threading.Thread(target=self.read_user, args=(user_socket, server)).start()
        threading.Thread(target=self.read_server, args=(user_socket, server)).start()

    def run(self):
        self.add_listen_port(12345)
        while True:
            read_list, write_list, err_list = select.select(self.listen_list, [], [])

            for req in read_list:
                if req == self.control_socket:
                    s, _ = self.control_socket.accept()
                    msg = s.recv(256)
                    args = msg.decode('utf-8').split('#')
                    # parse command part, need modification
                    if args[0] == 'add':
                        try:
                            port = eval(args[1])
                            listen_socket = self.add_listen_port(port)
                            self.listen_list.append(listen_socket)
                            print("add listen port", args[1], "succeed")
                        except socket.error:
                            print("add listen port", args[1], "failed")
                else:
                    (user, address) = req.accept()
                    self.handle_user(user)

if __name__ == "__main__":
    c = Client()
    c.run()
