import socket
import threading
from collections import deque
from central_server_files.Constant import *
import central_server_files.LB as LB
import central_server_files.login as login
from central_server_files.structures import *
from central_server_files.SQLDataBase import SQLDataBase


def main():
	new_ffsdgs_q: deque[PlayerCentral] = deque()
	LB_to_login_q: deque[LB_to_login_msg] = deque()

	login_sock_to_normals: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	login_sock_to_normals.bind(('0.0.0.0', LOGIN_SERVER.port))
	login_sock_to_normals.listen()

	LB_sock_to_normals: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	LB_sock_to_normals.bind(('0.0.0.0', LB_SERVER.port))
	LB_sock_to_normals.listen()

	threads: list[threading.Thread] = []


	Initialized_connection_threads = []

	Initialized_connection_login_Thread = threading.Thread(target=login.initialize_conn_with_normals, args=(login_sock_to_normals,))
	Initialized_connection_threads.append(Initialized_connection_login_Thread)

	Initialized_connection_LB_Thread = threading.Thread(target=LB.initialize_conn_with_normals, args=(LB_sock_to_normals,))
	Initialized_connection_threads.append(Initialized_connection_LB_Thread)

	for thread in Initialized_connection_threads:
		thread.start()

	for thread in Initialized_connection_threads:
		thread.join()


	LB_Thread = threading.Thread(target=LB.LB_main, args=(new_ffsdgs_q, LB_to_login_q))
	threads.append(LB_Thread)

	login_Thread = threading.Thread(target=login.login_main, args=(new_ffsdgs_q, LB_to_login_q, SQLDataBase(DB_HOST, DB_PASSWORD)))
	threads.append(login_Thread)

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()


if __name__ == '__main__':
	main()
