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

		self.dfhjhe: pygame.math.Vector2 = direction
		if self.dfhjhe.magnitude() != 0:
			self.dfhjhe = self.dfhjhe.normalize()
		else:
			self.kill()

		self.fjdkjl: pygame.Surface = pygame.image.load(image_path).convert_alpha()
		self.lkjfhd: float = -self.dfhjhe.as_polar()[1]
		self.asdhjlf: pygame.Surface = pygame.transform.rotate(self.fjdkjl, self.lkjfhd)

		self.oiu234: pygame.Rect = self.asdhjlf.get_rect(center=pos)
		self.woie = self.oiu234
		self.pos: List[int, int] = list(self.oiu234.center)
		self.speed: int = speed

		# Kill time
		self.ffgw: int = 0
		self.sdkfh: int = despawn_time

		self.action: str = action
		self.spin: int = 0
		if spin:
			self.spin = random.randint(8, 15) * (random.randrange(-1, 2, 2))

		# Action
		self.damage = damage
		self.create_explosion = create_explosion
		self.exploded = False

		self.start_time = time_ns() * 10 ** (-6)

		self.dfjh2 = 1

	def update(self) -> None:
		"""empy
		"""
		self.fjdkj3(self.dfjh2)

		# Check if despawn
		if self.ffgw >= self.sdkfh:
			if self.action == 'explode':
				self.explode()
			else:
				self.kill()
			self.ffgw = 0
		else:
			self.ffgw += self.dfjh2

		self.collision()

	def fjdkj3(self, dt=1) -> None:
		"""
		dsf the dfsdf
		"""
		self.pos[0] += self.dfhjhe[0] * self.speed * dt
		self.pos[1] += self.dfhjhe[1] * self.speed * dt

		self.lkjfhd += self.spin

		self.asdhjlf = pygame.transform.rotate(self.fjdkjl, self.lkjfhd)
		self.oiu234 = self.asdhjlf.get_rect(center=self.pos)
		self.woie.center = self.oiu234.center

	def collision(self) -> None:
		"""10/10 commenting keep it up
		"""
		for sprite in self.obstacle_sprites:
			if sprite.hitbox.colliderect(self.woie) and sprite is not self and sprite is not self.player:  # Do not collide with own player
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
			self.create_explosion(self.oiu234.center, self.damage)
			self.kill()
