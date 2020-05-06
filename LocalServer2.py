#ローカル用


import logging
import os
import json
import random
import psycopg2

import socket
import threading

from bottle import route, run
from LobbyBase import LobbyBase

# from LobbyBase import LobbyBase

# bind_ip = "127.0.0.1" #お使いのサーバーのホスト名を入れます
# bind_port = 12345 #クライアントで設定したPORTと同じもの指定してあげます

bind_ip = "0.0.0.0" #お使いのサーバーのホスト名を入れます
bind_port = int(os.getenv("PORT", 5000)) 

Lobby = LobbyBase(16)

def CreateServer():
    with socket.create_server((bind_ip,bind_port), family=socket.AF_INET, dualstack_ipv6=False) as server:
        # create socket object
        # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server = socket.create_server((bind_ip,bind_port), family=socket.AF_INET6, dualstack_ipv6=True)
        # bind ip + port as a server 
        # server.bind((bind_ip, bind_port))
        # listen with maximum 5 waiting queues
        server.listen(5)  ### server while loop
        print ("Listening on %s: %d" % (bind_ip, bind_port))
        while True:
            # event: a conncetion from client
            client, addr = server.accept()
            print ("Accepted connection from %s: %d" % (addr[0], addr[1]))
            #接続してきたやつの受信待機用に個別にスレッドを作成
            message = threading.Thread(target=on_message, args=(client,addr,))
            message.start()

# thread processing a task from clients
def on_message(client_socket,addr):
    while True:
        try:
            request = client_socket.recv(1024)
             # 切断された
            if len(request) == 0:
                break
            # print data (max buffer size 1024) sent from client
            print ("Received: %s" % request)
            print(client_socket.proto)
            # send a message "Ack" to client
            # client_socket.send("Ack!, connecting..".encode('utf_8'))

            data = json.loads(request)

            print(data['state'])
            print(data)

            if data['state'] == 'Init':
                sendData = InitMessage(data)
            elif data['state'] == 'Login':
                Lobby.Login(client_socket,addr[0],addr[1],data)
            elif data['state'] == 'MemberList':
                Lobby.LobbyMemberList(client_socket,data)
            elif data['state'] == 'OpenChat':
                Lobby.OpenChat(client_socket,data)
            elif data['state'] == 'DirectChat':
                Lobby.DirectChat(client_socket,data)    
        except socket.error:
            print("Lost")
            break
        except ConnectionResetError:
            print("close conenection")
            break
        except json.decoder.JSONDecodeError:
            print("not json")
            continue
        except Exception as e:
            print(e)
            continue
    # client_socket.close()

@route('/')
def hello():
    print("hello")
    return ""

# Main
if __name__ == "__main__":
    CreateServer()