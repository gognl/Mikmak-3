import pygame
from pygame.sprite import AbstractGroup
from server_files_normal import ClientManager


class Player(pygame.sprite.Sprite):
	def __init__(self, groups: AbstractGroup, entity_id: int, pos: (int, int)):
		super().__init__(groups)
		self.client_manager: ClientManager = None
		self.entity_id = entity_id

		# Load player sprite from files
		self.image: pygame.Surface = pygame.image.load('./graphics/player/down_idle/down.png')

		# Position of player
		self.rect: pygame.Rect = self.image.get_rect(topleft=pos)

		# Attacking
		self.attacking: bool = False

		# weapon
		self.weapon = ''

		# Animations
		self.status = 'down'
