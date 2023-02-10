import pygame
from client_files.code.settings import *
from client_files.code.entity import Entity
from client_files.code.support import *


class Enemy(Entity):
	def __init__(self, enemy_name, pos, groups, entity_id, obstacle_sprites):
		# general setup
		super().__init__(groups, entity_id)
		self.status = None
		self.sprite_type = 'enemy'

		# graphics setup
		self.import_graphics(enemy_name)
		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(topleft=pos)
		self.height = 1

		# Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
		self.hitbox = self.rect.inflate(-20, -26)
		self.obstacle_sprites = obstacle_sprites

		# stats
		self.enemy_name = enemy_name
		enemy_info = enemy_data[enemy_name]
		self.health = enemy_info['health']
		self.exp = enemy_info['exp']
		self.speed = enemy_info['speed']
		self.damage = enemy_info['damage']
		self.resistance = enemy_info['resistance']
		self.attack_radius = enemy_info['attack_radius']
		self.notice_radius = enemy_info['notice_radius']

	def import_graphics(self, name):

		if name == 'other_player':
			path: str = '../graphics/player/'
			self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [],
							   'left_idle': [], 'right_idle': []}
			for animation in self.animations.keys():
				self.animations[animation] = list(import_folder(path + animation).values())

			self.status = 'down_idle'

		else:
			self.animations = {'move': []}
			path = f'../graphics/monsters/{name}/move/'
			self.animations['move'] = list(import_folder(path).values())
			self.status = 'move'

	def animate(self) -> None:
		"""
        animate through images
        :return: None
        """
		animation: list[pygame.Surface] = self.animations[self.status]

		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# set the image
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center=self.hitbox.center)

	# TODO: different than vid @goni what does this do??
	def update_pos(self, pos: (int, int)) -> None:
		self.rect.x = pos[0]
		self.rect.y = pos[1]

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
			print('attack')
		elif self.status == 'move':
			self.direction = self.get_player_distance_direction(player)[1]
			if self.enemy_name != "other_player":
				self.image = self.animations['move'][0 if self.direction.x < 0 else 1]
		else:
			self.direction = pygame.math.Vector2()

	def update(self):
		return
		self.move(self.speed)

	def enemy_update(self, player):
		return
		self.get_status(player)
		self.actions(player)


class TitleEnemy(Enemy):
	def __init__(self, enemy_name, pos, groups, direction):
		super().__init__(enemy_name, pos, groups, 0, None)

		self.direction = direction
		self.image = self.animations['move'][0 if self.direction[0] < 0 else 1]

	def title_move(self):
		self.rect.x += self.direction[0]
