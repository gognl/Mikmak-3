import random
import threading
import time
from collections import deque
import socket
from central_server_files.structures import *
from central_server_files.db_utils import load_info_by_id, is_user_in_db, add_new_to_db, get_current_id, update_id_table, update_user_info, load_player_data, get_id_by_name
from central_server_files.SQLDataBase import SQLDataBase
from server_files_normal.game.settings import *
from central_server_files.encryption import *
from _struct import unpack, pack
from central_server_files.Constant import MAX_ENTITY_ID_SIZE, DH_p, DH_g, LOGIN_PORT_TO_CLIENT
from base64 import urlsafe_b64encode as b64

PROTOCOL_LEN = 2
DATA_MAX_LENGTH = 510
id_socket_dict = {}
DH_normal_keys = {}
server_serverSocket_dict = {}
active_players_id: list[int] = []

server_indices = [i for i in range(4)]

def login_main(new_players_q: deque[PlayerCentral], LB_to_login_q: deque[LB_to_login_msg], db: SQLDataBase) -> None:
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', LOGIN_PORT_TO_CLIENT))

    threads = []

    look_for_new_clients_Thread = threading.Thread(target=look_for_new, args=(new_players_q, db, sock))
    threads.append(look_for_new_clients_Thread)

    send_server_ip_to_client_Thread = threading.Thread(target=send_server_ip_to_client, args=(db, LB_to_login_q))
    threads.append(send_server_ip_to_client_Thread)

    handle_disconnect_Thread = threading.Thread(target=handle_disconnect, args=(db,))
    threads.append(handle_disconnect_Thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

def DH_with_normal(normal_sock: socket.socket, server: Server):
    a = random.randrange(DH_p)
    x = pow(DH_g, a, DH_p)
    normal_sock.send(x.to_bytes(128, 'little'))
    y = normal_sock.recv(1024)
    DH_normal_keys[server] = b64(pow(int.from_bytes(y, 'little'), a, DH_p).to_bytes(128, 'little'))

def find_normal_server(ip: str):
    for server in NORMAL_SERVERS:
        if server.ip == ip:
            return server
    return None

def initialize_conn_with_normals(sock_to_normals: socket.socket):
    amount_connected = 0
    while amount_connected < 2:
        normal_sock, addr = sock_to_normals.accept()
        port = int.from_bytes(normal_sock.recv(2), 'little')
        server = Server(addr[0], port)
        if server not in NORMAL_SERVERS_FOR_CLIENT:
            normal_sock.close()
            continue

        server_serverSocket_dict[server] = normal_sock

        DH_with_normal(normal_sock, server)
        normal_sock.settimeout(0.02)

        amount_connected += 1
    print("The servers are ready! (Login)")

def look_for_new(new_players_q: deque[PlayerCentral], db: SQLDataBase, sock: socket.socket) -> None:
    sock.listen()
    while True:
        client_sock, addr = sock.accept()
        length = unpack("<H", client_sock.recv(PROTOCOL_LEN))[0]
        data = client_sock.recv(length).decode()
        username = data.split(" ")[0]
        password = data.split(" ")[1]
        if not is_user_in_db(db, username):
            new_id = get_current_id(db) + 1
            add_new_to_db(db, new_id, username, password)
            update_id_table(db)
            list_user_info = load_info_by_id(db, new_id)
        else:
            new_id = get_id_by_name(db, username)
            list_user_info = load_info_by_id(db, new_id)

            if list_user_info[0][2] != password or new_id in active_players_id:
                x = 0
                error_code = x.to_bytes(2, 'little')
                client_sock.send(error_code)
                client_sock.close()
                continue

        info_tuple = list_user_info[0]
        active_players_id.append(new_id)
        id_socket_dict[info_tuple[0]] = client_sock
        new_players_q.append(PlayerCentral(pos=Point(info_tuple[3], info_tuple[4]), player_id=info_tuple[0]))

next_item_id: int = 4*AMOUNT_ITEMS_PER_SERVER+50

def send_server_ip_to_client(db: SQLDataBase, LB_to_login_q: deque[LB_to_login_msg]):
    while True:
        if len(LB_to_login_q) == 0:
            continue
        msg: LB_to_login_msg = LB_to_login_q.pop()
        info_data = InfoData(info=load_player_data(db, msg.client_id))  # list of the info
        client_id_bytes = msg.client_id.to_bytes(6, 'little')
        encrypted_package_info = encrypt(InfoMsgToNormal(client_id=msg.client_id, info_list=info_data).serialize(), DH_normal_keys[msg.server])
        size = pack("<H", len(encrypted_package_info))

        server_serverSocket_dict[msg.server].send(size)
        server_serverSocket_dict[msg.server].send(encrypted_package_info)

        client_sock: socket.socket = id_socket_dict[msg.client_id]
        inventory_from_info: dict[str, int] = info_data.info[6]
        inventory: dict[str, tuple[list[int], int]] = {}
        global next_item_id
        for item_name, item_count in inventory_from_info.items():
            inventory[item_name] = ([next_item_id+i for i in range(item_count)], item_count)
            next_item_id += item_count

        data_to_client = DataToClient(pos_x=info_data.info[0], pos_y=info_data.info[1], health=info_data.info[2],
                                      strength=info_data.info[3], resistance=info_data.info[4], xp=info_data.info[5], inventory=inventory)
        resp_to_client: LoginResponseToClient = LoginResponseToClient(encrypted_id=encrypt(client_id_bytes, DH_normal_keys[msg.server]), server=ServerSer(ip=msg.server.ip, port=msg.server.port),
                                                                      data_to_client=data_to_client)
        resp_to_client_bytes = resp_to_client.serialize()

        def func():
            time.sleep(0.3)
            client_sock.send(pack("<H", len(resp_to_client_bytes)))
            client_sock.send(resp_to_client_bytes)

        threading.Thread(target=func).start()


def get_msg_from_timeout_socket(sock: socket.socket, size: int):
    while True:
        try:
            data = sock.recv(size)
            return data
        except socket.timeout:
            continue

def handle_disconnect(db: SQLDataBase):
    while True:
        for server in server_serverSocket_dict:
            normal_sock: socket.socket = server_serverSocket_dict[server]

            try:
                size = unpack('<H', normal_sock.recv(2))[0]
            except socket.timeout:
                continue

            player_data = PlayerData(ser=decrypt(get_msg_from_timeout_socket(normal_sock, size), DH_normal_keys[server]))
            print(player_data)

            disconnected_client_sock = id_socket_dict[player_data.entity_id]
            disconnected_client_sock.close()
            active_players_id.remove(player_data.entity_id)
            update_user_info(db, player_data)
