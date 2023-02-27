import threading
from collections import deque
import socket
from structures import *
from db_utils import load_info, is_user_in_db, add_new_to_db, get_current_id, update_id_table
from SQLDataBase import SQLDataBase

PORT = 12402
PROTOCOL_LEN = 1
DATA_MAX_LENGTH = 510
id_socket_dict = {}
DH_p = 129580882928432529101537842147269734269461392429415268045151341409571915390240545252786047823626355003667141296663918972102908481139133511887035351545132033655663683090166304802438003459450977581889646160951156933194756978255460848171968985564238788467016810538221614304187340780075305032745815204247560364281
DH_g = 119475692254216920066132241696136552167987712858139173729861721592048057547464063002529177743099212305134089294733874076960807769722388944847002937915383340517574084979135586810183464775095834581566522721036079400681459953414957269562943460288437613755140572753576980521074966372619062067471488360595813421462



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

def DH_with_normals():
    pass

def look_for_new(new_players_q: deque[PlayerCentral], db: SQLDataBase, sock: socket.socket) -> None:
    sock.listen()
    while True:
        client_sock, addr = sock.accept()
        length = sock.recv(PROTOCOL_LEN).decode()
        data = sock.recv(int(length)).decode()
        username = data.split(" ")[0]
        password = data.split(" ")[1]
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
        new_players_q.append(PlayerCentral(Point(info_tuple[3], info_tuple[4]), info_tuple[0]))


def send_server_ip_to_client(msgs_to_client_q: deque[MsgToClient]) -> None:
    msg_to_client = msgs_to_client_q.pop()
    client_dest_sock: socket.socket = id_socket_dict.get(msg_to_client.dest_id)
    client_dest_sock.send(msg_to_client.msg)
