import math
import random
import threading
import time
from collections import deque
import pygame
from structures import *


def get_closest_server(p: Point, regions_division: dict[Server, Region]) -> Server:
	closest_server = None
	min_dist2 = math.inf
	for server in regions_division:
		d2 = Point.dist2(p, regions_division[server].c)
		if d2 < min_dist2:
			min_dist2 = d2
			closest_server = server

	return closest_server


def update_centroids(positions, prev_centroids):
	centroids = [Point(c.x, c.y) for c in prev_centroids]

	for iter in range(1, 21):
		k = len(centroids)
		closest = [[] for j in range(k)]
		J = 0
		for p in positions:
			closest_centroid_index = get_closest_centroid(p, centroids)
			closest[closest_centroid_index].append(p)

			J += Point.dist2(p, centroids[closest_centroid_index])

		for j in range(k - 1, -1, -1):
			if len(closest[j]) == 0:
				centroids.pop(j)
				continue

			l = len(closest[j])
			new_location = Point(0, 0)
			for i in range(l):
				new_location.x += closest[j][i].x
				new_location.y += closest[j][i].y
			centroids[j] = Point(new_location.x / l, new_location.y / l)

		J /= len(positions)
		print(f"After {iter} iterations: Error is {J}")

	return centroids


def rand(n):
	return random.randrange(n)

amount_servers = 5
W = 800#40960
H = 600#30720

normal_servers = [Server("0.0.0.0", i) for i in range(amount_servers)]
regions_division = {server: Region(Point(rand(W), rand(H)), -1, -1) for server in normal_servers}
players = [Player(Point(rand(W), rand(H)), 0) for _ in range(100)]

def update_regions(players: list[Player], regions_division: dict[Server, Region]):
	while True:
		players_copy = players.copy()

		regions_div_copy = {server: regions_division[server] for server in normal_servers}
		players_belong: dict[Server, list[Player]] = {}

		for iter in range(1, 21):
			players_belong, changed_regions_div = {}, {}
			for server in normal_servers:
				players_belong[server] = []
				changed_regions_div[server] = Region(Point(0, 0), -1, -1)

			for player in players_copy:
				closest_server = get_closest_server(player.pos, regions_div_copy)
				changed_regions_div[closest_server].c.add(player.pos)
				players_belong[closest_server].append(player)

			for server in normal_servers:
				if len(players_belong[server]) == 0:
					# server is not used
					continue
				changed_regions_div[server].c.div(len(players_belong[server]))

				regions_div_copy[server] = changed_regions_div[server]

		for server in normal_servers:
			max_dx, max_dy = -math.inf, -math.inf
			for player in players_belong[server]:
				dx = abs(player.pos.x - regions_div_copy[server].c.x)
				if dx > max_dx:
					max_dx = dx

				dy = abs(player.pos.y - regions_div_copy[server].c.y)
				if dy > max_dy:
					max_dy = dy

			regions_div_copy[server].rw, regions_div_copy[server].rh = max_dx, max_dy

		for server in normal_servers:
			regions_division[server] = regions_div_copy[server]

		time.sleep(5)

		
def find_suitable_server(player: Player) -> Server:
	for server in normal_servers:
		if player.pos in regions_division[server]:
			return server

	return None  # not arriving here


def look_for_new_client(new_clients_q: deque[Player], msgs_to_clients_q: deque[MsgToClient]):
	while True:
		if len(new_clients_q) == 0:
			continue
		new_client = new_clients_q.pop()
		suitable_server = find_suitable_server(new_client)
		msg = MsgToClient(new_client.id,
						b'{suitable_server}')  # TODO: change parameter to the serializable encoding of suitable_server
		msgs_to_clients_q.append(msg)


def LB_main(new_players_q: deque[Player], msgs_to_clients_q: deque[MsgToClient]):
	threads: [threading.Thread] = []

	look_for_new_client_Thread = threading.Thread(target=look_for_new_client, args=(new_players_q, msgs_to_clients_q))
	threads.append(look_for_new_client_Thread)

	update_regions_Thread = threading.Thread(target=update_regions, args=(players, regions_division))
	threads.append(update_regions_Thread)

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()
