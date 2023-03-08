import random
import threading
from collections import deque
import socket
from structures import *
from db_utils import load_info, is_user_in_db, add_new_to_db, get_current_id, update_id_table, update_user_info
from SQLDataBase import SQLDataBase
from server_files_normal.game.settings import *
from encryption import *
from _struct import unpack, pack

PORT = 12402
PROTOCOL_LEN = 2
DATA_MAX_LENGTH = 510
id_socket_dict = {}
DH_normal_keys = {}
server_serverSocket_dict = {}

DH_p = 129580882928432529101537842147269734269461392429415268045151341409571915390240545252786047823626355003667141296663918972102908481139133511887035351545132033655663683090166304802438003459450977581889646160951156933194756978255460848171968985564238788467016810538221614304187340780075305032745815204247560364281
DH_g = 119475692254216920066132241696136552167987712858139173729861721592048057547464063002529177743099212305134089294733874076960807769722388944847002937915383340517574084979135586810183464775095834581566522721036079400681459953414957269562943460288437613755140572753576980521074966372619062067471488360595813421462

server_indices = [i for i in range(4)]

def login_main(sock_to_normals: socket.socket, new_players_q: deque[PlayerCentral], LB_to_login_q: deque[LB_to_login_msg], db: SQLDataBase) -> None:
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', PORT))

    threads = []

    look_for_new_clients_Thread = threading.Thread(target=look_for_new, args=(new_players_q, db, sock))
    threads.append(look_for_new_clients_Thread)

    send_server_ip_to_client_Thread = threading.Thread(target=send_server_ip_to_client, args=(db, LB_to_login_q, sock_to_normals))
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
    DH_normal_keys[server] = pow(int.from_bytes(y, 'little'), a, DH_p).to_bytes(128, 'little')

def initialize_conn_with_normals(sock_to_normals: socket.socket):
    amount_connected = 0
    while amount_connected < 4:
        normal_sock, addr = sock_to_normals.accept()
        server = Server(addr[0], addr[1])
        if server not in NORMAL_SERVERS:
            normal_sock.close()
            continue

        normal_sock.settimeout(0.02)
        server_serverSocket_dict[server] = normal_sock
        DH_with_normal(normal_sock, server)

        amount_connected += 1

def look_for_new(new_players_q: deque[PlayerCentral], db: SQLDataBase, sock: socket.socket) -> None:
    sock.listen()
    while True:
        client_sock, addr = sock.accept()
        length = unpack("<H", sock.recv(PROTOCOL_LEN))[0]
        data = client_sock.recv(length).decode()
        username = data.split(" ")[0]
        password = hash_and_salt(data.split(" ")[1])
        if not is_user_in_db(db, username):
            new_id = get_current_id(db) + 1
            add_new_to_db(db, new_id, username, password)
            update_id_table(db)
            list_user_info = load_info(db, username)
        else:
            list_user_info = load_info(db, username)
            if not list_user_info[0][2] == password:
                client_sock.send("incorrect password".encode())
                client_sock.close()
                continue

        info_tuple = list_user_info[0]
        id_socket_dict[info_tuple[0]] = client_sock
        new_players_q.append(PlayerCentral(pos=Point(info_tuple[3], info_tuple[4]), player_id=info_tuple[0]))

def send_server_ip_to_client(db: SQLDataBase, LB_to_login_q: deque[LB_to_login_msg]) -> None:
    msg: LB_to_login_msg = LB_to_login_q.pop()
    info_to_normals = InfoData(info=load_info(db, msg.client_id)[0])  # Tuple of the info
    client_id_bytes = msg.client_id.to_bytes(6, 'little')

    server_serverSocket_dict[msg.server].send(InfoMsgToNormal(encrypted_id=encrypt(client_id_bytes, DH_normal_keys[msg.server]), info=info_to_normals.serialize()).serialize())

    client_sock: socket.socket = id_socket_dict[msg.client_id]
    resp_to_client: LoginResponseToClient = LoginResponseToClient(encrypted_id=encrypt(client_id_bytes, DH_normal_keys[msg.server]), server=ServerSer(server=msg.server))
    resp_to_client_bytes = resp_to_client.serialize()
    client_sock.send(pack("<H", len(resp_to_client_bytes)))
    client_sock.send(resp_to_client_bytes)

def handle_disconnect(db: SQLDataBase):
    for server in server_serverSocket_dict:
        normal_sock: socket.socket = server_serverSocket_dict[server]
        try:
            size = unpack('<H',normal_sock.recv(2))[0]
        except socket.timeout:
            continue

        player_data = PlayerData(ser=decrypt(normal_sock.recv(size), DH_normal_keys[server]))
        update_user_info(db, player_data)


#TODO chat
