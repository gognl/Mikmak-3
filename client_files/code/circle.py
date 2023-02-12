import pygame

class Circle(pygame.sprite.Sprite):
	def __init__(self, groups, pos, color, radius):
		super().__init__(groups)

		if radius == 20:
			self.height = 5
		elif radius == 15:
			self.height = 6
		elif radius == 10:
			self.height = 7
		self.image = pygame.Surface((radius, radius)).convert_alpha()
		self.image.fill(color)
		self.rect = self.image.get_rect(topleft=pos)
