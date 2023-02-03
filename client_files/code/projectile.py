import pygame
from client_files.code.entity import Entity


class Projectile(Entity):
	def __init__(self, player, camera, screen_center, weapon, mouse, groups, height):
		super().__init__(groups)
		self.height: int = height

		self.direction: pygame.math.Vector2 = pygame.math.Vector2(mouse[0], mouse[1])
		self.image: pygame.Surface = pygame.image.load('../graphics/player/down_idle/down.png').convert_alpha()
		self.rect: pygame.Rect = self.image.get_rect(center=weapon.rect.center)
		self.hitbox = self.rect
		print(self.rect.center)

		# TODO - collisions

	def update(self) -> None:
		"""
		Move forwards
		:return: None
		"""
		self.rect.center += self.direction
