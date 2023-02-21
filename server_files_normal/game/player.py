from collections import deque

import pygame
from server_files_normal import ClientManager
from server_files_normal.game.settings import *
from server_files_normal.game.weapon import Weapon
from server_files_normal.structures import *


class Player(pygame.sprite.Sprite):
	def __init__(self, groups, entity_id: int, pos: (int, int), create_bullet, create_kettle):
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
		self.shoot_cooldown = 300  # less than client cooldown, because of the possible latency

		# Switch cooldown
		self.can_switch_weapon = True
		self.weapon_switch_time = None
		self.switch_duration_cooldown = 300  # less than client cooldown, because of the possible latency

		# violence
		self.attacking: bool = False
		self.attack_cooldown: int = 300  # less than client cooldown, because of the possible latency
		self.attack_time: int = 0

		# Projectiles
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
		self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 10}  # TODO - is magic needed?
		self.health = self.stats['health']
		self.energy = self.stats['energy']
		self.xp = 0
		self.speed = self.stats['speed']
		self.strength = self.stats['attack']  # TODO - make this stat actually matter and change the damage amount
		self.resistance = 0  # TODO - make this stat actually matter and change the damage amount, MAKE ATTACKING THE PLAYER MAKE THIS GO DOWN SLIGHTLY

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
					self.create_attack()
					self.attacking = True
					self.attack_time = pygame.time.get_ticks()
				else:
					if self.weapon_index == 1:
						if self.can_shoot:
							self.create_bullet(self, attack.direction)
							self.can_shoot = False
							self.shoot_time = pygame.time.get_ticks()
					elif self.weapon_index == 2:
						self.create_kettle(self, attack.direction)
						self.switch_weapon(0)

		self.update_pos(update.pos)

	def update(self):
		self.cooldowns()

		# Death
		if self.health <= 0:
			self.xp = 0
			self.kill()
			print('he died lmao')
			# TODO Notify clients

	def cooldowns(self):
		current_time: int = pygame.time.get_ticks()

		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown and self.weapon_index not in self.on_screen:
				self.attacking = False
				self.destroy_attack()

		if not self.can_switch_weapon:
			if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
				self.can_switch_weapon = True

		if not self.can_shoot:
			if current_time - self.shoot_time >= self.shoot_cooldown:
				self.can_shoot = True

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
			self.create_attack()

		self.attacks.append(Client.Output.AttackUpdate(weapon_id=self.weapon_index, attack_type=0, direction=(0, 0)))

	def create_attack(self):
		self.current_weapon = Weapon(self, (), 2)

	def destroy_attack(self):
		if self.current_weapon:
			self.current_weapon.kill()
		self.current_weapon = None

	def update_pos(self, pos):
		self.rect.topleft = pos
		self.hitbox = self.rect.inflate(-20, -26)

	def reset_attacks(self):
		self.attacks: deque = deque()
