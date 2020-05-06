import logging
# import psycopg2
import os
import json
import random

import socket
import threading

from bottle import route, run


from LobbyBase import LobbyBase

Lobby = LobbyBase(16)

def CreateServer():
    # bind_ip = socket.gethostname() #お使いのサーバーのホスト名を入れます
    # bind_ip = "34.82.63.106" #お使いのサーバーのホスト名を入れます
    bind_ip = "0.0.0.0" #お使いのサーバーのホスト名を入れます
    bind_port = int(os.getenv("PORT", 5000)) 
    # bind_port = 8081 

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


def on_message(client_socket,addr):
    while True:
        try:
            request = client_socket.recv(1024)
             # 切断された
            if len(request) == 0:
                Lobby.Logout(client_socket)
                client_socket.close()
                break
            # print data (max buffer size 1024) sent from client
            print ("Received: %s" % request)
            print(client_socket.proto)
            # send a message "Ack" to client
            # client_socket.send("Ack!, connecting..".encode('utf_8'))

            data = json.loads(request)

            print(data['state'])
            print(data)

            client_socket.send("OK".encode('utf_8'))

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

# @route('/')
# def hello():
#     print("hello")
#     return ""

@route('/')
def hello():
    print("hello")
    return ""

# Main
if __name__ == "__main__":
    # t = threading.Thread(target=CreateServer)
    # t.daemon = True
    # t.start()
    # app.run(debug=True)
    CreateServer()