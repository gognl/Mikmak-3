from collections import deque
from typing import Union

from client_files.code.entity import Entity
from client_files.code.settings import weapon_data
from client_files.code.structures import Server
from client_files.code.support import *

class OtherPlayer(Entity):
	def __init__(self, pos, groups, entity_id, obstacle_sprites, create_attack, destroy_attack,
                 create_bullet, create_kettle, create_dropped_item):
		super().__init__(groups, entity_id)

		self.status = None
		self.sprite_type = 'enemy'

		# graphics setup
		self.import_graphics()
		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(topleft=pos)
		self.height = 2

		# Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
		self.hitbox = self.rect.inflate(-20, -26)
		self.obstacle_sprites = obstacle_sprites

		self.enemy_name = 'other_player'

		# violence
		self.attacking: bool = False
		self.attack_cooldown: int = 400
		self.attack_time: int = 0

		self.create_attack = create_attack
		self.destroy_attack = destroy_attack
		self.create_bullet = create_bullet
		self.create_kettle = create_kettle
		self.weapon_index = 0
		self.on_screen = (1, 2)  # Indices of weapons that stay on screen
		self.weapon = list(weapon_data.keys())[self.weapon_index]
		self.current_weapon = None

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

		self.create_dropped_item = create_dropped_item

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

	def process_server_update(self, update: Server.Input.PlayerUpdate) -> Union[str, None]:
		self.status = update.status

		if update.status == 'dead':
			self.xp = 0
			self.create_dropped_item("grave_player", self.rect.center)
			self.kill()
			return 'dead'

		if not self.attacking:
			for attack in update.attacks:
				if attack.attack_type == 0:  # switch
					if self.weapon_index in self.on_screen:
						self.destroy_attack(self)
					self.weapon_index = attack.weapon_id
					self.weapon = list(weapon_data.keys())[self.weapon_index]
					self.attacking = False
					if self.weapon_index in self.on_screen:
						self.create_attack(self)
				elif attack.attack_type == 1:  # attack
					if self.weapon_index not in self.on_screen:
						self.create_attack(self)
						self.attacking = True
						self.attack_time = pygame.time.get_ticks()
					else:
						if self.weapon_index == 1:
							self.create_bullet(self, self.current_weapon.rect.center, attack.direction)
						elif self.weapon_index == 2:
							self.create_kettle(self, self.current_weapon.rect.center, attack.direction)

							# switch to sword
							self.destroy_attack(self)
							self.weapon_index = 0
							self.weapon = list(weapon_data.keys())[self.weapon_index]
							self.attacking = False

		self.update_pos(update.pos)

	def update(self):

		# inputs
		while self.update_queue:
			if self.process_server_update(self.update_queue.popleft()) == 'dead':
				return

		self.cooldowns()
		self.animate()

	def cooldowns(self):
		current_time: int = pygame.time.get_ticks()
		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown and self.weapon_index not in self.on_screen:
				self.attacking = False
				self.destroy_attack(self)
