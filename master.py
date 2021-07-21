import socket
import subprocess
from _thread import *
from datetime import datetime
import configparser


def get_number_of_active_node(node_ip_map):
    result = 0
    active_node = {}
    for key, value in node_ip_map.items():
        res = 1
        try:
            param = '-c'
            command = ['ping', param, '1', value]
            res = subprocess.call(command)
        except:
            pass
        if res == 0:
            result += 1
            active_node[key] = value
    return result, active_node


def find_preffered_node(active_node, hash_value):
    tmp = sorted(active_node.keys())
    for i in range(len(tmp) - 1):
        if tmp[i] <= hash_value < tmp[i + 1]:
            return tmp[i]
    return tmp[-1]


def threaded_client(conn):
    try:
        parser = configparser.ConfigParser()
        PORT = 65432
        while True:
            try:
                parser.read('config.cfg')
                node_ip_map = dict(parser.items("DATABASE-NODE-IP"))
                consistent_hash_key = []
                [consistent_hash_key.append(i) for i in range(100, 999, (999 - 100 + 1) // 3)]
                node_ip_mapping = {}
                for c_hash_key, ip in zip(consistent_hash_key[0:len(node_ip_map)], node_ip_map.values()):
                    node_ip_mapping[c_hash_key] = ip

                data = conn.recv(2048)
                key = data.decode().split()[1]
                print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "++ FROM CLIENT: ", data)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
                    d_hash = int(str(hash(key))[-3::])

                    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "++ CHECKING ACTIVE DATABASE NODES", "+" * 50)
                    number_of_active_node, active_node = get_number_of_active_node(node_ip_mapping)
                    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "-- NUMBER OF ACTIVE DATABASE NODES",
                          number_of_active_node, "+" * 50)
                    if number_of_active_node == 0:
                        response = "All Database Nodes Down".encode()
                    else:
                        preffered_node = find_preffered_node(active_node, d_hash)
                        # print("_*_"*10, preffered_node, active_node, d_hash, active_node[preffered_node], PORT)
                        # s1.connect((active_node[preffered_node], PORT))
                        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "++ CONNECTED TO NODE:", preffered_node,
                              active_node[preffered_node], key)
                        s1.sendall(data)
                        response = s1.recv(1024)
                    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "++ FROM DATABASE: ", response)
            except Exception as e:
                response = "Incomplete Query or Internal Error: {}".format(e).encode()
            conn.sendall(response)
    except KeyboardInterrupt:
        conn.close()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ServerSocket:
    host = socket.gethostname()
    port = 65431
    ThreadCount = 0
    ServerSocket.bind((host, port))
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '++ WAITING FOR CONNECTIONS')
    ServerSocket.listen()

    while True:
        Client, address = ServerSocket.accept()
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '++ CONNECTED TO: ' + address[0] + ':' + str(address[1]))
        start_new_thread(threaded_client, (Client,))
        ThreadCount += 1
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '++ THREAD NUMBER: ' + str(ThreadCount))
