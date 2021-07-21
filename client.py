#!/usr/bin/env python3
import socket

HOST = '172.17.0.5'  # The server's hostname or IP address
PORT = 65431        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        query = input("unacademy[aman.db]>> ")
        s.sendall(query.encode())
        data = s.recv(1024)
        print(data.decode())
