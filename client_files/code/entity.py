import pygame
from client_files.code.weapon import Weapon
from client_files.code.projectile import Projectile


class Entity(pygame.sprite.Sprite):
	def __init__(self, world, groups, entity_id):
		super().__init__(groups)
		self.world = world
		self.frame_index = 0
		self.animation_speed = 0.25
		self.direction = pygame.math.Vector2()
		self.entity_id = entity_id
		self.current_weapon = None

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
				if sprite.hitbox.colliderect(self.hitbox) and sprite is not self and type(sprite) is not Projectile:  # Do not collide with projects - they collide with you
					if self.direction.x > 0:  # Player going right
						self.hitbox.right = sprite.hitbox.left
					elif self.direction.x < 0:  # Player going left
						self.hitbox.left = sprite.hitbox.right
					elif hasattr(sprite, 'direction'):  # Only if sprite has direction
						if sprite.direction.x > 0:  # Sprite going right
							self.hitbox.left = sprite.hitbox.right
						elif sprite.direction.x < 0:  # Sprite going left
							self.hitbox.right = sprite.hitbox.left

		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox) and sprite is not self and type(sprite) is not Projectile:  # Do not collide with projects - they collide with you
					if self.direction.y > 0:  # Player going down
						self.hitbox.bottom = sprite.hitbox.top
					elif self.direction.y < 0:  # Player going up
						self.hitbox.top = sprite.hitbox.bottom
					elif hasattr(sprite, 'direction'):  # Only if sprite has direction
						if sprite.direction.y > 0:  # Sprite going down
							self.hitbox.top = sprite.hitbox.bottom
						elif sprite.direction.y < 0:  # Sprite going up
							self.hitbox.bottom = sprite.hitbox.top

	def create_attack(self) -> None:
		self.current_weapon = Weapon(self, [self.world.visible_sprites], 2)

	def destroy_attack(self):
		if self.current_weapon:
			self.current_weapon.kill()
		self.current_weapon = None

	def create_bullet(self):
		Projectile(self, self.world.camera, self.world.screen_center, self.current_weapon,
				   pygame.mouse.get_pos(), (self.world.visible_sprites, self.world.obstacle_sprites,
											self.world.projectile_sprites), self.world.obstacle_sprites, 3, 15, 2000,
				   '../graphics/weapons/bullet.png')

	def create_kettle(self):
		Projectile(self, self.world.camera, self.world.screen_center, self.current_weapon,
				   pygame.mouse.get_pos(), (self.world.visible_sprites, self.world.obstacle_sprites,
											self.world.projectile_sprites), self.world.obstacle_sprites, 3, 5, 750,
				   '../graphics/weapons/kettle/full.png', 'explode', True)
