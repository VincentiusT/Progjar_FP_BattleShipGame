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
