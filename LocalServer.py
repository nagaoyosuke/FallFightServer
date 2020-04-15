#ローカル用


import logging
import psycopg2
import os
import json
import random

from websocket_server import WebsocketServer
 
from bottle import route, run

from LobbyBase import LobbyBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(' %(module)s -  %(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
 
# Callback functions
Lobby = LobbyBase(16)

 #新しいクライアントが接続
def new_client(client, server):
    logger.info('New client {}:{} has joined.'.format(client['address'][0], client['address'][1]))
    server.clients[-1]['name'] = (str(client['id']))
    sendData = dict([('state', 'Info'), ('message', server.clients[-1]['name'] + "が入室しました")])
    server.send_message_to_all(json.dumps(sendData,ensure_ascii=False))

#クライアントの接続がきれた
def client_left(client, server):
    logger.info('Client {}:{} has left.'.format(client['address'][0], client['address'][1]))
    # server.send_message_to_all(str(getNickNameFromID(server,client['id'])) + "が退出しました")
    Lobby.Logout(client,server)
    
#クライアントからメッセージを受信
def message_received(client, server, message):

    data = json.loads(message)

    print(data['state'])

    if data['state'] == 'Init':
        sendData = InitMessage(data)
    elif data['state'] == 'Battle':
        sendData = Lobby.Battle(client,server,data)
    elif data['state'] == 'Login':
        Lobby.Login(client,server,data)
    elif data['state'] == 'Matching':
        Lobby.MatchingRequest(client,server,data)
    elif data['state'] == 'MemberList':
        Lobby.LobbyMemberList(client,server,data)
    elif data['state'] == 'MyBattleReSet':
        Lobby.MyBattleReSet(client,server,data)
    elif data['state'] == 'OpenChat':
        Lobby.OpenChat(client,server,data)
    elif data['state'] == 'DirectChat':
        Lobby.DirectChat(client,server,data)

    # sendID = getSendID(int(client['id']))
    # server.send_message(server.clients[sendID],json.dumps(sendData))

@route('/')
def hello():
    print("hello")
    return ""

# Main
if __name__ == "__main__":
    server = WebsocketServer(port=12345, host='127.0.0.1', loglevel=logging.INFO)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()