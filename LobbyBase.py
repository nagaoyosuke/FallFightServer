import logging
import psycopg2
import os
import json
import random
from collections import deque
from MemberBase import MemberBase
from RoomBase import RoomBase

class LobbyBase:

    def __init__(self, maxUser):
        self.maxUser = maxUser
        self.maxRooms = int(maxUser / 4) + 1
        self.__IDTable = deque(range(1,maxUser))
        self.__RoomIDTable = deque(range(1,self.maxRooms))
        self.Member = []
        self.Rooms = []
        

    def __handler(self,func,*args):
        return func(*args)

    #Nullチェック
    def MemberCheck(self,func,arg):
        if func != None:
            my = self.__handler(func,arg)
            if my == None:
                #sendData = dict([('state', 'Error'), ('message', str(ErrMessage))])
                #sendData = dict([('state', 'Error'), ('message', 'You donot join Member in Lobby')])
                #server.send_message(socket,json.dumps(sendData))
                return False
        return True

    def Login(self, socket,ip,port, data):
        print(data['name'])

        #DBの設定がないからIDの送信は今の所必要ない(01/22)
        # m = MemberBase(socket,data['ID'],data['name'])
        m = MemberBase(socket,ip,port,self.__IDTable.popleft(),data['name'])

        # if len(self.Member) > 0:
        #     if self.Member in m:
        #         self.ErrorSend(socket,'100','You are already login Lobby')
        #         return

        self.Member.append(m)
        
        #IDを適当にとってるから修正必要、あと被ることがあるからそれも(01/22)
        #順番になった
        sendData = dict([('state', 'Login'), ('ID', str(m.ID))])
        socket.send(self.ChangeJsonSend(sendData))

    def Logout(self,socket):

        print("Logout")
        #対戦相手の情報が残ってるから削除
        # user = self.GetFindMemberFromOppClient(socket)
        logoutUser = self.GetFindMemberFromClient(socket)
        self.__IDTable.append(logoutUser)

        if logoutUser != None:
            self.Member.remove(logoutUser)

        if user == None:
            return

        user.opp = None
        
        sendData = dict([('state', 'Info'), ('message', 'Your Opp Logout')])
        socket.send(self.ChangeJsonSend(sendData))

    def LobbyMemberList(self, socket, data):
        base = dict([('ID',-1), ('name','Hoge')])
        sendData = {"state": "MemberList","Member": []}

        # sendData.append(dict([('state','MemberList')]))
        # sendData.append('state')
        # sendData.append('MemberList')

        for m in self.Member:
            if m.isBattle == True:
                continue

            b = base.copy()
            b['ID'] = m.ID
            b['name'] = m.name
            sendData['Member'].append(b)
        
        print(sendData)
        socket.send(self.ChangeJsonSend(sendData))

    def CreateRoomRequest(self, socket, data):
        if self.MemberCheck(self.GetFindMemberFromClient,socket) == False:
            self.ErrorSend(socket,'101','You donot join Member in Lobby')
            return

        m = self.GetFindMemberFromUserID(data['ID'])

        if m.isJoin == True:
            self.ErrorSend(socket,'103','You have already created or entered a room')
            return

        r = RoomBase(self.__RoomIDTable,data['roomName'],4,m)
        self.Rooms.append(r)

    def GetFindMemberFromSocket(self,socket):
        for value in self.Member:
            if value.socket == socket:
                return value
        return None

    def GetFindMemberFromOppClient(self,socket):
        for value in self.Member:
            if value.opp == None:
                continue
            if value.opp.socket == socket:
                return value
        return None

    def GetFindMemberFromUserID(self,ID):
        for value in self.Member:
            if str(value.ID) == str(ID):
                return value
        return None

    def ChangeJsonSend(self,json_SendData):
        return json.dumps(json_SendData,ensure_ascii=False).encode('utf_8')

    def ErrorSend(self,socket,code,message,isAll=False):
        sendData = dict([('state', 'Error'), ('code', str(code)), ('message', message)])
        if isAll == True:
            for m in self.Member:
                socket.send(self.ChangeJsonSend(sendData))
        else:    
            socket.send(self.ChangeJsonSend(sendData))

    def OpenChat(self, socket, data):
        for m in self.Member:
            m.socket.send(str(data).encode('utf_8'))            

    def DirectChat(self, socket, data):

        if self.MemberCheck(self.GetFindMemberFromClient,socket) == False:
            self.ErrorSend(socket,'101','You donot join Member in Lobby')
            return

        if self.MemberCheck(self.GetFindMemberFromUserID,data['oppID']) == False:
            self.ErrorSend(socket,'102','Opponent donot join Member in Lobby')
            return

        my = self.GetFindMemberFromClient(socket)
        opp = self.GetFindMemberFromUserID(data['oppID'])

        sendData = dict([('state', 'DirectChat'),('oppID', my.ID),('oppName', my.name),('text', data['text'])])

        server.send_message(opp.socket,json.dumps(sendData,ensure_ascii=False))
