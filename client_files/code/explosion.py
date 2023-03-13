import pygame

from client_files.code.settings import *
from client_files.code.item import Item


class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, damage, groups, sprites, speed=EXPLOSION_SPEED, radius=EXPLOSION_RADIUS, color='orange', player=None):
        super().__init__(groups)

        self.player = player
        # Sprite
        if color == 'orange':
            self.image = pygame.image.load(f'../graphics/particles/explosion.png').convert_alpha()
        elif color == 'blue':
            self.image = pygame.image.load(f'../graphics/particles/lightning.png').convert_alpha()
        elif color == 'gray':
            self.image = pygame.image.load(f'../graphics/particles/magnet.png').convert_alpha()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=pos)
        self.height = 5

        # Explosion stats
        self.speed = speed
        self.radius = radius

        # Damage
        self.damage = damage
        self.sprites = sprites

    def update(self):

        if self.player is not None:
            self.rect.center = self.player.rect.center

        self.image = pygame.transform.scale(self.original_image, (int(self.rect.width * self.speed), int(self.rect.height * self.speed)))
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.rect.width >= self.radius * 2:
            if self.player is not None and self.player.is_magnet:  # magnet
                self.image = self.original_image
                self.rect = self.image.get_rect(center=self.player.rect.center)
                return
            self.kill()
