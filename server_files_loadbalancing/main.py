import random
import socket

import numpy
import numpy as np
import pygame


class Server:
	def __init__(self, ip: str, port: int):
		self.ip: str = ip
		self.port: int = port


class NormalServer(Server):
	def __init__(self, ip: str, port: int):
		super().__init__(ip, port)
		self.location = Point(-1, -1)

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __repr__(self):
		return f"({self.x}, {self.y})"

def dist2(p1, p2):
	return (p1.x - p2.x)**2 + (p1.y - p2.y)**2

def get_closest_centroid(p: Point, centroids: list[Point]) -> int:
	closest_centroid_index = 0
	min_dist2 = dist2(p, centroids[0])
	for j in range(1, len(centroids)):
		d2 = dist2(p, centroids[j])
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

			J += dist2(p, centroids[closest_centroid_index])

		for j in range(k-1, -1, -1):
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

def main():
	simulate_algo()
	# servers: list[NormalServer] = []
	# login_ip, login_port = "", 0
	# login_server = Server(login_ip, login_port)
	#
	# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# sock.bind(("0.0.0.0", 17120))
	#
	# while True:
	# 	data, address = sock.recvfrom(1024)




if __name__ == '__main__':
	main()
