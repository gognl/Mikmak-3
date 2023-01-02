import socket
import pygame
from client_demo_files.settings import *


def initialize_game() -> (pygame.Surface, pygame.time.Clock):
	"""
	    Initializes the game.
	    :return: screen, clock
	"""
	pygame.init()
	size = (WINDOW_WIDTH, WINDOW_HEIGHT)
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption("Cows")
	clock = pygame.time.Clock()
	return screen, clock


def run_game():

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False


def close_game():
	pygame.quit()


def main():
	initialize_game()
	run_game()
	close_game()


if __name__ == '__main__':
	main()
	print("123")

