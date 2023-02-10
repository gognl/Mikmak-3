import pygame
from client_files.code.settings import *


class Item(pygame.sprite.Sprite):
    def __init__(self, name, groups, pos):
        super().__init__(groups)

        # Inventory
        self.name = name

        # Sprite
        self.image = pygame.image.load(f'../graphics/items/{self.name}.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.height = 4

        # Pick up cooldown
        self.spawn_time = pygame.time.get_ticks()
        self.pick_up_cooldown = ITEM_PICK_UP_COOLDOWN
        self.can_pick_up = False

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.spawn_time > self.pick_up_cooldown:
            self.can_pick_up = True

    def used(self):
        pass  # TODO - add uses for items
