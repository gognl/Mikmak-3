import pygame


class Projectile(pygame.sprite.Sprite):
	def __init__(self, player, camera, screen_center, weapon, mouse, groups, height):
		super().__init__(groups)
		self.player = player
		self.height: int = height

		self.direction: pygame.math.Vector2 = pygame.math.Vector2(mouse[0], mouse[1]) - (player.rect.center - camera + screen_center)
		self.direction = self.direction.normalize()

		self.image: pygame.Surface = pygame.image.load('../graphics/player/down_idle/down.png').convert_alpha()
		self.rect: pygame.Rect = self.image.get_rect(center=weapon.rect.center)
		self.hitbox = self.rect
		self.speed: int = 1

		# TODO - not collide with your own bullets, not go only in integer directions, collide even when not moving

	def update(self) -> None:
		"""
		Move forwards
		:return: None
		"""
		self.move()

	def move(self) -> None:
		"""
		Move the projectile towards the direction it is going
		:return: None
		"""
		self.hitbox.x += self.direction.x * self.speed
		self.hitbox.y += self.direction.y * self.speed
		self.rect.center = self.hitbox.center
