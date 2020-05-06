import logging
# import psycopg2
import os
import json
import random
from MemberBase import MemberBase
# 対戦する部屋
class RoomBase:

    def __init__(self,ID,name,maxUser,createdUser):
        self.ID = ID
        self.name = name
        self.maxUser = maxUser
        self.Member = []
        self.createdUser = createdUser

    def JoinMember(self,member):
        print('Join' + 'ID:' + member.ID + ' name:' + member.name)
        self.Member.append(member)

    def ExitMember(self,member):
        print('Exit' + 'ID:' + member.ID + ' name:' + member.name)
        self.Member.remove(member)