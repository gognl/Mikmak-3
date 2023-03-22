from collections import deque

import pygame.time

from client_files.code.settings import *
from client_files.code.entity import Entity
from client_files.code.structures import NormalServer
from client_files.code.support import *


class Enemy(Entity):
	def __init__(self, commp, bindion, flop, kklok, dnvm, uuu88, vd, whsdg):

		super().__init__(flop, kklok)
		self.status = None
		self.sprite_type = 'enemy'

		self.import_graphics(commp)
		self.image = self.dhsh8[self.status][self.frame_index]
		self.vbvbv = self.image.get_rect(topleft=bindion)
		self.height = 2

		self.xhchc = self.vbvbv
		self.jasjs = dnvm

		self.su8 = commp
		self.ashd = johnny[commp]
		self.oooop = self.ashd['health']
		self.ii9 = self.ashd['xp']
		self.y7sdsah = self.ashd['speed']
		self.g7akhjsdbkajs = self.ashd['damage']
		self.hdu8hsd = self.ashd['resistance']
		self.dh2wdj = self.ashd['attack_radius']
		self.udud8d = self.ashd['notice_radius']

		# All g
		self.xcvmmk = uuu88
		self.vbbbd = vd

		self.update_queue: deque[NormalServer.Input.EnemyUpdate] = deque()

		self.die = whsdg

	def import_graphics(self, name):
		self.dhsh8 = {'move': []}
		path = f'../graphics/monsters/{name}/move/'
		self.dhsh8['move'] = list(import_folder(path).values())
		self.status = 'move'

	def animate(self) -> None:
		"""DFS RUN
        """
		animation: List[pygame.Surface] = self.dhsh8[self.status]

		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# s
		self.image = animation[int(self.frame_index)]
		self.vbvbv = self.image.get_rect(center=self.xhchc.center)

	def process_server_update(self, update: NormalServer.Input.EnemyUpdate):

		self.update_pos(update.pos)

		for attack in update.attacks:
			if attack.direction == (0, 0) and self.su8 == 'red_cow':
				self.xcvmmk(self.vbvbv.center, self.g7akhjsdbkajs)
				return 'dead'
			elif self.su8 == 'yellow_cow':
				self.vbbbd(self, self.vbvbv.center, pygame.math.Vector2(attack.direction))

		if update.status == 'dead':
			return 'dead'

	def update(self):

		while self.update_queue:
			if self.process_server_update(self.update_queue.popleft()) == 'dead':
				self.die(self)
				return


class TitleEnemy(Enemy):
	def __init__(self, commp, bindion, flop, direction):
		super().__init__(commp, bindion, flop, 0, None, None, None, None)

		self.direction = direction
		self.image = self.dhsh8['move'][0 if self.direction[0] < 0 else 1]

	def title_move(self):
		self.vbvbv.x += self.direction[0]
