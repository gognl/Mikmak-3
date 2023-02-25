from collections import deque

import pygame
from server_files_normal import ClientManager
from server_files_normal.game.settings import *
from server_files_normal.game.weapon import Weapon
from server_files_normal.structures import *
from server_files_normal.game.item import Item


class Player(pygame.sprite.Sprite):
	def __init__(self, groups, entity_id: int, pos: (int, int), create_bullet, create_kettle, weapons_group, create_attack, item_sprites):
		self.client_manager: ClientManager = None
		self.entity_id = entity_id

		# Load player sprite from files
		self.image: pygame.Surface = pygame.image.load('./graphics/player/down_idle/down.png')

		# Position of player
		self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
		self.hitbox = self.rect.inflate(-20, -26)

		# Animations
		self.status = 'down'

		# Shooting cooldown
		self.can_shoot = True
		self.shoot_time = None
		self.shoot_cooldown = 18  # less than client cooldown, because of the possible latency

		# Switch cooldown
		self.can_switch_weapon = True
		self.weapon_switch_time = None
		self.switch_duration_cooldown = 18  # less than client cooldown, because of the possible latency

		# violence
		self.attacking: bool = False
		self.attack_cooldown: int = 18  # less than client cooldown, because of the possible latency
		self.attack_time: int = 0

		# Projectiles
		self.create_attack = create_attack
		self.create_bullet = create_bullet
		self.create_kettle = create_kettle

		# Weapons
		self.weapon_index = 0
		self.on_screen = (1, 2)  # Indices of weapons that stay on screen
		self.weapon = list(weapon_data.keys())[self.weapon_index]
		self.current_weapon = None

		self.attacks: deque = deque()

		# updates queue
		self.update_queue: deque = deque()

		# Stats
		self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'speed': 10}
		self.health = self.stats['health']
		self.energy = self.stats['energy']
		self.xp = 0
		self.speed = self.stats['speed']
		self.strength = self.stats['attack']
		self.resistance = 0

		self.weapons_group = weapons_group

		self.previous_state = {}

		self.item_sprites = item_sprites
		self.inventory_items = {}

		super().__init__(groups)

	def process_client_updates(self, update: Client.Input.PlayerUpdate):
		self.status = update.status

		self.cooldowns()

		for attack in update.attacks:
			if attack.attack_type == 0:  # switch
				self.switch_weapon(attack.weapon_id)
			elif attack.attack_type == 1:  # attack
				if self.weapon_index not in self.on_screen:
					self.attacks.append(Client.Output.AttackUpdate(weapon_id=self.weapon_index, attack_type=1, direction=(0, 0)))
					self.create_attack(self)
					self.attacking = True
					self.attack_time = pygame.time.get_ticks()
				else:
					if self.weapon_index == 1:
						if self.can_shoot:
							self.create_bullet(self, self.current_weapon.rect.center, attack.direction)
							self.can_shoot = False
							self.shoot_time = pygame.time.get_ticks()
					elif self.weapon_index == 2:
						self.create_kettle(self, attack.direction)
						self.switch_weapon(0)

		self.update_pos(update.pos)

	def update(self):

		if self.status == 'dead':
			return

		# Death
		if self.health <= 0:
			self.xp = 0
			if self.current_weapon is not None:
				self.current_weapon.kill()
			self.status = 'dead'
			return

		self.cooldowns()

		# Pick up items
		self.item_collision()

	def cooldowns(self):
		current_time: int = pygame.time.get_ticks()

		# TODO - change this to match gabriel's changes after he fixes this to be based on ticks and not on time
		# Speed skill timers
		# if not self.can_speed:
		# 	if current_time - self.speed_start >= self.speed_time and self.is_fast:
		# 		self.speed = int(self.speed / self.speed_skill_factor)
		# 		self.is_fast = False
		# 	if current_time - self.speed_start >= self.speed_skill_cooldown:
		# 		self.can_speed = True
		#
		# # Magnet skill timers
		# if not self.can_magnet:
		# 	if current_time - self.magnet_start >= self.magnet_time and self.is_magnet:
		# 		self.is_magnet = False
		# 		self.remove(self.magnetic_players)
		# 	if current_time - self.magnet_start >= self.magnet_skill_cooldown:
		# 		self.can_magnet = True

		if self.attacking:  # TODO - make this based on ticks not time
			if current_time - self.attack_time >= self.attack_cooldown:
				self.attacking = False
				if self.weapon_index not in self.on_screen:
					self.destroy_attack()

		if not self.can_switch_weapon:
			if self.weapon_switch_time >= self.switch_duration_cooldown:
				self.can_switch_weapon = True
				self.weapon_switch_time = 0
			else:
				self.weapon_switch_time += 1

		if not self.can_shoot:
			if self.shoot_time >= self.shoot_cooldown:
				self.can_shoot = True
				self.shoot_time = 0
			else:
				self.shoot_time += 1

	def switch_weapon(self, weapon_id: int) -> None:
		"""
		switch current held weapon
		:return:
		"""

		if self.weapon_index in self.on_screen:
			self.destroy_attack()

		self.can_switch_weapon = False
		self.weapon_switch_time = pygame.time.get_ticks()
		self.weapon_index = weapon_id
		self.weapon = list(weapon_data.keys())[self.weapon_index]

		self.attacking = False

		if self.weapon_index in self.on_screen:
			self.create_attack(self)

		self.attacks.append(Client.Output.AttackUpdate(weapon_id=self.weapon_index, attack_type=0, direction=(0, 0)))

	def destroy_attack(self):
		if self.current_weapon:
			self.current_weapon.kill()
		self.current_weapon = None

	def update_pos(self, pos):
		self.rect.topleft = pos
		self.hitbox = self.rect.inflate(-20, -26)

	def deal_damage(self, damage):
		self.health -= int(damage - (0.1 * self.resistance))

	def item_collision(self):
		item: Item
		for item in self.item_sprites:
			if self.rect.colliderect(item.rect):
				if item.can_pick_up:
					if item.name == "xp":
						item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='pickup'))
						self.xp += 1
						item.die = True
					elif item.name == "grave_player" or item.name == "grave_pet":
						if len(self.inventory_items) < INVENTORY_ITEMS:
							item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='pickup'))
							self.inventory_items[item.name + f'({len(self.inventory_items)})'] = 1
							item.die = True
					else:
						if item.name in self.inventory_items:
							item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='pickup'))
							self.inventory_items[item.name] += 1
							item.die = True
						elif len(self.inventory_items) < INVENTORY_ITEMS:
							item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='pickup'))
							self.inventory_items[item.name] = 1
							item.die = True

	def reset_attacks(self):
		self.attacks: deque = deque()
