import json
import socket
import time

data = json.load(open("init/config.json"))

msg1 = ["addport@13579,2",
        "upgrade@13579,3"]

msg2 = ["getflow@12345",
        "preflow@12345",
        "getIP@12345",
        "getIPList@12345"]

msg3 = ["close@13579,3",
        "reopen@13579"]


for m in msg1:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((data["client_ip"], int(data["control_socket_port"])))
    s.send(bytearray(m, encoding="utf-8"))
    s.close()
    time.sleep(1)

for m in msg2:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((data["client_ip"], int(data["control_socket_port"])))
    s.send(bytearray(m, encoding="utf-8"))
    msg = s.recv(1024)
    print(msg)
    s.close()
    time.sleep(1)
