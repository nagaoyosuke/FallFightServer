class MemberBase:
    #入室してる部屋
    RoomBase = None
    isJoin = False

    def __init__(self,client,server,ID,name,nickName,streetAddress):
        self.client = client
        self.server = server
        self.ID = ID
        self.name = name
