import random
import threading
from collections import deque
import pygame
from structures import *


def get_closest_centroid(p: Point, centroids: list[Point]) -> int:
	closest_centroid_index = 0
	min_dist2 = Point.dist2(p, centroids[0])
	for j in range(1, len(centroids)):
		d2 = Point.dist2(p, centroids[j])
		if d2 < min_dist2:
			min_dist2 = d2
			closest_centroid_index = j

	return closest_centroid_index


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


def simulate_algo():
	W = 800
	H = 600
	SERVERS_AMOUNT = 1
	PLAYERS_AMOUNT = 100

	def rand(n):
		return random.randrange(n)

	positions = [Point(rand(W), rand(H)) for _ in range(PLAYERS_AMOUNT)]
	centroids = [Point(rand(W), rand(H)) for _ in range(SERVERS_AMOUNT)]

	centroids = update_centroids(positions, centroids)

	print(len(centroids))

	pygame.init()
	screen = pygame.display.set_mode((800, 600))

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		screen.fill((255, 255, 255))

		for p in positions:
			pygame.draw.circle(screen, (0, 0, 255), (p.x, p.y), 3)

		for c in centroids:
			pygame.draw.circle(screen, (255, 0, 0), (c.x, c.y), 2)

		pygame.display.flip()

	pygame.quit()


def find_suitable_server(client: Client) -> Server:
	pass


def look_for_new_client(new_clients_q: deque[Client], msgs_to_clients_q: deque[MsgToClient]):
	while True:
		if len(new_clients_q) == 0:
			continue
		new_client = new_clients_q.pop()
		suitable_server = find_suitable_server(new_client)
		msg = MsgToClient(new_client.id,
						b'{suitable_server}')  # TODO: change parameter to the serializable encoding of suitable_server
		msgs_to_clients_q.append(msg)


def LB_main(new_clients_q: deque[Client], msgs_to_clients_q: deque[MsgToClient]):
	threads: [threading.Thread] = []

	look_for_new_client_Thread = threading.Thread(target=look_for_new_client, args=(new_clients_q, msgs_to_clients_q))
	threads.append(look_for_new_client_Thread)

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()
