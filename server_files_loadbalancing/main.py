import random
import socket

import numpy
import numpy as np
import pygame

W = 800
H = 600
SERVERS_AMOUNT = 7
PLAYERS_AMOUNT = 100

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __repr__(self):
		return f"({self.x}, {self.y})"


def rand(n):
	return random.randrange(n)


def dist2(p1, p2):
	return (p1.x - p2.x)**2 + (p1.y - p2.y)**2

def main():
	positions = [Point(rand(W), rand(H)) for _ in range(PLAYERS_AMOUNT)]
	m = len(positions)

	centroids = [Point(rand(W), rand(H)) for _ in range(SERVERS_AMOUNT)]

	for iter in range(1, 21):
		k = len(centroids)
		closest = [[] for j in range(k)]
		J = 0
		for p in positions:
			closest_centroid_index = 0
			min_dist2 = dist2(p, centroids[0])
			for j in range(1, k):
				d2 = dist2(p, centroids[j])
				if d2 < min_dist2:
					min_dist2 = d2
					closest_centroid_index = j

			closest[closest_centroid_index].append(p)
			J += min_dist2

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

		J /= m
		print(f"After {iter} iterations: Error is {J}")

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




if __name__ == '__main__':
	main()
