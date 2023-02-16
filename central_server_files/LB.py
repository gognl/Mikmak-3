import math
import random
import threading
import time
from collections import deque
import pygame
from structures import *


def rand(n):
	return random.randrange(n)


amount_servers = 4
W = 800  # 40960
H = 600  # 30720

normal_servers = [Server("0.0.0.0", i) for i in range(amount_servers)]
center = Point(W//2, H//2)
players = [Player(Point(rand(W), rand(H)), 0) for _ in range(100)]


def get_new_center(players: list[Player]):
	if len(players) == 0:
		return Point(W//2, H//2)

	avg = Point(0, 0)
	for player in players:
		avg.add(player.pos)
	avg.div(len(players))
	return avg


def find_suitable_server_index(player: Player, center: Point) -> int:
	b0 = player.pos.x > center.x
	b1 = player.pos.y > center.y
	return 2*b1+b0

def look_for_new_client(new_clients_q: deque[Player], msgs_to_clients_q: deque[MsgToClient], servers: list[Server]):
	while True:
		if len(new_clients_q) == 0:
			continue
		new_client = new_clients_q.pop()
		suitable_server = servers[find_suitable_server_index(new_client, center)]
		msg = MsgToClient(new_client.id,
		                  b'{suitable_server}')  # TODO: change parameter to the serializable encoding of suitable_server
		msgs_to_clients_q.append(msg)

def LB_main(new_players_q: deque[Player], msgs_to_clients_q: deque[MsgToClient]):
	threads: [threading.Thread] = []

	look_for_new_client_Thread = threading.Thread(target=look_for_new_client, args=(new_players_q, msgs_to_clients_q))
	threads.append(look_for_new_client_Thread)

	update_regions_Thread = threading.Thread(target=get_new_center, args=(players,))
	threads.append(update_regions_Thread)

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()

colors = [(0, 255, 0), (0, 0, 255), (255, 0, 255), (255, 120, 0)]
cnts = [0, 0, 0, 0]

def show_example():

	center = get_new_center(players)
	for p in players:
		cnts[find_suitable_server_index(p, center)] += 1
	print(cnts)

	pygame.init()

	# Set up the drawing window
	screen = pygame.display.set_mode([W, H])

	# Run until the user asks to quit
	running = True
	while running:

		# Did the user click the window close button?
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		screen.fill((255, 255, 255))

		pygame.draw.circle(screen, (255, 0, 0), (center.x, center.y), 3)

		for p in players:
			pygame.draw.circle(screen, colors[find_suitable_server_index(p, center)], (p.pos.x, p.pos.y), 2)

		pygame.display.flip()

	# Done! Time to quit.
	pygame.quit()

show_example()