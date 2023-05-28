import random
import struct
import threading
from threading import Lock
import time
from collections import deque
import socket
from central_server_files.structures import *
from central_server_files.db_utils import load_info_by_id, is_user_in_db, add_new_to_db, get_current_id, update_id_table, update_user_info, load_player_data, get_id_by_name
from central_server_files.SQLDataBase import SQLDataBase
from central_server_files.Constant import *
from central_server_files.encryption import *
from _struct import unpack, pack
from central_server_files.Constant import DH_p, DH_g, LOGIN_PORT_TO_CLIENT

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

    get_msgs_from_normal_sockets_Thread = threading.Thread(target=get_msgs_from_normal_sockets, args=(db,))
    threads.append(get_msgs_from_normal_sockets_Thread)

    chat_lock = Lock()
    handle_chat_Thread = threading.Thread(target=handle_chat_msgs, args=(chat_lock,))
    threads.append(handle_chat_Thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

def DH_with_normal(normal_sock: socket.socket, server: Server):
    a = random.randrange(DH_p)
    x = pow(DH_g, a, DH_p)
    normal_sock.send(x.to_bytes(128, 'little'))
    y = normal_sock.recv(1024)
    DH_normal_keys[server] = pow(int.from_bytes(y, 'little'), a, DH_p).to_bytes(128, 'little')

amount_connected = 0
def initialize_conn_with_normals(sock_to_normals: socket.socket):
    global amount_connected
    threads = []
    while amount_connected < 4:
        normal_sock, addr = sock_to_normals.accept()
        ip, port = ServerSer(ser=normal_sock.recv(100)).addr()
        server = Server(ip, port)

        if server not in NORMAL_SERVERS_FOR_CLIENT:
            normal_sock.close()
            continue

        server_serverSocket_dict[server] = normal_sock

        def do_DH():
            global amount_connected
            DH_with_normal(normal_sock, server)

        thread = threading.Thread(target=do_DH)
        threads.append(thread)
        thread.start()

        amount_connected += 1

    for thread in threads:
        thread.join()

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
        client_sock.settimeout(0.05)
        id_socket_dict[info_tuple[0]] = client_sock
        new_players_q.append(PlayerCentral(pos=Point(info_tuple[3], info_tuple[4]), player_id=info_tuple[0]))

next_item_id: int = 4*AMOUNT_ITEMS_PER_SERVER+50
clients_can_send = set()

def send_server_ip_to_client(db: SQLDataBase, LB_to_login_q: deque[LB_to_login_msg]):
    while True:
        if len(LB_to_login_q) == 0:
            continue
        msg: LB_to_login_msg = LB_to_login_q.pop()
        info_data = InfoData(info=load_player_data(db, msg.client_id))  # list of the info
        client_id_bytes = msg.client_id.to_bytes(6, 'little')

        inventory_from_info: dict[str, int] = info_data.info[6]
        inventory: dict[str, tuple[list[int], int]] = {}
        global next_item_id
        item_ids = []
        for item_name, item_count in inventory_from_info.items():
            current_item_ids = [next_item_id+i for i in range(item_count)]
            item_ids.extend(current_item_ids)
            inventory[item_name] = (current_item_ids, item_count)
            next_item_id += item_count

        encrypted_package_info = encrypt(InfoMsgToNormal(client_id=msg.client_id, info_list=info_data, item_ids=item_ids).serialize(), DH_normal_keys[msg.server])
        size = pack("<H", len(encrypted_package_info))

        server_serverSocket_dict[msg.server].send(size)
        server_serverSocket_dict[msg.server].send(encrypted_package_info)

        client_sock: socket.socket = id_socket_dict[msg.client_id]


        data_to_client = DataToClient(pos_x=info_data.info[0], pos_y=info_data.info[1], health=info_data.info[2],
                                      strength=info_data.info[3], resistance=info_data.info[4], xp=info_data.info[5], inventory=inventory)
        resp_to_client: LoginResponseToClient = LoginResponseToClient(encrypted_id=encrypt(client_id_bytes, DH_normal_keys[msg.server]), server=ServerSer(ip=msg.server.ip, port=msg.server.port),
                                                                      data_to_client=data_to_client)

        def func():
            while client_id_bytes not in clients_can_send:
                pass

            resp_to_client_bytes = resp_to_client.serialize()
            client_sock.send(pack("<H", len(resp_to_client_bytes)))
            client_sock.send(resp_to_client_bytes)

            try:
                clients_can_send.remove(client_id_bytes)
            except Exception:
                pass

        threading.Thread(target=func).start()


def get_msg_from_timeout_socket(sock: socket.socket, size: int):
    while True:
        try:
            data = sock.recv(size)
            return data
        except socket.timeout:
            continue

def get_msgs_from_normal_sockets(db: SQLDataBase):
    for server in server_serverSocket_dict:
        normal_sock: socket.socket = server_serverSocket_dict[server]
        normal_sock.settimeout(0.02)
    while True:
        for server in server_serverSocket_dict:
            normal_sock: socket.socket = server_serverSocket_dict[server]
            try:
                pref = normal_sock.recv(1)
                if pref == b'1':
                    client_id_bytes = decrypt(normal_sock.recv(1024), DH_normal_keys[server])
                    clients_can_send.add(client_id_bytes)
                else:
                    size = unpack('<H', normal_sock.recv(2))[0]
                    player_data = PlayerData(
                        ser=decrypt(get_msg_from_timeout_socket(normal_sock, size), DH_normal_keys[server]))
                    handle_disconnect(db, player_data)

            except socket.timeout:
                continue

def handle_disconnect(db: SQLDataBase, player_data: PlayerData):
    disconnected_client_sock = id_socket_dict[player_data.entity_id]
    disconnected_client_sock.close()
    active_players_id.remove(player_data.entity_id)
    update_user_info(db, player_data)
    update_user_info(db, player_data)


def handle_chat_msgs(chat_lock: Lock):
    while True:
        with chat_lock:
            dict_copy = dict(id_socket_dict)
            for client_id in dict_copy:
                client_sock: socket.socket = dict_copy[client_id]

                try:
                    size = unpack('<H', client_sock.recv(2))[0]
                except (socket.timeout, struct.error):
                    continue
                except OSError:
                    continue

                ser = get_msg_from_timeout_socket(client_sock, size)
                msgs_lst = ChatMsgsLst(ser=ser)
                if(msgs_lst.serialize() != ser):
                    print("problem")

                for id2 in dict_copy:
                    if client_id == id2:
                        continue
                    client_sock2 = dict_copy[id2]
                    try:
                        client_sock2.send(pack('<H', len(ser)))
                        client_sock2.send(ser)
                    except OSError:
                        continue
                    #size2 = pack('<H', len(msgs_lst.serialize()))
                    #if size2 == size:
                    #    client_sock2.send(size2)
                    #    client_sock2.send(msgs_lst.serialize())
                    #else:
                    #    print('problem')


