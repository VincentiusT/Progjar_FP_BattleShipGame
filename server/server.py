from DefClass import Attack, Message, Chat
import socket
import sys
import threading
import pickle

def read_msg(clients, sock_cli, addr_cli, username_cli):
    while True:
        data = b''
        while True:
            part = sock_cli.recv(65535)
            data += part
            if len(part) < 65535:
                # either 0 or end of data
                break

        obj = pickle.loads(data)
        if isinstance(obj, Chat):
            if obj.type_id == "message":
                dest_sock_cli = get_sock(username_cli, obj.dest)
                dest_sock_cli.send(pickle.dumps(Chat(username_cli, 'message', obj.msg)))
            elif obj.type_id == "bcast":
                send_bcast(username_cli, obj.msg)
            elif obj.type_id == "file":
                dest_sock_cli = get_sock(username_cli, obj.dest)
                dest_sock_cli.send(pickle.dumps(Chat(username_cli, 'file', obj.msg)))
            elif obj.type_id == "reqfriend":
                dest_uname = obj.dest
                if dest_uname not in clients:
                    send_error(username_cli, f"{dest_uname} not in clients")
                else:
                    dest_sock_cli = clients[dest_uname][0]
                    dest_sock_cli.send(pickle.dumps(Chat(username_cli, 'reqfriend', '')))
                # dest_sock_cli = get_sock(username_cli, obj.dest)
                # dest_sock_cli.send(pickle.dumps(Chat(username_cli, 'file', obj.msg)))
            elif obj.type_id == "accfriend":
                add_friend(src_uname, obj.dest)
                src_uname = username_cli
                friends[src_uname].append(dest_username)
                friends[dest_username].append(src_uname)
                dest_sock_cli = get_sock(username_cli, obj.dest)
                dest_sock_cli.send(pickle.dumps(Chat(username_cli, 'message', obj.msg)))

        elif isinstance(obj, Message):
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

        elif isinstance(obj, Attack):
            dest_sock_cli = clients[obj.dest][0]
            atkCoordinate = pickle.dumps(Attack(obj.dest, obj.coordinateX, obj.coordinateY))
            dest_sock_cli.send(atkCoordinate)

    sock_cli.close()
    print("connection closed", addr_cli)
    
def send_bcast(src_uname, msg):
    global clients
    global friends
    cur_friends = friends[src_uname]
    for cur_friend in cur_friends:
        if cur_friend not in clients:
            continue
        if cur_friend == src_uname:
            continue

        dest_sock_cli = clients[cur_friend][0]
        dest_sock_cli.send(pickle.dumps(Chat(src_uname, 'message', msg)))

def add_friend(uname1, uname2):
    global clients
    global friends
    friends[uname1].append(uname2)
    friends[uname2].append(uname1)
    dest_sock_cli_1 = clients[uname1][0]
    dest_sock_cli_2 = clients[uname2][0]
    dest_sock_cli_1.send(pickle.dumps(Chat(uname1, 'message', f"{uname2} added")))
    dest_sock_cli_2.send(pickle.dumps(Chat(uname2, 'message', f"{uname1} added")))

def get_sock(src_username, dest_username):
    global clients
    global friends
    if dest_username not in friends[src_username]:
        send_error(src_username, f"Error: {dest_username} not a friend")
        return None
    if dest_username not in clients:
        send_error(src_username, f"Error: {dest_username} not in clients")
        return None
    return clients[dest_username][0]

def send_error(uname, msg):
    global clients
    dest_sock_cli = clients[uname][0]
    dest_sock_cli.send(pickle.dumps(Chat('System', 'message', msg)))

server_address = ('192.168.0.106', 80)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_address)
server_socket.listen(5)

# buat dictionary utk menyimpan informasi
clients = {}
friends = {}

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
        friends[username_cli] = []

except KeyboardInterrupt:
    server_socket.close()
    sys.exit(0)