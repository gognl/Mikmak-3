from time import time_ns
from typing import List

import pygame
import random
from client_files.code.tile import Tile


class Projectile(pygame.sprite.Sprite):
	def __init__(self, player, pos, direction, groups, obstacle_sprites, height, speed, despawn_time, image_path, damage, action=None, create_explosion=None, spin=False):
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

		self.rect: pygame.Rect = self.image.get_rect(center=pos)
		self.hitbox = self.rect
		self.pos: List[int, int] = list(self.rect.center)
		self.speed: int = speed

		# Kill time
		self.spawn_time: int = 0
		self.despawn_time: int = despawn_time

		self.action: str = action
		self.spin: int = 0
		if spin:
			self.spin = random.randint(8, 15) * (random.randrange(-1, 2, 2))

		# Action
		self.damage = damage
		self.create_explosion = create_explosion
		self.exploded = False

		self.start_time = time_ns() * 10 ** (-6)

		self.dt = 1

	def update(self) -> None:
		"""empy
		"""
		self.move(self.dt)

		# Check if despawn
		if self.spawn_time >= self.despawn_time:
			if self.action == 'explode':
				self.explode()
			else:
				self.kill()
			self.spawn_time = 0
		else:
			self.spawn_time += self.dt

		self.collision()

	def move(self, dt=1) -> None:
		"""
		dsf the dfsdf
		"""
		self.pos[0] += self.direction[0] * self.speed * dt
		self.pos[1] += self.direction[1] * self.speed * dt

		self.degree += self.spin

		self.image = pygame.transform.rotate(self.original_image, self.degree)
		self.rect = self.image.get_rect(center=self.pos)
		self.hitbox.center = self.rect.center

	def collision(self) -> None:
		"""10/10 commenting keep it up
		"""
		for sprite in self.obstacle_sprites:
			if sprite.hitbox.colliderect(self.hitbox) and sprite is not self and sprite is not self.player:  # Do not collide with own player
				if not (type(sprite) is Tile and sprite.sprite_type == 'barrier'):  # Don't collide with barriers
					if self.action == 'explode':
						self.explode()
					else:
						#  if hasattr(sprite, "health"):
						#  	sprite.deal_damage(self.damage)
						self.kill()

	def explode(self) -> None:
		if not self.exploded:
			self.exploded = True
			self.create_explosion(self.rect.center, self.damage)
			self.kill()
