from typing import List

import pygame
import random
from client_files.code.tile import Tile


class Projectile(pygame.sprite.Sprite):
	def __init__(self, player, weapon, direction, groups, obstacle_sprites, height, speed, despawn_time, image_path, damage, action=None, create_explosion=None, spin=False):
		super().__init__(groups)
		self.player = player
		self.height: int = height
		self.obstacle_sprites: pygame.sprite.Group = obstacle_sprites

		self.direction: pygame.math.Vector2 = direction
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()
		else:
			self.kill()

		self.original_image: pygame.Surface = pygame.image.load(image_path).convert_alpha()
		self.degree: float = -self.direction.as_polar()[1]
		self.image: pygame.Surface = pygame.transform.rotate(self.original_image, self.degree)

		self.rect: pygame.Rect = self.image.get_rect(center=weapon.rect.center)
		self.hitbox = self.rect
		self.pos: List[int, int] = list(self.rect.center)
		self.speed: int = speed

		# Kill time
		self.spawn_time: int = pygame.time.get_ticks()
		self.despawn_time: int = despawn_time

		self.action: str = action
		self.spin: int = 0
		if spin:
			self.spin = random.randint(8, 15) * (random.randrange(-1, 2, 2))

		# Action
		self.damage = damage
		self.create_explosion = create_explosion
		self.exploded = False

	def update(self) -> None:
		"""
		Move forwards
		:return: None
		"""
		self.move()

		# Check if despawn
		current_time: int = pygame.time.get_ticks()
		if current_time - self.spawn_time >= self.despawn_time:
			if self.action == 'explode':
				self.explode()
			else:
				self.kill()

		self.collision()

	def move(self) -> None:
		"""
		Move the projectile towards the direction it is going
		:return: None
		"""
		self.pos[0] += self.direction[0] * self.speed
		self.pos[1] += self.direction[1] * self.speed

		self.degree += self.spin

		self.image = pygame.transform.rotate(self.original_image, self.degree)
		self.rect = self.image.get_rect(center=self.pos)
		self.hitbox.center = self.rect.center

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
			if sprite.hitbox.colliderect(self.hitbox) and sprite is not self and sprite is not self.player:  # Do not collide with own player
				if not (type(sprite) is Tile and sprite.sprite_type == 'barrier'):  # Don't collide with barriers
					if self.action == 'explode':
						self.explode()
					else:
						if hasattr(sprite, "health"):
							sprite.health -= self.damage
						self.kill()

	def explode(self) -> None:
		"""
		Explode.
		:return: None
		"""
		if not self.exploded:
			self.exploded = True
			self.create_explosion(self.rect.center, self.damage)
			self.kill()
