import socket
import time
from datetime import datetime

HOST = socket.gethostname()
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    database = {}
    while True:
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'Connected by:', addr)
            data = conn.recv(1024).decode().split()
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'Query Received:', data)
            try:
                cmd = data[0]
                key = data[1]
                if cmd in ("SET", "set", "Set"):
                    if database.get(key):
                        response = "Can't Override"
                    else:
                        database[key] = data[2]
                        response = "OK"
                elif cmd in ("GET", "get", "Get"):
                    response = database.get(key, "0")
                    current_time = round(time.time())
                    if isinstance(response, list):
                        ttl = response[1] - current_time
                        if ttl > 0:
                            response = "{} | {}".format(response[0], "TTL: {} seconds".format(ttl))
                        else:
                            database.pop(key)
                            response = "0"
                elif cmd in ("EXPIRE", "expire", "Expire"):
                    time_in_sec = int(data[2])
                    current_time = round(time.time())
                    value = database.get(key)
                    if value:
                        database[key] = [value, current_time + time_in_sec]
                    response = "OK"
                else:
                    response = "Querry != SET/GET/EXPIRE"
            except:
                response = "Incomplete Query"
            conn.sendall(response.encode())
