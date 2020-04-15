import socket
import threading
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 接続先
host = "127.0.0.1"
port = 12345
sock.connect((host, port));

def Handler(sock):
    while True:
        try:
            read = sock.recv(4096); #(3)
            print("読み込んだバイト数:({})".format(len(read)));
            print("<"+read.decode()+">");
            if (len(read) < 4096) :
                continue
            #end
        except Exception as e:
            continue


while (True):
    your_input = input(">>>"); #(1)
    print(sock.send(your_input.encode("UTF-8"))); #(2)
    thread = threading.Thread(target = Handler, args= (sock,), daemon= True)
    thread.start();