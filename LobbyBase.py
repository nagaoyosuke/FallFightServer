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
        self.__IDTable = deque(range(maxUser))
        self.__RoomIDTable = deque(range(self.maxRooms))
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
                #server.send_message(client,json.dumps(sendData))
                return False
        return True

    def Login(self, client, server, data):
        print(data['name'])

        #DBの設定がないからIDの送信は今の所必要ない(01/22)
        # m = MemberBase(client,server,data['ID'],data['name'])
        m = MemberBase(client,server,self.__IDTable.popleft(),data['name'])

        if self.LoginMember in m:
            sendData = dict([('state', 'Error'), ('message', 'You are already login Lobby')])
            server.send_message(client,json.dumps(sendData,ensure_ascii=False))
            return

        self.Member.append(m)
        
        #IDを適当にとってるから修正必要、あと被ることがあるからそれも(01/22)
        #順番になった
        sendData = dict([('state', 'Login'), ('ID', str(m.ID))])
        server.send_message(client,json.dumps(sendData,ensure_ascii=False))

    def Logout(self,client,server):

        print("Logout")
        #対戦相手の情報が残ってるから削除
        # user = self.GetFindMemberFromOppClient(client)
        logoutUser = self.GetFindMemberFromClient(client)
        self.__IDTable.append(logoutUser)

        if logoutUser != None:
            self.Member.remove(logoutUser)

        if user == None:
            return

        user.opp = None
        
        sendData = dict([('state', 'Info'), ('message', 'Your Opp Logout')])
        server.send_message(user.client,json.dumps(sendData,ensure_ascii=False))  

    def LobbyMemberList(self, client, server, data):
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
        server.send_message(client,json.dumps(sendData,ensure_ascii=False))

    def CreateRoomRequest(self, client, server, data):
        if self.MemberCheck(self.GetFindMemberFromClient,client) == False:
            self.ErrorSend(client,server,'101','You donot join Member in Lobby')
            return

        m = self.GetFindMemberFromUserID(data['ID'])

        if m.isJoin == True:
            self.ErrorSend(client,server,'103','You have already created or entered a room')
            return

        r = RoomBase(self.__RoomIDTable,data['roomName'],4,m)
        self.Rooms.append(r)



    def MatchingRequest(self, client, server, data):

        if self.MemberCheck(self.GetFindMemberFromClient,client) == False:
            sendData = dict([('state', 'Error'), ('message', 'You donot join Member in Lobby')])
            server.send_message(client,json.dumps(sendData,ensure_ascii=False))
            return

        if self.MemberCheck(self.GetFindMemberFromUserID,data['oppID']) == False:
            sendData = dict([('state', 'Error'), ('message', 'Opponent donot join Member in Lobby')])
            server.send_message(client,json.dumps(sendData,ensure_ascii=False))
            return

        my = self.GetFindMemberFromClient(client)
        opp = self.GetFindMemberFromUserID(data['oppID'])
        my.opp = opp
        opp.opp = my

        my.isBattle = True
        opp.isBattle = True
        my.time = -10.0
        opp.time = -10.0

        sendData = dict([('state', 'Matching'), ('oppID', opp.ID),('oppName', opp.name)])
        server.send_message(client,json.dumps(sendData,ensure_ascii=False))
        sendData['oppID'] = my.ID
        sendData['oppName'] = my.name
        server.send_message(opp.client,json.dumps(sendData,ensure_ascii=False))

        #マッチング確認がないからすぐにバトルのセッティング
        self.BattleInit(server, my, opp, data)

    def BattleInit(self, server, my, opp, data):
        sendData = dict([('state', 'Init'), ('name', str(opp.name)), ('nickName',str(opp.nickName)), ('streetAddress',str(opp.streetAddress)), ('startTime', str(random.uniform(4,10)))])
        server.send_message(my.client,json.dumps(sendData,ensure_ascii=False))
        sendData['name'] = my.name
        sendData['nickName'] = my.nickName
        sendData['streetAddress'] = my.streetAddress
        server.send_message(opp.client,json.dumps(sendData,ensure_ascii=False))

    def Battle(self, client, server, data):
        if self.MemberCheck(self.GetFindMemberFromClient,client) == False:
            sendData = dict([('state', 'Error'), ('message', 'You donot join Member in Lobby')])
            server.send_message(client,json.dumps(sendData,ensure_ascii=False))
            return
        my = self.GetFindMemberFromClient(client)

        if self.MemberCheck(self.GetFindMemberFromClient,my.opp.client) == False:
            sendData = dict([('state', 'Error'), ('message', 'You donot join Member in Lobby')])
            server.send_message(client,json.dumps(sendData,ensure_ascii=False))
            return
        opp = my.opp

        time = float(data['attackTime'])
        my.time = time
        opp.opp.time = time

        sendData = dict([('state', 'Info'), ('message', 'AttackSpeed OK')])
        server.send_message(client,json.dumps(sendData,ensure_ascii=False))
        sendData = dict([('state', 'Info'), ('message', 'OppAttackSpeed OK')])
        server.send_message(my.opp.client,json.dumps(sendData,ensure_ascii=False))

        #両方とものタイムが揃ったら
        if (my.time > -1.0) and (my.opp.time > -1.0):
            my.isBattle = False
            opp.isBattle = False
            sendData2 = dict([('state', 'Battle'), ('isJudge', 'Win'), ('myTime',str(my.time)), ('oppTime',str(my.opp.time))])
            if (my.time < my.opp.time):
                sendData2['isJudge'] = 'Win'
                server.send_message(client,json.dumps(sendData2,ensure_ascii=False))
                sendData2['isJudge'] = 'Lose'
                server.send_message(my.opp.client,json.dumps(sendData2,ensure_ascii=False))
            elif (my.time > my.opp.time):
                sendData2['isJudge'] = 'Lose'
                server.send_message(client,json.dumps(sendData2,ensure_ascii=False))
                sendData2['isJudge'] = 'Win'
                server.send_message(my.opp.client,json.dumps(sendData2,ensure_ascii=False))
            elif (my.time == my.opp.time):
                sendData2['isJudge'] = 'Draw'
                server.send_message(client,json.dumps(sendData2))              
                server.send_message(my.opp.client,json.dumps(sendData2,ensure_ascii=False))

    

    def MyBattleReSet(self,client,server):
        print('MyBattleReSet')

        if self.MemberCheck(self.GetFindMemberFromClient,client) == False:
            sendData = dict([('state', 'Error'), ('message', 'You donot join Member in Lobby')])
            server.send_message(client,json.dumps(sendData,ensure_ascii=False))
            return

        my = self.GetFindMemberFromClient(client)
        my.opp = None
        my.isBattle = False
        my.time = -10.0

        sendData = dict([('state', 'Info'), ('message', 'Your battle data reset OK')])
        server.send_message(user.client,json.dumps(sendData,ensure_ascii=False))  

    def GetFindMemberFromClient(self,client):
        for value in self.Member:
            if value.client == client:
                return value
        return None

    def GetFindMemberFromOppClient(self,client):
        for value in self.Member:
            if value.opp == None:
                continue
            if value.opp.client == client:
                return value
        return None

    def GetFindMemberFromUserID(self,ID):
        for value in self.Member:
            if str(value.ID) == str(ID):
                return value
        return None

    def ErrorSend(self,client,server,code,message,isAll=False):
        sendData = dict([('state', 'Error'), ('code', str(code)), ('message', message)])
        if isAll == True:
            server.send_message_to_all(json.dumps(sendData,ensure_ascii=False))
        else:    
            server.send_message(client,json.dumps(sendData,ensure_ascii=False))
    

    def OpenChat(self, client, server, data):
        server.send_message_to_all(json.dumps(data,ensure_ascii=False))

    def DirectChat(self, client, server, data):

        if self.MemberCheck(self.GetFindMemberFromClient,client) == False:
            sendData = dict([('state', 'Error'), ('message', 'You donot join Member in Lobby')])
            server.send_message(client,json.dumps(sendData,ensure_ascii=False))
            return

        if self.MemberCheck(self.GetFindMemberFromUserID,data['oppID']) == False:
            sendData = dict([('state', 'Error'), ('message', 'Opponent donot join Member in Lobby')])
            server.send_message(client,json.dumps(sendData,ensure_ascii=False))
            return

        my = self.GetFindMemberFromClient(client)
        opp = self.GetFindMemberFromUserID(data['oppID'])

        sendData = dict([('state', 'DirectChat'),('oppID', my.ID),('oppName', my.name),('text', data['text'])])

        server.send_message(opp.client,json.dumps(sendData,ensure_ascii=False))
