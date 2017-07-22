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
        self.private_videos = []           # [ (privacy flag, check private video request) ]
        self.assert_video_feature = {(sohu_check_feature_header,
                                      sohu_get_vid_from_feature_header,
                                      sohu_check_vid_from_video_request)}

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

                        for (m1, m2, m3) in self.assert_video_feature:
                            if m1(header):                          # check if header is feature header
                                flag = m2(header)                   # get privacy flag value
                                if (flag, m3) not in self.private_videos:
                                    self.private_videos.append((flag, m3))     # push this video request
                                break

                        if is_video_request(header):
                            if "&qd_tvid=" in header and "&qd_vipdyn=" not in header:
                                self.user_proxy[u][1] = "private"       # iqiyi private video

                            if self.user_proxy[u][1] == "VPN":
                                for (flag, m) in self.private_videos:
                                    if m(header, flag):                 # go through private video list
                                        self.user_proxy[u][1] = "private"
                                        break

                            if self.user_proxy[u][1] == "VPN":          # if request is still normal video request
                                proxy = self.generate_socket(self.local_proxy_addr)  # then eject and set to noVPN
                                proxy.settimeout(10)
                                print("ejected:", header)
                                self.user_proxy[u][0] = proxy
                                self.user_proxy[u][1] = "noVPN"
                                Thread(target=self.proxy2user, args=(user, proxy)).start()

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
            if self.user_proxy[u][0] != proxy:
                proxy.close()
                break
            try:
                msg = proxy.recv(4096)
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
