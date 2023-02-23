from typing import List

import pygame

from server_files_normal.game.projectile import Projectile
from server_files_normal.game.support import import_folder
from server_files_normal.game.player import Player
from server_files_normal.game.settings import *


class Enemy(pygame.sprite.Sprite):
	def __init__(self, enemy_name: str, pos: (int, int), groups, entity_id: int, obstacle_sprites: pygame.sprite.Group):
		super().__init__(groups)

		self.entity_id = entity_id

		self.import_graphics(enemy_name)
		self.image = self.animations[self.status][0]
		self.rect = self.image.get_rect(topleft=pos)

		# Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
		self.hitbox = self.rect.inflate(-20, -26)

		# stats
		self.enemy_name = enemy_name
		enemy_info = enemy_data[enemy_name]
		self.health = enemy_info['health']
		self.xp = enemy_info['xp']
		self.speed = enemy_info['speed']
		self.damage = enemy_info['damage']
		self.resistance = enemy_info['resistance']
		self.attack_radius = enemy_info['attack_radius']
		self.notice_radius = enemy_info['notice_radius']

		self.obstacle_sprites: pygame.sprite.Group = obstacle_sprites

		self.direction = pygame.math.Vector2()

	def import_graphics(self, name: str):
		self.animations = {'move': []}
		path = f'./graphics/monsters/{name}/move/'
		self.animations['move'] = list(import_folder(path).values())
		self.status = 'move'

	def get_closest_player(self, players: List[Player]) -> Player:
		enemy_pos = pygame.Vector2(self.rect.center)
		return min(players, key=lambda p: enemy_pos.distance_squared_to(pygame.Vector2(p.rect.center)))

	def get_player_distance_direction(self, player):
		enemy_vec = pygame.math.Vector2(self.rect.center)
		player_vec = pygame.math.Vector2(player.rect.center)
		distance = (player_vec - enemy_vec).magnitude()
		if distance > 10:
			direction = (player_vec - enemy_vec).normalize()
		else:
			direction = pygame.math.Vector2()
		return distance, direction

	def get_status(self, player):
		distance = self.get_player_distance_direction(player)[0]

		if distance <= self.attack_radius:
			self.status = 'attack'
		elif distance <= self.notice_radius:
			self.status = 'move'
		else:
			self.status = 'idle'

	def actions(self, player):
		if self.status == 'attack':
			#print('attack')
			pass
		elif self.status == 'move':
			self.direction = self.get_player_distance_direction(player)[1]
			self.image = self.animations['move'][0 if self.direction.x < 0 else 1]
		else:
			self.direction = pygame.math.Vector2()

	def move(self, speed: int) -> None:
		"""
		Move the player towards the direction it is going, and apply collision
		:param speed: maximum pixels per direction per frame (may vary if both directions are active)
		:return: None
		"""
		# Normalize direction
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal')  # Check collisions in the horizontal axis
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')  # Check collisions in the vertical axis
		self.rect.center = self.hitbox.center

	def collision(self, direction: str) -> None:
		"""
		Apply collisions to the player, each axis separately
		:param direction: A string representing the direction the player is going
		:return: None
		"""

		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox) and sprite is not self and type(sprite) is not Projectile:  # Do not collide with projects - they collide with you
					if self.direction.x > 0:  # Player going right
						self.hitbox.right = sprite.hitbox.left
					elif self.direction.x < 0:  # Player going left
						self.hitbox.left = sprite.hitbox.right
					elif hasattr(sprite, 'direction'):  # Only if sprite has direction
						if sprite.direction.x > 0:  # Sprite going right
							self.hitbox.left = sprite.hitbox.right
						elif sprite.direction.x < 0:  # Sprite going left
							self.hitbox.right = sprite.hitbox.left

		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox) and sprite is not self and type(sprite) is not Projectile:  # Do not collide with projects - they collide with you
					if self.direction.y > 0:  # Player going down
						self.hitbox.bottom = sprite.hitbox.top
					elif self.direction.y < 0:  # Player going up
						self.hitbox.top = sprite.hitbox.bottom
					elif hasattr(sprite, 'direction'):  # Only if sprite has direction
						if sprite.direction.y > 0:  # Sprite going down
							self.hitbox.top = sprite.hitbox.bottom
						elif sprite.direction.y < 0:  # Sprite going up
							self.hitbox.bottom = sprite.hitbox.top

	def update(self):
		self.move(self.speed)

	def enemy_update(self, players):
		if not players:
			return
		player: Player = self.get_closest_player(players)
		self.get_status(player)
		self.actions(player)

	def deal_damage(self, damage):
		self.health -= int(damage - (0.1 * self.resistance))
