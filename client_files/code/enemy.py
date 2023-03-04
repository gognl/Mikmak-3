from typing import List, Union
import random

import pygame.time

from client_files.code.other_player import OtherPlayer
from client_files.code.player import Player
from client_files.code.settings import *
from client_files.code.entity import Entity
from client_files.code.support import *


class Enemy(Entity):
	def __init__(self, enemy_name, pos, groups, entity_id, obstacle_sprites, create_dropped_item, create_explosion, create_bullet, safe=None, nametag=False, name=None, create_nametag=None, nametag_update=None):
		# general setup
		super().__init__(groups, entity_id, nametag, name, create_nametag, nametag_update)
		self.status = None
		self.sprite_type = 'enemy'

		# graphics setup
		self.import_graphics(enemy_name)
		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(topleft=pos)
		self.height = 2

		self.hitbox = self.rect
		self.obstacle_sprites = obstacle_sprites

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
		self.create_dropped_item = create_dropped_item

		# Server
		self.changes = {'pos': (self.rect.x, self.rect.y)}  # changes made in this tick

		# Safe from attacks
		self.safe = safe

		# Nametag
		if nametag:
			self.initialize_nametag()

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

	def import_graphics(self, name):
		self.animations = {'move': []}
		path = f'../graphics/monsters/{name}/move/'
		self.animations['move'] = list(import_folder(path).values())
		self.status = 'move'

	def animate(self) -> None:
		"""
        animate through images
        :return: None
        """
		animation: List[pygame.Surface] = self.animations[self.status]

		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# set the image
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center=self.hitbox.center)

	def get_closest_player(self, players: List[Union[Player, 'OtherPlayer']]) -> Union[Player, 'OtherPlayer']:
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
			self.on_kill()
			self.kill()
		elif self.enemy_name == "yellow_cow":
			self.create_bullet(self, self.rect.center, pygame.math.Vector2(player.rect.center[0], player.rect.center[1]))

	def actions(self, player):
		if self.status == 'attack':
			# if self.can_attack:
			# 	self.can_attack = False
			# 	self.attack(player)
			pass  # moved to server

		elif self.status == 'move':
			if self.can_move:
				self.can_move = False
				self.direction = self.get_player_distance_direction(player)[1]
				self.image = self.animations['move'][0 if self.direction.x < 0 else 1]

		else:
			self.direction = pygame.math.Vector2()

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

	def on_kill(self):
		for i in range(min(2, len(self.death_items))):
			self.create_dropped_item(random.choice(self.death_items), self.rect.center)
		for i in range(self.xp):
			self.create_dropped_item("xp", self.rect.center)

	def update(self):

		previous_state: dict = {'pos': (self.rect.x, self.rect.y)}

		self.move(self.speed)

		self.changes: dict = {'pos': (self.rect.x, self.rect.y)}
		if self.changes == previous_state:
			self.changes = None

		# Death
		if self.health <= 0:
			self.on_kill()
			self.kill()

		self.cooldowns()

	def enemy_update(self, players):
		if not players:
			return

		# Don't use players who are safe from this enemy
		for i, player in enumerate(players):
			if self.safe is not None and player in self.safe:
				del players[i]

		if not players:
			return

		player: Player = self.get_closest_player(players)
		self.get_status(player)
		self.actions(player)


class Pet(Enemy):
	def __init__(self, enemy_name, pos, groups, entity_id, obstacle_sprites, owner, create_dropped_item, create_explosion, create_bullet, safe, nametag, name, create_nametag, nametag_update):
		super().__init__(enemy_name, pos, groups, entity_id, obstacle_sprites, create_dropped_item, create_explosion, create_bullet, safe, nametag, name, create_nametag, nametag_update)
		self.owner = owner

		self.stop_radius = self.enemy_info['stop_radius']

	def get_status(self, owner):
		distance = self.get_player_distance_direction(owner)[0]

		if self.notice_radius < distance:
			self.status = 'move'
		elif self.stop_radius >= distance:
			self.status = 'idle'

	def actions(self, owner):
		if self.status == 'move':
			self.direction = self.get_player_distance_direction(owner)[1]
			self.image = self.animations['move'][0 if self.direction.x < 0 else 1]
		else:
			self.direction = pygame.math.Vector2()

	def update(self):
		previous_state: dict = {'pos': (self.rect.x, self.rect.y)}

		self.move(self.speed)  # TODO - path finding for pets

		self.changes: dict = {'pos': (self.rect.x, self.rect.y)}
		if self.changes == previous_state:
			self.changes = None

		# Death
		if self.health <= 0:
			self.on_kill()

			self.nametag.kill = True
			self.owner.pets -= 1
			self.kill()

	def enemy_update(self, players):
		self.get_status(self.owner)
		self.actions(self.owner)


class TitleEnemy(Enemy):
	def __init__(self, enemy_name, pos, groups, direction):
		super().__init__(enemy_name, pos, groups, 0, None, None, None, None)

		self.direction = direction
		self.image = self.animations['move'][0 if self.direction[0] < 0 else 1]

	def title_move(self):
		self.rect.x += self.direction[0]
