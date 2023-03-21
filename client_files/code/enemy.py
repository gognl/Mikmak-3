from collections import deque

import pygame.time

from client_files.code.settings import *
from client_files.code.entity import Entity
from client_files.code.structures import NormalServer
from client_files.code.support import *


class Enemy(Entity):
	def __init__(self, enemy_name, pos, groups, entity_id, obstacle_sprites, create_explosion, create_bullet, die):

		super().__init__(groups, entity_id)
		self.status = None
		self.sprite_type = 'enemy'

		self.import_graphics(enemy_name)
		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(topleft=pos)
		self.height = 2

		self.hitbox = self.rect
		self.obstacle_sprites = obstacle_sprites

		self.enemy_name = enemy_name
		self.enemy_info = enemy_data[enemy_name]
		self.health = self.enemy_info['health']
		self.xp = self.enemy_info['xp']
		self.speed = self.enemy_info['speed']
		self.damage = self.enemy_info['damage']
		self.resistance = self.enemy_info['resistance']
		self.attack_radius = self.enemy_info['attack_radius']
		self.notice_radius = self.enemy_info['notice_radius']

		# All g
		self.create_explosion = create_explosion
		self.create_bullet = create_bullet

		self.update_queue: deque[NormalServer.Input.EnemyUpdate] = deque()

		self.die = die

	def import_graphics(self, name):
		self.animations = {'move': []}
		path = f'../graphics/monsters/{name}/move/'
		self.animations['move'] = list(import_folder(path).values())
		self.status = 'move'

	def animate(self) -> None:
		"""DFS RUN
        """
		animation: List[pygame.Surface] = self.animations[self.status]

		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# s
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center=self.hitbox.center)

	def process_server_update(self, update: NormalServer.Input.EnemyUpdate):

		self.update_pos(update.pos)

		for attack in update.attacks:
			if attack.direction == (0, 0) and self.enemy_name == 'red_cow':
				self.create_explosion(self.rect.center, self.damage)
				return 'dead'
			elif self.enemy_name == 'yellow_cow':
				self.create_bullet(self, self.rect.center, pygame.math.Vector2(attack.direction))

		if update.status == 'dead':
			return 'dead'

	def update(self):

		while self.update_queue:
			if self.process_server_update(self.update_queue.popleft()) == 'dead':
				self.die(self)
				return


class TitleEnemy(Enemy):
	def __init__(self, enemy_name, pos, groups, direction):
		super().__init__(enemy_name, pos, groups, 0, None, None, None, None)

		self.direction = direction
		self.image = self.animations['move'][0 if self.direction[0] < 0 else 1]

	def title_move(self):
		self.rect.x += self.direction[0]
