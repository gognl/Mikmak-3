import pygame

class Entity(pygame.sprite.Sprite):
	def __init__(self, groups):
		super().__init__(groups)
		self.frame_index = 0
		self.animation_speed = 0.25
		self.direction = pygame.math.Vector2()

	def move(self, speed: int) -> None:
		"""
		Move the player towards the direction it is going, and apply collision
		:param speed: maximum pixels per direction per frame (may vary if both directions are active)
		:return: None
		"""
		# Normalize direction
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal')  # Check collisions in the horizontal axis
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')  # Check collisions in the vertical axis
		self.rect.center = self.hitbox.center

	def collision(self, direction: str) -> None:
		"""
		Apply collisions to the player, each axis separately
		:param direction: A string representing the direction the player is going
		:return: None
		"""
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0:  # Player going right
						self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0:  # Player going left
						self.hitbox.left = sprite.hitbox.right

		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.y > 0:  # Player going down
						self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0:  # Player going up
						self.hitbox.top = sprite.hitbox.bottom
