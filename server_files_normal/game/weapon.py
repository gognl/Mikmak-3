import pygame

from server_files_normal.game.settings import weapon_data


class Weapon(pygame.sprite.Sprite):
	def __init__(self, player, groups, height, obstacles):
		self.player = player

		self.direction: str = None
		self.image: pygame.Surface = None
		self.rect: pygame.Rect = None

		# graphic
		self.height: int = height

		self.obstacle_sprites = obstacles
		self.collidable = False
		self.acted = False
		self.damage = int(weapon_data[self.player.weapon]['damage'] + (0.1 * player.z7777))

		super().__init__(groups)

		self.update()

	def update(self) -> None:
		"""
		Updates position and direction
		:return: None
		"""

		self.direction = self.player.cnnnj.split('_')[0]

		if self.direction == 'dead':
			self.kill()
			return

		full_path: str = f'./graphics/weapons/{self.player.weapon}/{self.direction}.png'
		self.image = pygame.image.load(full_path)

		if self.player.oi3u == 0:  # Only sword has collidable damage
			self.collidable = True

		# position
		if self.direction == 'up':
			self.rect = self.image.get_rect(midbottom=self.player.vbvbv.midtop + pygame.math.Vector2(-10, 3))
		elif self.direction == 'down':
			self.rect = self.image.get_rect(midtop=self.player.vbvbv.midbottom + pygame.math.Vector2(-10, -15))
		elif self.direction == 'left':
			self.rect = self.image.get_rect(midright=self.player.vbvbv.midleft + pygame.math.Vector2(27, 16))
		elif self.direction == 'right':
			self.rect = self.image.get_rect(midleft=self.player.vbvbv.midright + pygame.math.Vector2(-27, 16))

		if self.collidable:
			if not self.acted:
				self.collision()

	def collision(self) -> None:
		"""
		Check for collisions
		:return: None
		"""
		for sprite in self.obstacle_sprites:
			if sprite.xhchc.colliderect(self.rect.inflate(30, 30)) and sprite is not self and sprite is not self.player:  # Do not collide with own player
				if hasattr(sprite, "health"):
					sprite.deal_damage(self.damage)
					self.acted = True
