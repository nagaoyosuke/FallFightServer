class MemberBase:
    #入室してる部屋
    RoomBase = None
    isJoin = False

    def __init__(self,socket,ip,port,ID,name):
        self.socket = socket
        self.ip = ip
        self.port = port
        self.ID = ID
        self.name = name
