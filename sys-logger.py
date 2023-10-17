import socket
import requests

HOST = '0.0.0.0'
PORT = 514
url1 = "http://192.168.200.230:8000/alert/"
#with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.gethostname) as s:
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print(f"{HOST} Listening on port {PORT}")

    while True:
        data1 = s.recv(1024)
        #data1 = s.recv(min(MSGLEN - bytes_recd, 2048))
        requests.post(url = url1, data = data1)
        print(data1)
        if not data1:
            break