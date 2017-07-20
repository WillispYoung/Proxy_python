import json
import socket
import re
from threading import Thread
from modifier import *


def check_type(header):
    return True


class Client(object):
    def __init__(self):
        try:
            data = json.load(open("init/config.json"))
            self.local_proxy_addr = ("", data["local_proxy_port"])
            self.listen_addr = ("", data["listen_port"])
            self.remote_proxy_addr = (data["remote_proxy_ip"], data["remote_proxy_port"])
        except IOError:
            print("config file not found")
            exit(1)

        self.acceptor = self.tcp_socket()
        self.acceptor.bind(self.listen_addr)
        self.acceptor.listen(20)
        print("listening " + self.listen_addr[0] + " " + str(self.listen_addr[1]))

        self.user_proxy_dict = {}       # means user socket and proxy socket pair
        self.user_proxy_status = {}     # means using VPN or not

    def tcp_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_local_proxy(self):
        s = self.tcp_socket()
        s.connect(self.local_proxy_addr)
        return s

    def get_remote_proxy(self):
        s = self.tcp_socket()
        s.connect(self.remote_proxy_addr)
        return s

    def user2proxy(self, u, p):
        user = u
        proxy = p
        while True:
            try:
                msg = user.recv(4096)
                if self.user_proxy_status[u] == "VPN":
                    try:
                        content = msg.decode("utf-8")
                        first_line = content.split("\n")[0]
                        # if first_line.startswith("GET"):
                        #     print first_line
                        if first_line.startswith("GET") and check_type(first_line):
                            print(first_line)
                            proxy = self.tcp_socket()
                            proxy.connect(self.local_proxy_addr)
                            self.user_proxy_dict[u] = proxy
                            self.user_proxy_status[u] = "noVPN"
                    except UnicodeDecodeError:
                        pass
                proxy.send(msg)
            except socket.error:
                break
        user.close()
        proxy.close()

    def proxy2user(self, u, p):
        user = u
        proxy = p
        while True:
            if self.user_proxy_dict[u] != proxy:
                proxy = self.user_proxy_dict[u]
            try:
                msg = proxy.recv(4096)
                user.send(msg)
            except socket.error:
                break
        user.close()
        proxy.close()

    def handle_user_connection(self, s):
        lps = self.get_local_proxy()
        self.user_proxy_dict[s] = lps
        self.user_proxy_status[s] = "VPN"
        Thread(target=self.user2proxy, args=(s, lps)).start()
        Thread(target=self.proxy2user, args=(s, lps)).start()

    def run(self):
        while True:
            s, _ = self.acceptor.accept()
            self.handle_user_connection(s)

if __name__ == "__main__":
    c = Client()
    c.run()