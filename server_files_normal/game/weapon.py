import pygame


class Weapon(pygame.sprite.Sprite):
	def __init__(self, player, groups, height):
		super().__init__(groups)
		self.player = player

		self.direction: str = None
		self.image: pygame.Surface = None
		self.rect: pygame.Rect = None

		# graphic
		self.height: int = height

		self.direction = self.player.status.split('_')[0]

		full_path: str = f'./graphics/weapons/{self.player.weapon}/{self.direction}.png'
		self.image = pygame.image.load(full_path)

		# position
		if self.direction == 'up':
			self.rect = self.image.get_rect(midbottom=self.player.rect.midtop + pygame.math.Vector2(-10, 3))
		elif self.direction == 'down':
			self.rect = self.image.get_rect(midtop=self.player.rect.midbottom + pygame.math.Vector2(-10, -15))
		elif self.direction == 'left':
			self.rect = self.image.get_rect(midright=self.player.rect.midleft + pygame.math.Vector2(27, 16))
		elif self.direction == 'right':
			self.rect = self.image.get_rect(midleft=self.player.rect.midright + pygame.math.Vector2(-27, 16))
