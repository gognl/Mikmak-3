import pygame
import re
from client_files.code.settings import *


class Item(pygame.sprite.Sprite):
    def __init__(self, name, groups, pos):
        super().__init__(groups)

        # Inventory
        self.name = re.sub("\(.*?\)", "", name)

        # Sprite
        self.image = pygame.image.load(f'../graphics/items/{self.name}.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.height = 4

        # Pick up cooldown
        self.spawn_time = pygame.time.get_ticks()
        self.pick_up_cooldown = ITEM_PICK_UP_COOLDOWN
        self.can_pick_up = False

        self.despawn_time = ITEM_DESPAWN_TIME

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.spawn_time > self.pick_up_cooldown:
            self.can_pick_up = True

        if current_time - self.spawn_time > self.despawn_time:
            del self
