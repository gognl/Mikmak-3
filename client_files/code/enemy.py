import pygame
from client_files.code.settings import *
from client_files.code.entity import Entity
from client_files.code.support import *

class Enemy(Entity):
	def __init__(self, enemy_name, pos, groups):

		# general setup
		super().__init__(groups)
		self.sprite_type = 'enemy'

		# graphics setup
		self.import_graphics(enemy_name)
		self.status = 'down'
		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(topleft=pos)
		self.height = 1

	def import_graphics(self, name):

		if name == 'other_player':
			path: str = '../graphics/player/'
			self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': []}
			for animation in self.animations.keys():
				self.animations[animation] = list(import_folder(path + animation).values())
		else:
			self.animations = {'idle': [], 'move': [], 'attack': []}
			path = f'../graphics/monsters/{name}/'
			for animation in self.animations.keys():
				self.animations[animation] = list(import_folder(path + animation).values())
