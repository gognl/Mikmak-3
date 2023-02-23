import pygame
from client_files.code.tile import Tile
from client_files.code.settings import *


class Weapon(pygame.sprite.Sprite):
	def __init__(self, player, groups, obstacle_sprites, height):
		super().__init__(groups)
		self.player = player

		self.direction: str = None
		self.image: pygame.Surface = None
		self.rect: pygame.Rect = None

		# graphic
		self.height: int = height

		# Collision damage
		self.obstacle_sprites = obstacle_sprites
		self.collidable = False
		self.acted = False
		self.damage = int(weapon_data[self.player.weapon]['damage'] + (0.1 * player.strength))

		self.update()

	def update(self) -> None:
		"""
		Updates position and direction
		:return: None
		"""

		if self.player.status == 'dead':
			self.kill()
			return

		self.direction = self.player.status.split('_')[0]

		full_path: str = f'../graphics/weapons/{self.player.weapon}/{self.direction}.png'
		self.image = pygame.image.load(full_path).convert_alpha()

		if self.player.weapon_index == 0:  # Only sword has collidable damage
			self.collidable = True

		# position
		if self.direction == 'up':
			self.rect = self.image.get_rect(midbottom=self.player.rect.midtop + pygame.math.Vector2(-10, 3))
		elif self.direction == 'down':
			self.rect = self.image.get_rect(midtop=self.player.rect.midbottom + pygame.math.Vector2(-10, -15))
		elif self.direction == 'left':
			self.rect = self.image.get_rect(midright=self.player.rect.midleft + pygame.math.Vector2(27, 16))
		elif self.direction == 'right':
			self.rect = self.image.get_rect(midleft=self.player.rect.midright + pygame.math.Vector2(-27, 16))

		if self.collidable:
			if not self.acted:
				self.collision()

	def update_obstacles(self, obstacle_sprites: pygame.sprite.Group) -> None:
		"""
		Update obstacle sprites
		:return: None
		"""
		self.obstacle_sprites = obstacle_sprites

	def collision(self) -> None:
		"""
		Check for collisions
		:return: None
		"""
		for sprite in self.obstacle_sprites:
			if sprite.hitbox.colliderect(self.rect) and sprite is not self and sprite is not self.player:  # Do not collide with own player
				if not (type(sprite) is Tile and sprite.sprite_type == 'barrier'):  # Don't collide with barriers
					if hasattr(sprite, "health"):
						sprite.deal_damage(self.damage)
						self.acted = True
