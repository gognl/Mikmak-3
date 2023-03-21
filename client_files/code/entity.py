import pygame
from client_files.code.projectile import Projectile


class Entity(pygame.sprite.Sprite):
	def __init__(self, groups, entity_id, nametag=False, name=None, create_nametag=None, nametag_update=None):
		super().__init__(groups)
		self.frame_index = 0
		self.animation_speed = 0.25
		self.direction = pygame.math.Vector2()
		self.entity_id = entity_id

		if nametag:
			self.name = name

		self.create_nametag = create_nametag
		self.nametag_update = nametag_update
		self.nametag = None

	def initialize_nametag(self):
		self.nametag = self.create_nametag(self, self.name)

	def move(self, speed: int) -> None:
		"""
		ffsdfasdf
		"""
		# sd
		if self.nametag is not None:
			self.nametag_update(self.nametag)

		# a
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal')
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')
		self.rect.center = self.hitbox.center

	def collision(self, direction: str) -> None:
		"""
		Eat the cgame
		"""
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox) and sprite is not self and type(sprite) is not Projectile:  # TODO - add a water feautre
					if self.direction.x > 0:
						self.hitbox.right = sprite.hitbox.left
					elif self.direction.x < 0:
						self.hitbox.left = sprite.hitbox.right
					elif hasattr(sprite, 'direction'):
						if sprite.direction.x > 0:
							self.hitbox.left = sprite.hitbox.right
						elif sprite.direction.x < 0:
							self.hitbox.right = sprite.hitbox.left

		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox) and sprite is not self and type(sprite) is not Projectile:  # Do not collide with projectiles - they collide with you
					if self.direction.y > 0:  # Player going down
						self.hitbox.bottom = sprite.hitbox.top
					elif self.direction.y < 0:  # Player going up
						self.hitbox.top = sprite.hitbox.bottom
					elif hasattr(sprite, 'direction'):  # Only if sprite has direction
						if sprite.direction.y > 0:  # Sprite going down
							self.hitbox.top = sprite.hitbox.bottom
						elif sprite.direction.y < 0:  # Sprite going up
							self.hitbox.bottom = sprite.hitbox.top

	def deal_damage(self, damage):
		if hasattr(self, "health") and hasattr(self, "resistance"):
			self.health -= int(damage - (0.1 * self.resistance))
		else:
			print("Doesn't have health / resistance attribute")

	def update_pos(self, pos):
		self.rect.topleft = pos
		self.hitbox = self.rect.inflate(-20, -26)
