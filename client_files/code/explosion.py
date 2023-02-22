import pygame
from client_files.code.settings import *
from client_files.code.item import Item
from client_files.code.player import Player


class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, damage, groups, sprites):
        super().__init__(groups)

        # Sprite
        self.image = pygame.image.load(f'../graphics/particles/explosion.png').convert_alpha()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=pos)
        self.height = 5

        # Explosion stats
        self.speed = EXPLOSION_SPEED
        self.radius = EXPLOSION_RADIUS

        # Damage
        self.damage = damage
        self.sprites = sprites
        self.deal_damage()

    def deal_damage(self):
        position = pygame.math.Vector2(self.rect.center[0], self.rect.center[1])
        for sprite in self.sprites:
            if position.distance_to(sprite.rect.center) <= self.radius:
                if hasattr(sprite, "health"):
                    sprite.health -= self.damage
                    if hasattr(sprite, "paused"):
                        sprite.pause()
                elif isinstance(sprite, Item):
                    sprite.kill()

    def update(self):
        self.image = pygame.transform.scale(self.original_image, (int(self.rect.width * self.speed), int(self.rect.height * self.speed)))
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.rect.width >= self.radius * 2:
            self.kill()
