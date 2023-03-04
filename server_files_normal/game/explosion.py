import pygame

from server_files_normal.game.item import Item
from server_files_normal.game.settings import *


class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, damage, groups, sprites):
        super().__init__(groups)

        # Sprite
        self.image = pygame.image.load(f'./graphics/particles/explosion.png')
        self.rect = self.image.get_rect(center=pos)

        # Explosion stats
        self.radius = EXPLOSION_RADIUS

        # Damage
        self.damage = damage
        self.sprites = sprites
        self.deal_damage()
        self.kill()

    def deal_damage(self):
        position = pygame.math.Vector2(self.rect.center[0], self.rect.center[1])
        for sprite in self.sprites:
            if position.distance_to(sprite.rect.center) <= self.radius:
                if hasattr(sprite, "health"):
                    sprite.deal_damage(self.damage)
                elif isinstance(sprite, Item):
                    # TODO change this
                    sprite.kill()
