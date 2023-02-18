import pygame

class Circle(pygame.sprite.Sprite):
	def __init__(self, groups, radius, pos):
		super().__init__(groups)
		self.image = pygame.Surface((radius, radius))
		self.rect = self.image.get_rect(topleft=pos)
		self.height = 10
