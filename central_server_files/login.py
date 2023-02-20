from collections import deque
import socket
from structures import *
from db_utils import load_info, is_user_in_db, add_new_to_db
from SQLDataBase import SQLDataBase

PORT = 12402
PROTOCOL_LEN = 1
DATA_MAX_LENGTH = 510
id_port_dict = {}
id = 0  # to change!!!!

def login_main(new_players_q: deque[PlayerCentral], msgs_to_clients_q: deque[MsgToClient], db: SQLDataBase):
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', PORT))

def look_for_new(new_players_q: deque[PlayerCentral], db: SQLDataBase, sock: socket.socket) -> None:
    sock.listen()
    while True:
        client_sock, addr = sock.accept()
        length = sock.recv(PROTOCOL_LEN).decode()
        data = sock.recv(int(length)).decode()
        username = data.split(" ")[0]
        password = data.split(" ")[1]
        if not is_user_in_db(db, username):
            add_new_to_db(db, id, username, password)
        else:
            list_user_info = load_info(db, username)
