import threading
from collections import deque
import socket
from structures import *
from db_utils import load_info, is_user_in_db, add_new_to_db
from SQLDataBase import SQLDataBase

PORT = 12402
PROTOCOL_LEN = 1
DATA_MAX_LENGTH = 510
id_socket_dict = {}
Id = 0  # to change!!!!


def login_main(new_players_q: deque[PlayerCentral], msgs_to_clients_q: deque[MsgToClient], db: SQLDataBase) -> None:
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', PORT))
    threads = []

    look_for_new_clients_Thread = threading.Thread(target=look_for_new, args=(new_players_q, db, sock))
    threads.append(look_for_new_clients_Thread)

    send_server_ip_to_client_Thread = threading.Thread(target=send_server_ip_to_client, args=msgs_to_clients_q)
    threads.append(send_server_ip_to_client_Thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def look_for_new(new_players_q: deque[PlayerCentral], db: SQLDataBase, sock: socket.socket) -> None:
    sock.listen()
    while True:
        client_sock, addr = sock.accept()
        length = sock.recv(PROTOCOL_LEN).decode()
        data = sock.recv(int(length)).decode()
        username = data.split(" ")[0]
        password = data.split(" ")[1]
        if not is_user_in_db(db, username):
            add_new_to_db(db, Id, username, password)
            list_user_info = load_info(db, username)
        else:
            list_user_info = load_info(db, username)

        info_tuple = list_user_info[0]
        id_socket_dict[info_tuple[0]] = client_sock
        new_players_q.append(PlayerCentral(Point(info_tuple[3], info_tuple[4]), info_tuple[0]))


def send_server_ip_to_client(msgs_to_client_q: deque[MsgToClient]) -> None:
    msg_to_client = msgs_to_client_q.pop()
    client_dest_sock: socket.socket = id_socket_dict.get(msg_to_client.dest_id)
    client_dest_sock.send(msg_to_client.msg)
