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

        # Exact position so magnet movement looks better
        self.xpos = self.rect.x
        self.ypos = self.rect.y

        # Pick up cooldown
        self.spawn_time = pygame.time.get_ticks()
        self.pick_up_cooldown = ITEM_PICK_UP_COOLDOWN
        self.can_pick_up = False

    def update_movement(self, magnetic_players):
        if len(magnetic_players) != 0:
            minvalue = 0
            min_distance_player = None
            for player in magnetic_players:
                if abs(self.rect.x - player.rect.x)**2 + abs(self.rect.y - player.rect.y)**2 <= max(40000, minvalue - 1):
                    minvalue = abs(self.rect.x - player.rect.x)**2 + abs(self.rect.y - player.rect.y)**2
                    min_distance_player = player
            if min_distance_player is not None:
                if self.rect.x > min_distance_player.rect.x:
                    self.xpos -= abs(self.rect.x - player.rect.x) / (minvalue ** (1 / 2))
                elif self.rect.x < min_distance_player.rect.x:
                    self.xpos += abs(self.rect.x - player.rect.x) / (minvalue ** (1 / 2))

                if self.rect.y > min_distance_player.rect.y:
                    self.ypos -= abs(self.rect.y - player.rect.y) / (minvalue ** (1 / 2))
                elif self.rect.y < min_distance_player.rect.y:
                    self.ypos += abs(self.rect.y - player.rect.y) / (minvalue ** (1 / 2))

                self.rect.x = int(self.xpos)
                self.rect.y = int(self.ypos)




    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_time > self.pick_up_cooldown:
            self.can_pick_up = True

    def used(self):
        pass  # TODO - add uses for items
