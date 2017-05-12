import json
import socket
import time

data = json.load(open("init/config.json"))

msgs = ["addport@13579,2",
        "upgrade@13579,3",
        "getflow@13579",
        "preflow@13579",
        "getIP@13579",
        "getIPList@13579",
        "close@13579,3",
        "reopen@13579"]

for i in range(len(msgs)):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((data["client_ip"], int(data["control_socket_port"])))
    s.send(bytearray(msgs[i], encoding="utf-8"))
    if 1 < i < 6:
        msg = s.recv(4096).decode("utf-8")
        print(msg)
    s.close()
    time.sleep(1)