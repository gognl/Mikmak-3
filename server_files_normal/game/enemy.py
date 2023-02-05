import pygame
from server_files_normal.game.support import import_folder


class Enemy(pygame.sprite.Sprite):
	def __init__(self, enemy_name: str, pos: (int, int), groups, entity_id: int):
		super().__init__(groups)

		self.entity_id = entity_id

		self.import_graphics(enemy_name)
		self.image = self.animations[self.status][0]
		self.rect = self.image.get_rect(topleft=pos)

	def import_graphics(self, name: str):
		self.animations = {'move': []}
		path = f'../graphics/monsters/{name}/move/'
		self.animations['move'] = list(import_folder(path).values())
		self.status = 'move'
