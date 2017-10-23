import json
import socket
from threading import Thread
from Modifier import *
from Util import *


class Shunt(object):
    def __init__(self):
        try:
            data = json.load(open("init/config.json"))
            self.listen_addr = ("localhost", data["shunt"]["listen_port"])
            self.noVPN_addr = (data["shunt"]["noVPN_ip"], data["shunt"]["noVPN_port"])
            self.VPN_addr = (data["shunt"]["VPN_ip"], data["shunt"]["VPN_port"])
            self.event_addr = ("localhost", data["shunt"]["event_listen_port"])
            self.GUI_addr = ("localhost", data["GUI"]["listen_port"])
        except IOError:
            print("config file not found, program exit")
            exit(1)

        print("local proxy addr: ", self.noVPN_addr)
        print("remote proxy addr: ", self.VPN_addr)
        print("listen addr: ", self.listen_addr)

        self.encrypt_map, self.decrypt_map = load_map("init/map")
        self.shunt_status = "dead"         # or alive

        self.acceptor = None
        self.event_listener = None
        # self.event_emitter = None

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
                        # print("REQ: " + header)

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
                                proxy = self.generate_socket(self.noVPN_addr)
                                proxy.settimeout(20)
                                self.user_proxy[u][0] = proxy
                                self.user_proxy[u][1] = "noVPN"

                                event_emitter = self.generate_socket(self.GUI_addr)
                                event_emitter.send(bytes("ejected: "+header, encoding="utf-8"))
                                event_emitter.close()

                                print("ejected:", header)
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
        rp = self.generate_socket(self.VPN_addr)
        self.user_proxy[s] = [rp, "VPN"]
        s.settimeout(30)
        rp.settimeout(30)
        Thread(target=self.user2proxy, args=(s, rp)).start()
        Thread(target=self.proxy2user, args=(s, rp)).start()

    def run_shunt(self):
        self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.acceptor.bind(self.listen_addr)
        self.acceptor.listen(30)
        # print("shunt program listening on port", self.listen_addr[1])

        while True:
            try:
                s, _ = self.acceptor.accept()
                self.handle_user_connection(s)
            except socket.error as e:
                print(e)
                continue

    def handle_control_message(self, s):
        try:
            msg = s.recv(1024)
            if msg == b'connect':
                self.shunt_status = "alive"
            elif msg == b'disconnect':
                self.shunt_status = "dead"
            else:
                print("invalid control message")
        except socket.error:
            pass
        s.close()

    def run(self):
        self.run_shunt()
        # Thread(target=self.run_shunt).start()

        # self.event_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.event_listener.bind(self.event_addr)
        # self.event_listener.listen(20)
        # print("event listener listening on port", self.event_addr[1])
        #
        # while True:
        #     s, addr = self.event_listener.accept()
        #     self.handle_control_message(s)
