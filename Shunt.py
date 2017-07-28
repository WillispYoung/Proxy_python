import json
import socket
from threading import Thread
from Modifier import *
from Util import *


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
        self.youku_vid_dictionary = {}
        self.youku_private_vid = set()

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

                        # youku html request: get vid pair and add to dictionary
                        if check_youku_html_request(header):
                            id1, id2 = get_youku_vid_from_html_request(content)
                            if id1:
                                self.youku_vid_dictionary[id1] = id2

                        # youku feature request: get video id
                        if check_youku_feature_header(header):
                            vid = get_youku_vid_from_header(header)
                            try:
                                self.youku_private_vid.add(self.youku_vid_dictionary[vid])
                            except KeyError:
                                pass

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

                            # youku private video
                            if check_youku_video_request(header):
                                vid = get_youku_vid_from_header(header)
                                if vid in self.youku_private_vid:
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
        proxy.close()
        user.close()

    def proxy2user(self, u, p):
        user = u
        proxy = p
        while True:
            if self.user_proxy[u][0] != proxy:
                proxy.close()
                return
            try:
                msg = proxy.recv(4096)
                if self.user_proxy[u][1] != "noVPN":
                    msg = decrypt(msg, self.decrypt_map)
                user.send(msg)
            except socket.error:
                break

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
