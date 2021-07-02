from DefClass import Attack, Message
import socket
import sys
import threading
import pickle

def read_msg(clients, sock_cli, addr_cli, username_cli):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break

        obj = pickle.loads(data)
        if isinstance(obj,Message):
            if obj.msg == "invite":
                dest_sock_cli = clients[obj.dest][0]
                invitePlayer = pickle.dumps(Message(username_cli,"invite"))
                dest_sock_cli.send(invitePlayer)
            elif obj.msg == "ready":
                ready = pickle.dumps(Message(username_cli,"ready"))
                dest_sock_cli.send(ready)
            elif obj.msg == "accept":
                dest_sock_cli = clients[obj.dest][0]
                startTurn = pickle.dumps(Message(username_cli,"accepted"))
                dest_sock_cli.send(startTurn)
            elif obj.msg == "attackSuccess":
                dest_sock_cli = clients[obj.dest][0]
                atkSuccess = pickle.dumps(Message(username_cli, "attackSuccess"))
                dest_sock_cli.send(atkSuccess)
            elif obj.msg == "attackFailed":
                dest_sock_cli = clients[obj.dest][0]
                atkFailed = pickle.dumps(Message(username_cli, "attackFailed"))
                dest_sock_cli.send(atkFailed)
            elif obj.msg == "startTurn":
                dest_sock_cli = clients[obj.dest][0]
                nextTurn = pickle.dumps(Message(username_cli, "startTurn"))
                dest_sock_cli.send(nextTurn)

        if isinstance(obj, Attack):
            dest_sock_cli = clients[obj.dest][0]
            atkCoordinate = pickle.dumps(Attack(obj.dest, obj.coordinateX, obj.coordinateY))
            dest_sock_cli.send(atkCoordinate)

    sock_cli.close()
    print("connection closed", addr_cli)
    

server_address = ('192.168.0.106', 80)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_address)
server_socket.listen(5)

#buat dictionary utk menyimpan informasi
clients = {}

try:
    while True:
        sock_cli, addr_cli = server_socket.accept()

        #baca username client
        username_cli = sock_cli.recv(65535).decode("utf-8")
        print(username_cli, "joined")

        #buat thread
        thread_cli = threading.Thread(target=read_msg, args=(clients, sock_cli, addr_cli, username_cli))
        thread_cli.start()

        #simpan informasi client ke dictionary
        clients[username_cli] = (sock_cli, addr_cli, thread_cli)

except KeyboardInterrupt:
    server_socket.close()
    sys.exit(0)