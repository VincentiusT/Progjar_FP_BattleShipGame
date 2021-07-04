class Message:
    def __init__(self, dest, msg):
        self.dest = dest
        self.msg = msg

class Attack:
    def __init__(self, dest, coordinateX, coordinateY):
        self.dest = dest
        self.coordinateX = coordinateX
        self.coordinateY = coordinateY

class Chat:
    def __init__(self, dest, type_id, msg):
        self.dest = dest
        self.type_id = type_id
        self.msg = msg
class RecordBoard:
    def __init__(self, dest, coordinateX, coordinateY, value):
        self.dest = dest
        self.coordinateX = coordinateX
        self.coordinateY = coordinateY
        self.value = value

class Room:
    def __init__(self, roomname):
        self.roomname = roomname

class ListRoom:
    def __init__(self, dest, roomList):
        self.dest = dest
        self.roomList = roomList