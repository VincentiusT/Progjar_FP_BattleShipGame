from DefClass import Attack, Message, RecordBoard, Room, ListRoom
import socket
import sys
import threading
import os
import ntpath
import pickle

def receive_attack(sock_cli):
    while True:
        data = b''
        while True:
            part = sock_cli.recv(65535)
            data += part
            if len(part) < 65535:
                # either 0 or end of data
                break
            
        obj = pickle.loads(data)
        if isinstance(obj, Message):
            if obj.msg == "ready":
                print(obj.dest, " is ready!")
                global canPlay
                canPlay = True
            elif obj.msg == "invite":
                print("invitation to play from ", obj.dest, " type [ accept ",obj.dest,"] to play")
                global opponent 
                opponent = obj.dest
            elif obj.msg == "accepted":
                print("invitation accepted!\n") 
                opponent = obj.dest
                BattleShipIntro()
            elif obj.msg == "attackSuccess":
                print("your attack hit a ship!")
            elif obj.msg == "attackFailed":
                print("your attack miss!")
            elif obj.msg == "startTurn":
                print("--your turn--") 
                global myturn
                myturn = True
            elif obj.msg == "roomCreated":
                print("room is created!\n")

        if isinstance(obj, ListRoom):
            print("room list:\n")
            room_list = obj.roomList.items()
            for item in room_list:
                print(item)
        if isinstance(obj, Attack):
            check_attack(obj.coordinateX, obj.coordinateY)
        if isinstance(obj, RecordBoard):
            recordBoard[obj.coordinateX][obj.coordinateY] = obj.value
            print_recordBoard()
            

def check_attack(x,y):
    hitOrMiss = 0 #if hit=3, if miss=2
    if arena[x][y] == 1:
        print("your ship was attacked!")
        global totalShip
        totalShip-=1
        arena[x][y] = 3
        hitOrMiss = 3
        atkSuccess = pickle.dumps(Message(opponent, "attackSuccess"))
        sock_cli.send(atkSuccess)
        if totalShip <= 0:
            print("all of your ships have been destroyed!")
            global canPlay
            canPlay=False
            global isReady
            isReady=False
    elif arena[x][y] == 0:
        print("your ship is safe!")
        arena[x][y] = 2
        hitOrMiss = 2
        atkFailed = pickle.dumps(Message(opponent, "attackFailed"))
        sock_cli.send(atkFailed)
    updateRecordBoard = pickle.dumps(RecordBoard(opponent, x, y, hitOrMiss))
    sock_cli.send(updateRecordBoard)
    print_arena()
    global myturn
    myturn = True
    print("--your turn--") 
    
def print_arena():
    for n in arena:
        print(n)

def print_recordBoard():
    print("here is your record board to see if your attack hit successfully or miss:\n"
    "0= empty, 2=hit a empty space, 3=hit a ship")
    for n in recordBoard:
        print(n)

def input_ship(n):
    # for x in range(n):
    #     ship = input()
    #     coord = ship.split(" ")
    #     arena[int(coord[0])][int(coord[1])] = 1
    while True:
        ship = input()
        coord_y, coord_x = ship.split(" ")
        coord_y, coord_x = int(coord_y), int(coord_x)

        while True:
            dir = input("Input ship direction (h or v)")
            if dir not in ["h", "v"]:
                print("Input must be h or v!")
                continue
            else: 
                break
        
        if dir == "h":
            if coord_x+n >= 10:
                print("Ship is out of bounds!")
                print("Re-enter ship coordinates")
                continue
            else:
                for i in range(n):
                    arena[coord_y][coord_x+i] = 1
                break
        elif dir == "v":
            if coord_y+n >= 10:
                print("Ship is out of bounds!")
                print("Re-enter ship coordinates")
                continue
            else:
                for i in range(n):
                    arena[coord_y+i][coord_x] = 1
                break

    
