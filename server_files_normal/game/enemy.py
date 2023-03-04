from typing import List

import pygame

from server_files_normal.game.item import Item
from server_files_normal.game.projectile import Projectile
from server_files_normal.game.support import import_folder
from server_files_normal.game.player import Player
from server_files_normal.game.settings import *
from server_files_normal.structures import Client


class Enemy(pygame.sprite.Sprite):
	def __init__(self, enemy_name: str, pos: (int, int), groups, entity_id: int, obstacle_sprites: pygame.sprite.Group, item_sprites, create_explosion, create_bullet):
		super().__init__(groups)

		self.entity_id = entity_id

		self.import_graphics(enemy_name)
		self.image = self.animations[self.status][0]
		self.rect = self.image.get_rect(topleft=pos)

		# Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
		self.hitbox = self.rect

		# stats
		self.enemy_name = enemy_name
		self.enemy_info = enemy_data[enemy_name]
		self.health = self.enemy_info['health']
		self.xp = self.enemy_info['xp']
		self.speed = self.enemy_info['speed']
		self.damage = self.enemy_info['damage']
		self.resistance = self.enemy_info['resistance']
		self.attack_radius = self.enemy_info['attack_radius']
		self.notice_radius = self.enemy_info['notice_radius']

		# Death
		self.xp = self.enemy_info['xp']
		self.death_items = self.enemy_info['death_items']

		self.obstacle_sprites: pygame.sprite.Group = obstacle_sprites

		self.direction = pygame.math.Vector2()

		self.item_sprites = item_sprites

		# Attack cooldown
		self.can_attack = True
		self.attack_time = 0
		self.attack_cooldown = ENEMY_ATTACK_COOLDOWN

		# Move cooldown
		self.can_move = True
		self.move_time = 0
		self.move_cooldown = self.enemy_info['move_cooldown']

		# Attack actions
		self.create_explosion = create_explosion
		self.create_bullet = create_bullet

	def create_dropped_item(self, name, pos, item_id):
		new_item = Item(name, (self.item_sprites,), pos, item_id)
		new_item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='drop', pos=pos))

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

	def attack(self, player):
		if self.enemy_name == "white_cow" or self.enemy_name == "green_cow":
			player.deal_damage(self.damage)
		elif self.enemy_name == "red_cow":
			self.create_explosion(self.rect.center, self.damage)
			pass  # die
		elif self.enemy_name == "yellow_cow":
			self.create_bullet(self, self.rect.center, pygame.math.Vector2(player.rect.center[0], player.rect.center[1]))

	def actions(self, player):
		if self.status == 'attack':
			if self.can_attack:
				self.can_attack = False
				self.attack(player)

		elif self.status == 'move':
			if self.can_move:
				self.can_move = False
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

	def cooldowns(self):
		if not self.can_attack:
			if self.attack_time >= self.attack_cooldown:
				self.can_attack = True
				self.attack_time = 0
			else:
				self.attack_time += 1

		if not self.can_move:
			if self.move_time >= self.move_cooldown:
				self.can_move = True
				self.move_time = 0
			else:
				self.move_time += 1

	def update(self):
		self.move(self.speed)

		if self.health <= 0:
			pass  # die

		self.cooldowns()

	def enemy_update(self, players):
		if not players:
			return
		player: Player = self.get_closest_player(players)
		self.get_status(player)
		self.actions(player)

	def deal_damage(self, damage):
		self.health -= int(damage - (0.1 * self.resistance))
