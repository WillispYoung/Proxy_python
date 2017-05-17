import os
import time
import json
import socket
import select
import subprocess
from threading import Thread
from pathlib import Path
from modifier import *
from util import *
from queue import Queue


msg_queue = Queue()


class SocketThread(Thread):
    def __init__(self, func):
        super(SocketThread, self).__init__(target=func)
        self.func = func

    def run(self):
        while True:
            (socket1, socket2, option) = msg_queue.get()
            self.func(socket1, socket2, option)


class Manager(object):
    def __init__(self):
        try:
            data = json.load(open("init/config.json"))
            self.server_address = (data["server_ip"], int(data["server_port"]))
            self.control_socket_address = ("", int(data["control_socket_port"]))
        except IOError:
            print("config file error")

        self.encrypt_map, self.decrypt_map = load_map("init/map")
        self.bandwidth = {1: 1, 5: 2, 10: 5, 20: 10, 50: 20}
        self.port_ipaddr = {}

        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.bind(self.control_socket_address)
        self.control_socket.listen(20)
        print("manager listen on", self.control_socket_address[1])

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

    def read_user(self, user, server):
        while True:
            try:
                msg = user.recv(4096)
                msg = encrypt(msg, self.encrypt_map)
                server.send(msg)
            except socket.error:
                break
        user.close()
        server.close()

    def read_server(self, user, server):
        while True:
            try:
                msg = server.recv(4096)
                msg = decrypt(msg, self.decrypt_map)
                user.send(msg)
            except socket.error:
                break
        user.close()
        server.close()

    def transfer(self, socket1, socket2, option):
        if option == "u2s":
            self.read_user(socket1, socket2)
        elif option == "s2u":
            self.read_server(socket1, socket2)

    def handle_user(self, user):
        remote_address = user.getpeername()
        local_address = user.getsockname()
        if self.port_ipaddr[local_address[1]] != remote_address[0]:
            self.port_ipaddr[local_address[1]] = remote_address[0]
            now = (time.strftime("%Y-%m-%d,%H:%M:%S"), time.localtime())[0]
            command = "/home/zy/script/record_ip.sh " + str(local_address[1]) + " " + remote_address[0] + " " + now
            subprocess.Popen(command, shell=True)

        server = self.generate_server_socket()
        user.settimeout(10)
        server.settimeout(10)
        msg_queue.put((user, server, "u2s"))
        msg_queue.put((user, server, "s2u"))
        # Thread(target=self.read_user, args=(user, server)).start()
        # Thread(target=self.read_server, args=(user, server)).start()

    def handle_control_msg(self, control):
        data = control.recv(256).decode('utf-8')
        head = data.split('@')[0]
        msg = data.split('@')[1]
        if head == "addport":
            port = int(msg.split(',')[0])
            user_type = int(msg.split(',')[1])
            self.add_listen_port(port)
            print("open port", port, "type:", user_type)

            if type != 0:
                try:
                    subprocess.Popen("iptables -A OUTPUT -p tcp --sport "+str(port)+" -j ACCEPT", shell=True)
                    subprocess.Popen("iptables -t mangle -A OUTPUT -p tcp --sport "+str(port)+" -j MARK --set-mark "+str(port-10000), shell=True)
                    subprocess.Popen("tc class add dev eth9 parent  1: classid 1:"+str(port-10000)+" htb rate "+str(self.bandwidth[user_type])+"mbit ceil " + str(self.bandwidth[user_type] + 1) + "mbit burst 20k", shell=True)
                    subprocess.Popen("tc filter add dev eth9 parent 1: protocol ip prio 1 handle "+str(port-10000)+" fw classid 1:"+str(port-10000), shell=True)
                except Exception as e:
                    print(e)

        elif head == "upgrade":
            port = int(msg.split(',')[0])
            user_type = int(msg.split(',')[1])
            if type != 0:
                subprocess.Popen("tc class change dev eth9 parent  1: classid 1:"+str(port-10000) +
                                 " htb rate "+str(self.bandwidth[user_type])+"mbit ceil "+str(self.bandwidth[user_type]+1)+"mbit burst 20k", shell=True)
            subprocess.Popen("iptables -D INPUT -p tcp --dport "+str(port)+" -j DROP", shell=True)

        elif head == "downgrade":
            port = int(msg.split(',')[0])
            user_type = int(msg.split(',')[1])
            if type != 0:
                subprocess.Popen("tc class change dev eth9 parent  1: classid 1:"+str(port-10000) +
                                 " htb rate "+str(self.bandwidth[user_type])+"mbit ceil "+str(self.bandwidth[user_type]+1)+"mbit burst 20k", shell=True)

        elif head == "reopen":
            port = int(msg)
            subprocess.Popen("iptables -D INPUT -p tcp --dport "+str(port)+" -j DROP", shell=True)

            file1 = Path("/proxy/over_flow/"+str(port)+".1")
            file2 = Path("/proxy/over_flow/"+str(port)+".2")
            if file1.exists() and file1.is_file():
                os.remove("/proxy/over_flow/" + str(port)+".1")
            if file2.exists() and file2.is_file():
                os.remove("/proxy/over_flow/" + str(port) + ".2")

        elif head == "close":
            port = int(msg.split(',')[0])
            user_type = int(msg.split(',')[1])
            print("close port", port, "type", user_type)
            subprocess.Popen("iptables -A INPUT -p tcp --dport "+str(port)+" -j DROP", shell=True)

        elif head == "getflow":
            port = int(msg)
            result = get_flow_result(port)
            print("get", port, "flow", result)
            control.send(bytearray(str(result), encoding="utf-8"))

        elif head == "preflow":
            port = int(msg)
            result = get_pre_flow(port)
            print("get", port, "pre flow", result)
            control.send(bytearray(str(result), encoding="utf-8"))

        elif head == "getIP":
            port = int(msg)
            ip_address = get_ip_address(port)
            print("get", port, "ip address", ip_address)
            control.send(bytearray(ip_address, encoding="utf-8"))

        elif head == "getIPList":
            port = int(msg)
            ip_list = get_ip_address_list(port)
            if len(ip_list) == 0:
                control.send(bytearray("", encoding="utf-8"))
            else:
                for ip in ip_list:
                    control.send(bytearray(ip+",", encoding="utf-8"))
            print("get", port, "IP list")

        control.close()

    def run(self):
        self.add_listen_port(12345)
        self.port_ipaddr[12345] = ""
        print("add initial port", 12345)

        for i in range(0, 2000):
            SocketThread(self.transfer).start()

        while True:
            read_list, _, _ = select.select(self.listen_list, [], [])

            for req in read_list:
                if req == self.control_socket:
                    control, _ = self.control_socket.accept()
                    try:
                        self.handle_control_msg(control)
                    except (socket.error, IOError) as e:
                        print(e)
                else:
                    user, _ = req.accept()
                    self.handle_user(user)


if __name__ == "__main__":
    m = Manager()
    m.run()
