import socket
import threading
import time
from collections import deque
from structures import *
from server_files_normal.game.settings import *

center = Point(MAP_WIDTH//2, MAP_HEIGHT//2)
players: dict[ID, PlayerCentral] = {}
normal_sockets: dict[Server, socket.socket] = {}


def initialize_conn_with_normals(sock_to_normals: socket.socket):
	amount_connected = 0
	while amount_connected < 4:
		normal_sock, addr = sock_to_normals.accept()
		server = Server(addr[0], addr[1])
		if server not in NORMAL_SERVERS:
			normal_sock.close()
			continue

		normal_sock.settimeout(0.02)

		normal_sockets[server] = normal_sock

		amount_connected += 1


def send_center_update_to_normals():
	while True:
		new_center: Point = get_new_center(players.copy())
		for server in normal_sockets:
			normal_sock: socket.socket = normal_sockets[server]
			normal_sock.send(new_center.serialize())

		global center
		center = new_center

		time.sleep(3)


def get_new_center(players: dict[ID, PlayerCentral]):
	if len(players) == 0:
		return Point(MAP_WIDTH//2, MAP_HEIGHT//2)

	avg = Point(0, 0)
	for key in players:
		avg.add(players[key].pos)
	avg.div(len(players))

	return avg

def find_suitable_server_index(player: PlayerCentral) -> int:
	b0 = player.pos.x > center.x
	b1 = player.pos.y > center.y
	return 2*b1+b0

def look_for_new_client(new_players_q: deque[PlayerCentral], LB_to_login_q: deque[LB_to_login_msg]):
	while True:
		if len(new_players_q) == 0:
			continue
		new_player: PlayerCentral = new_players_q.pop()
		suitable_server = NORMAL_SERVERS[find_suitable_server_index(new_player)]
		msg: LB_to_login_msg = LB_to_login_msg(new_player.id, suitable_server)
		LB_to_login_q.append(msg)


def get_server(ip: str, port: int, servers: list[Server]):
	for server in servers:
		if server.ip == ip and server.port == port:
			return server
	return None


def recv_from_normals():
	for server in normal_sockets:
		normal_sock: socket.socket = normal_sockets[server]

		try:
			data = normal_sock.recv(1024)
		except socket.timeout:
			continue

		players_list = PlayerCentralList(ser=data)
		for player in players_list.players:
			players[player.id] = player


def LB_main(new_players_q: deque[PlayerCentral], LB_to_login_q: deque[LB_to_login_msg]):
	threads: list[threading.Thread] = []

	look_for_new_client_Thread = threading.Thread(target=look_for_new_client, args=(new_players_q, LB_to_login_q))
	threads.append(look_for_new_client_Thread)

	recv_from_normals_Thread = threading.Thread(target=recv_from_normals)
	threads.append(recv_from_normals_Thread)

	send_center_update_to_normals_Thread = threading.Thread(target=send_center_update_to_normals)
	threads.append(send_center_update_to_normals_Thread)

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()
