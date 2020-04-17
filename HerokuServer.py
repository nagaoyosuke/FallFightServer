import logging
import psycopg2
import os
import json
import random

import socket
import threading

from bottle import route, run
# from LobbyBase import LobbyBase

bind_ip = "https://fallfightserver.herokuapp.com" 
bind_port = int(os.getenv("PORT", 5000)) 

# Lobby = LobbyBase(16)
# thread processing a task from clients
def on_message(client_socket,addr):
    while True:
        try:
            request = client_socket.recv(1024)
            # print data (max buffer size 1024) sent from client
            print ("Received: %s" % request)
            # send a message "Ack" to client
            client_socket.send(request)

            # data = json.loads(request)

            # print(data['state'])
            # print(data)

            # if data['state'] == 'Init':
            #     sendData = InitMessage(data)
            # elif data['state'] == 'Login':
            #     Lobby.Login(client_socket,addr[0],addr[1],data)
            # elif data['state'] == 'MemberList':
            #     Lobby.LobbyMemberList(client_socket,data)
            # elif data['state'] == 'OpenChat':
            #     Lobby.OpenChat(client_socket,data)
            # elif data['state'] == 'DirectChat':
            #     Lobby.DirectChat(client_socket,data)    
        except socket.error:
            print("Lost")
            client_socket.close()
            break
        except Exception as e:
            print("err")
            print(e)
            client_socket.close()
            continue
    # client_socket.close()

@route('/')
def hello():
    print("hello")
    return ""

# Main
if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((socket.gethostname(), bind_port))
    server.listen(5)  
    print ("Listening on %s: %d" % (bind_ip, bind_port))
    while True:
        # event: a conncetion from client
        client, addr = server.accept()
        print ("Accepted connection from %s: %d" % (addr[0], addr[1]))
        #接続してきたやつの受信待機用に個別にスレッドを作成
        message = threading.Thread(target=on_message, args=(client,addr,))
        message.start()