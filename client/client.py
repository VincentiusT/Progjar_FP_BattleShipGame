from DefClass import Attack, Message
import socket
import sys
import threading
import os
import ntpath
import pickle

def receive_attack(sock_cli):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
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
            elif obj.msg == "attackSuccess":
                print("your attack hit a ship!")
            elif obj.msg == "attackFailed":
                print("your attack miss!")
            elif obj.msg == "startTurn":
                print("--your turn--") 
                global myturn
                myturn = True
        if isinstance(obj, Attack):
            check_attack(obj.coordinateX, obj.coordinateY)
            

def check_attack(x,y):
    if arena[x][y] != 0:
        print("your ship was attacked!")
        global totalShip
        totalShip-=1
        arena[x][y] = 2
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
        atkFailed = pickle.dumps(Message(opponent, "attackFailed"))
        sock_cli.send(atkFailed)
    print_arena()
    global myturn
    myturn = True
    print("--your turn--") 
    
def print_arena():
    for n in arena:
        print(n)

def input_ship(n):
    for x in range(n):
        ship = input()
        coord = ship.split(" ")
        arena[int(coord[0])][int(coord[1])] = 1

sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock_cli.connect(('192.168.0.106', 80))

#kirim username ke server
sock_cli.send(bytes(sys.argv[1], "utf-8"))

# buat thread utk membaca pesan dan jalankan threadnya
thread_cli = threading.Thread(target=receive_attack, args=(sock_cli,))
thread_cli.start()

canPlay = False
myturn = False
isReady = False

arena = [[0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0]]

opponent = ""
totalShip = 17

try:
    while True:
        if isReady == False:
            msg = input("BattleShip Game:\n1.invite <username>\n2.accept <username> \n")
            msg = msg.split(" ")
            if msg[0] == "accept":
                print("invitation accepted!\n")
                accMsg = pickle.dumps(Message(msg[1], "accept"))
                sock_cli.send(accMsg)
            elif msg[0] == "invite":
                invMsg = pickle.dumps(Message(msg[1], "invite"))
                sock_cli.send(invMsg)

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
            isReady=True
            if canPlay :
                startTurn = pickle.dumps(Message(opponent, "startTurn"))
                sock_cli.send(startTurn)
            isReady=True
            print("\nwaiting for the enemy to set their ships...", canPlay, myturn)

        while(canPlay):
            if(myturn):
                coordinate = input("enter coordinate to attack!: ")
                coordinateXY = coordinate.split(" ")
                atkCoordinate =pickle.dumps(Attack(opponent, int(coordinateXY[0]), int(coordinateXY[1])))
                sock_cli.send(atkCoordinate)
                myturn=False


except KeyboardInterrupt:
    sock_cli.close()
    sys.exit(0)
