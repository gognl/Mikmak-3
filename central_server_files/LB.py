import math
import random
import socket
import threading
import time
from collections import deque
import pygame
from structures import *
from encryption import *
import server_files_normal.game as game

def rand(n):
	return random.randrange(n)


amount_servers = 4
PORT = 17126
W = 800  # 40960
H = 600  # 30720

normal_servers = [Server("0.0.0.0", i) for i in range(amount_servers)]
center = Point(W//2, H//2)
players = {player_id: PlayerCentral(Point(rand(W), rand(H)), player_id, '') for player_id in range(100)}
players_overlap = {}
overlapping_area_T = 10

def send(sock: socket.socket, server: Server, obj):
	sock.sendto("{obg}".encode(), server.addr())  # TODO: send the serializable form of obj

def get_new_center(players: dict[ID, PlayerCentral]):
	if len(players) == 0:
		return Point(W//2, H//2)

	avg = Point(0, 0)
	for key in players:
		avg.add(players[key].pos)
	avg.div(len(players))

	global center
	center = avg

def find_suitable_server_index(player: PlayerCentral) -> int:
	b0 = player.pos.x > center.x
	b1 = player.pos.y > center.y
	return 2*b1+b0

def look_for_new_client(new_clients_q: deque[PlayerCentral], msgs_to_clients_q: deque[MsgToClient], servers: list[Server]):
	while True:
		if len(new_clients_q) == 0:
			continue
		new_client = new_clients_q.pop()
		suitable_server = servers[find_suitable_server_index(new_client)]
		msg = MsgToClient(new_client.id,
		                  b'{suitable_server}')  # TODO: change parameter to the serializable encoding of suitable_server
		msgs_to_clients_q.append(msg)


def get_server(ip: str, port: int, servers: list[Server]):
	for server in servers:
		if server.ip == ip and server.port == port:
			return server
	return None

def get_msgs_from_socket(sock: socket.socket, servers: list[Server]):
	while True:
		data, addr = sock.recvfrom(1024)
		server = get_server(addr[0], addr[1], servers)
		if server is None:
			continue
		decrypt(data, server.key)

		player = PlayerCentral(data[1:])  # TODO: Do it with serializable
		players[player.id] = player

# def send_overlapped_players_details(sock: socket.socket, servers: list[Server]):
# 	for player in players_overlap:
# 		if player.pos in Rect(0, 0, center.x+overlapping_area_T, center.y+overlapping_area_T):
# 			send(sock, servers[0], player)
#
# 		if player.pos in Rect(center.x-overlapping_area_T, 0, W, center.y-overlapping_area_T):
# 			send(sock, servers[1], player)
#
# 		if player.pos in Rect(0, center.x-overlapping_area_T, center.x+overlapping_area_T, H):
# 			send(sock, servers[2], player)
#
# 		if player.pos in Rect(center.x-overlapping_area_T, center.y-overlapping_area_T, W, H):
# 			send(sock, servers[3], player)


def LB_main(new_players_q: deque[PlayerCentral], msgs_to_clients_q: deque[MsgToClient]):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('0.0.0.0', PORT))

	threads: list[threading.Thread] = []

	look_for_new_client_Thread = threading.Thread(target=look_for_new_client, args=(new_players_q, msgs_to_clients_q))
	threads.append(look_for_new_client_Thread)

	# send_overlapped_players_details_Thread = threading.Thread(target=send_overlapped_players_details, args=(sock, normal_servers))
	# threads.append(send_overlapped_players_details_Thread)

	get_msgs_from_socket_Thread = threading.Thread(target=get_msgs_from_socket, args=(sock, normal_servers))
	threads.append(get_msgs_from_socket_Thread)

	# update_center_Thread = threading.Thread(target=get_new_center, args=(players,))
	# threads.append(update_center_Thread)

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()
