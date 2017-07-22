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

        self.user_proxy = {}                    # { user socket: [proxy socket, status] }
        self.check_private_video = []           # [ (privacy flag, check private video request) ]
        self.assert_video_feature = {(sohu_check_feature_header,
                                      sohu_get_vid_from_feature_header,
                                      sohu_check_vid_from_video_request)}

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
                if self.user_proxy[u][1] == "VPN":
                    try:
                        content = msg.decode("utf-8")
                        first_line = content.split("\n")[0]

                        for tri in self.assert_video_feature:
                            if tri[0](first_line):                          # check if header is feature header
                                flag = tri[1](first_line)                   # get privacy flag value
                                print(flag)
                                self.check_private_video.append((flag, tri[2]))     # push this video request into stack
                                break

                        if is_video_request(first_line):
                            for pair in self.check_private_video:
                                if pair[1](first_line, pair[0]):            # go through private video list and check
                                    self.user_proxy[u][1] = "private"
                                    break

                            if self.user_proxy[u][1] == "VPN":     # if request is still normal video request
                                proxy = self.get_local_proxy()          # then eject and set to noVPN
                                proxy.settimeout(10)
                                print(first_line)
                                self.user_proxy[u][0] = proxy
                                self.user_proxy[u][1] = "noVPN"
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
            if self.user_proxy[u][0] != proxy:
                proxy.close()
                break
            try:
                msg = proxy.recv(4096)
                user.send(msg)
            except socket.error:
                break

    def handle_user_connection(self, s):
        rp = self.get_remote_proxy()
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
