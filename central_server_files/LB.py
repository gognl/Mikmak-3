import threading
from collections import deque
from structures import *
from server_files_normal.game.settings import *

center = Point(MAP_WIDTH//2, MAP_HEIGHT//2)
players: dict[ID, PlayerCentral] = {}

def get_new_center(players: dict[ID, PlayerCentral]):
	if len(players) == 0:
		return Point(MAP_WIDTH//2, MAP_HEIGHT//2)

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


def LB_main(new_players_q: deque[PlayerCentral], LB_to_login_q: deque[LB_to_login_msg]):
	threads: list[threading.Thread] = []

	look_for_new_client_Thread = threading.Thread(target=look_for_new_client, args=(new_players_q, LB_to_login_q))
	threads.append(look_for_new_client_Thread)

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()
