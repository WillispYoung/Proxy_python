import sys
import socket
import select
import threading
from Modifier import *

server_address = (sys.argv[1], eval(sys.argv[2]))
key_map = load_map("map.txt")

def get_server_socket():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(server_address)
    return server


def add_listen_port(port):
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(("", port))
    listen_socket.listen(20)
    return listen_socket


def read_user(user, server):
    while True:
        try:
            msg = user.recv(4096)
            msg = encrypt(msg, key_map)
            server.send(msg)
        except socket.error:
            break
    user.close()
    server.close()


def read_server(user, server):
    while True:
        try:
            msg = server.recv(4096)
            msg = decrypt(msg, key_map)
            user.send(msg)
        except socket.error:
            break
    user.close()
    server.close()


def handle_user(user):
    server = get_server_socket()
    threading.Thread(target=read_user, args=(user, server)).start()
    threading.Thread(target=read_server, args=(user, server)).start()


control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.bind(("", 22222))
control_socket.listen(20)

# a_user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# a_user.bind(("", 22222))
# a_user.listen(20)

listen_list = [control_socket]

while True:
    read_list, write_list, err_list = select.select(listen_list, [], [])

    for req in read_list:
        if req == control_socket:
            msg = req.recv(256)
            # command: add#12345 --> listen on port 12345
            command = msg.split('#')
            if command[0] == "add":
                port = 0
                try:
                    port = eval(command[1])
                    listen_socket = add_listen_port(port)
                    listen_list.append(listen_socket)
                except socket.error:
                    print("add port", port, "failed")
        else:
            (user, address) = req.accept()
            handle_user(user)
