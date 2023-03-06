import socket
import threading
from collections import deque
from server_files_normal.game.settings import *
import LB
import login
from structures import *

CONN_NORMALS_PORT = CENTRAL_SERVER.port

def main():
	new_players_q: deque[PlayerCentral] = deque()
	LB_to_login_q: deque[LB_to_login_msg] = deque()
	login_sock_to_normals: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	login_sock_to_normals.bind(('0.0.0.0', CONN_NORMALS_PORT))
	login_sock_to_normals.listen()

	threads: list[threading.Thread] = []

	Initialized_connection_login_Thread = threading.Thread(target=login.initialize_conn_with_normal, args=(login_sock_to_normals,))
	Initialized_connection_login_Thread.start()
	Initialized_connection_login_Thread.join()

	LB_Thread = threading.Thread(target=LB.LB_main, args=(new_players_q, LB_to_login_q))
	threads.append(LB_Thread)

	login_Thread = threading.Thread(target=login.login_main, args=(login_sock_to_normals, new_players_q, LB_to_login_q))
	threads.append(login_Thread)

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()


if __name__ == '__main__':
	main()