def BattleShipIntro():
    print("--BattleShip Game!--\n"
    "arena 10x10\n"
    "    0  1  2  3  4  5  6  7  8  9\n"
    "----------------------------------\n"
    "0| [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n"
    "1| [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n"
    "2| [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n"
    "3| [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n"
    "4| [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n"
    "5| [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n"
    "6| [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n"
    "7| [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n"
    "8| [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n"
    "9| [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n"
    "you have 5 ships to be set:\n"
    "- Destroyer ship (size 2)\n"
    "- Submarine ship (size 3)\n"
    "- Cruiser ship (size 3)\n"
    "- Battleship (size 4)\n"
    "- Carrier (size 5)\n\n"
            
    "[Set your position]\n"
    "1. set destroyer ship (size 2) enter coordinates:")
    input_ship(2)
            
    print("2. set submarine ship (size 3) enter coordinates:")
    input_ship(3)

    print("3. set cruiser ship (size 3) enter coordinates:")
    input_ship(3)

    print("4. set battleship ship (size 4) enter coordinates:")
    input_ship(4)

    print("5. set submarine ship (size 5) enter coordinates:")
    input_ship(5)

    print("your ships are set! get ready for battle!")
    print_arena()
    print("0 = empty space, 1 = there is a ship, 2 = attacked location\n")
    print("opponent : ", opponent)
    readyMessage = pickle.dumps(Message(opponent, "ready"))
    sock_cli.send(readyMessage)
    global isReady
    isReady=True
    if canPlay :
        startTurn = pickle.dumps(Message(opponent, "startTurn"))
        sock_cli.send(startTurn)
    isReady=True
    print("\nwaiting for the enemy to set their ships...", canPlay, myturn)
    

sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock_cli.connect(('192.168.0.106', 80))

#kirim username ke server
username = sys.argv[1]
sock_cli.send(bytes(username, "utf-8"))

# buat thread utk membaca pesan dan jalankan threadnya
thread_cli = threading.Thread(target=receive_attack, args=(sock_cli,))
thread_cli.start()

canPlay = False
myturn = False
isReady = False
inRoom = False

arena = [[0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0]]

recordBoard = [[0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0]]

opponent = ""
totalShip = 17

try:
    while True:
        if isReady == False:
            if not inRoom:
                msg = input("BattleShip Game:\n-invite <username>\n-accept <username> \n-create room\n-join <roomname>\n-list room\n ")
                msg = msg.split(" ")
                if msg[0] == "accept":
                    print("invitation accepted!\n")
                    accMsg = pickle.dumps(Message(msg[1], "accept"))
                    sock_cli.send(accMsg)
                elif msg[0] == "invite":
                    invMsg = pickle.dumps(Message(msg[1], "invite"))
                    sock_cli.send(invMsg)
                elif msg[0] == "create":
                    room = pickle.dumps(Room(username))
                    print("waiting for people joining tour room..\n")
                    inRoom = True
                    sock_cli.send(room)
                elif msg[0] == "join":
                    joinMsg = pickle.dumps(Message(msg[1], "join"))
                    opponent = msg[1]
                    sock_cli.send(joinMsg)
                    BattleShipIntro()
                elif msg[0] == "list":
                    listRoom = pickle.dumps(ListRoom(username, "listRoom"))
                    sock_cli.send(listRoom)

        while(canPlay):
            if(myturn):
                coordinate = input("enter coordinate to attack!: ")
                coordinateXY = coordinate.split(" ")
                if recordBoard[int(coordinateXY[0])][int(coordinateXY[1])] == 2 or recordBoard[int(coordinateXY[0])][int(coordinateXY[1])] == 3:
                    print("this coordinate has been used")
                    continue
                atkCoordinate =pickle.dumps(Attack(opponent, int(coordinateXY[0]), int(coordinateXY[1])))
                sock_cli.send(atkCoordinate)
                myturn=False


except KeyboardInterrupt:
    sock_cli.close()
    sys.exit(0)
