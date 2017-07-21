import json
import socket
import re
import time
import subprocess
from threading import Thread
from modifier import *


class Client(object):
    def __init__(self):
        try:
            data = json.load(open("init/config.json"))
            # use ("localhost", port) not ("", port)
            self.local_proxy_addr = ("localhost", data["shunt"]["local_proxy_port"])
            self.listen_addr = ("localhost", data["shunt"]["listen_port"])
            self.remote_proxy_addr = (data["shunt"]["remote_proxy_ip"], data["shunt"]["remote_proxy_port"])
        except IOError:
            print("config file not found")
            exit(1)

        self.encrypt_map, self.decrypt_map = load_map("init/map")

        self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.acceptor.bind(self.listen_addr)
        self.acceptor.listen(20)
        print("shunt program listening on port", self.listen_addr[1])

        self.user_proxy_dict = {}       # means user socket and proxy socket pair
        self.user_proxy_status = {}     # means using VPN or not

    def check_type(self, header):
        pattern = "GET .+\.(flv|f4v|mp4|m3u8|ts)\?.*"
        return re.match(pattern, header)

    def get_local_proxy(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.local_proxy_addr)
        return s

    def get_remote_proxy(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                        if self.check_type(first_line):
                            print(first_line)
                            proxy = self.get_local_proxy()
                            proxy.settimeout(10)
                            self.user_proxy_dict[u] = proxy
                            self.user_proxy_status[u] = "noVPN"
                            Thread(target=self.proxy2user, args=(user, proxy)).start()
                    except UnicodeDecodeError:
                        pass
                proxy.send(msg)
            except socket.error:
                break

    def proxy2user(self, u, p):
        user = u
        proxy = p
        while True:
            if self.user_proxy_dict[u] != proxy:
                proxy.close()
                break
            try:
                msg = proxy.recv(4096)
                user.send(msg)
            except socket.error:
                break

    def handle_user_connection(self, s):
        rps = self.get_remote_proxy()
        self.user_proxy_dict[s] = rps
        self.user_proxy_status[s] = "VPN"
        s.settimeout(10)
        rps.settimeout(10)
        Thread(target=self.user2proxy, args=(s, rps)).start()
        Thread(target=self.proxy2user, args=(s, rps)).start()

    def run(self):
        while True:
            s, _ = self.acceptor.accept()
            self.handle_user_connection(s)

if __name__ == "__main__":
    try:
        subprocess.Popen("C:/squid/sbin/squid", shell=True)
        print("local squid started")
    finally:
        pass
    c = Client()
    c.run()
