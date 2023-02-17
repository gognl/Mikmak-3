import pygame
from client_files.code.entity import Entity
from client_files.code.support import *

class OtherPlayer(Entity):
	def __init__(self, pos, groups, entity_id, obstacle_sprites):
		super().__init__(groups, entity_id)

		self.status = None
		self.sprite_type = 'enemy'

		# graphics setup
		self.import_graphics()
		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(topleft=pos)
		self.height = 1

		# Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
		self.hitbox = self.rect.inflate(-20, -26)
		self.obstacle_sprites = obstacle_sprites

		self.enemy_name = 'other_player'

	def import_graphics(self):
		path: str = '../graphics/player/'
		self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [],
							'left_idle': [], 'right_idle': []}
		for animation in self.animations.keys():
			self.animations[animation] = list(import_folder(path + animation).values())

		self.status = 'down_idle'

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

	#def update(self) -> None:
	#	pass
