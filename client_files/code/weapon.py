import pygame


class Weapon(pygame.sprite.Sprite):
	def __init__(self, player, groups, height):
		super().__init__(groups)
		# graphic
		self.height = height
		self.image = pygame.Surface((40, 40))
		print("here")
		# position
		self.rect = self.image.get_rect(center=player.rect.center)

