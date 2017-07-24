import json
import socket
import subprocess
from threading import Thread
from modifier import *
from util import *


class Client(object):
    def __init__(self):
        try:
            data = json.load(open("init/config.json"))
            self.local_proxy_addr = ("localhost", data["shunt"]["local_proxy_port"])
            self.listen_addr = ("localhost", data["shunt"]["listen_port"])
            self.remote_proxy_addr = (data["shunt"]["remote_proxy_ip"], data["shunt"]["remote_proxy_port"])
            print("config information loaded")
        except IOError:
            print("config file not found")
            exit(1)
        self.encrypt_map, self.decrypt_map = load_map("init/map")

        self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.acceptor.bind(self.listen_addr)
        self.acceptor.listen(20)
        print("shunt program listening on port", self.listen_addr[1])

        self.user_proxy = {}               # { user socket: [proxy socket, status] }
        self.sohu_private_vid = set()

    @staticmethod
    def generate_socket(addr):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        return s

    def user2proxy(self, u, p):
        user = u
        proxy = p
        while True:
            try:
                msg = user.recv(4096)
                if self.user_proxy[u][1] == "VPN":
                    try:
                        content = msg.decode("utf-8")
                        header = content.split("\n")[0]

                        # sohu: get vid from feature header
                        if "&passwd=" in header:
                            vid = header.split("vid=")[1].split("&")[0]
                            self.sohu_private_vid.add(vid)

                        if is_video_request(header):
                            # iqiyi private video
                            if "&qd_tvid=" in header and "&qd_vipdyn=" not in header:
                                self.user_proxy[u][1] = "private"

                            # sohu private video
                            if self.user_proxy[u][1] == "VPN":
                                for vid in self.sohu_private_vid:
                                    if ("vid=" + vid) in header:
                                        self.user_proxy[u][1] = "private"
                                        break

                            # for youku, 111.13.140.* or 103.41.140.* shall be ejected
                            # otherwise set to private
                            if check_youku_request(header):
                                if not (u.getpeername()[0].startswith("111.13.140") or
                                            u.getpeername()[0].startswith("103.41.140")):
                                    self.user_proxy[u][1] = "private"

                            # if request is still normal video request
                            # then set to noVPN and eject it
                            if self.user_proxy[u][1] == "VPN":
                                proxy = self.generate_socket(self.local_proxy_addr)
                                proxy.settimeout(10)
                                print("ejected:", header)
                                self.user_proxy[u][0] = proxy
                                self.user_proxy[u][1] = "noVPN"
                                Thread(target=self.proxy2user, args=(user, proxy)).start()

                    except UnicodeDecodeError:
                        pass
                if self.user_proxy[u][1] != "noVPN":
                    msg = encrypt(msg, self.encrypt_map)
                proxy.send(msg)
            except socket.error:
                break
        user.close()
        proxy.close()

    def proxy2user(self, u, p):
        user = u
        proxy = p
        while True:
            if self.user_proxy[u][0] != proxy:
                proxy.close()
                break
            try:
                msg = proxy.recv(4096)
                if self.user_proxy[u][1] != "noVPN":
                    msg = decrypt(msg, self.decrypt_map)
                user.send(msg)
            except socket.error:
                break
        user.close()
        proxy.close()

    def handle_user_connection(self, s):
        rp = self.generate_socket(self.remote_proxy_addr)
        self.user_proxy[s] = [rp, "VPN"]
        s.settimeout(10)
        rp.settimeout(10)
        Thread(target=self.user2proxy, args=(s, rp)).start()
        Thread(target=self.proxy2user, args=(s, rp)).start()

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
