from collections import deque

import pygame
import re
from server_files_normal.game.settings import *
from server_files_normal.structures import Client


class Item(pygame.sprite.Sprite):
    def __init__(self, name, groups, pos, item_id):

        self.item_id = item_id
        self.actions: deque = deque()

        # Inventory
        self.str_name = name
        self.name = re.sub("\(.*?\)", "", name)

        # Sprite
        self.image = pygame.image.load(f'./graphics/items/{self.name}.png')
        self.rect = self.image.get_rect(center=pos)
        self.height = 1

        # Exact position so magnet movement looks better
        self.xpos = self.rect.x
        self.ypos = self.rect.y

        # Pick up cooldown
        self.spawn_time = 0
        self.pick_up_cooldown = ITEM_PICK_UP_COOLDOWN
        self.can_pick_up = False

        self.despawn_time = ITEM_DESPAWN_TIME

        self.die = False

        self.previous_pos = ()

        self.dt = 1

        self.speed = 10

        super().__init__(groups)

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
                    self.xpos -= self.speed * self.dt * abs(self.rect.x - player.rect.x) / (minvalue ** (1 / 2))
                elif self.rect.x < min_distance_player.rect.x:
                    self.xpos += self.speed * self.dt * abs(self.rect.x - player.rect.x) / (minvalue ** (1 / 2))

                if self.rect.y > min_distance_player.rect.y:
                    self.ypos -= self.speed * self.dt * abs(self.rect.y - player.rect.y) / (minvalue ** (1 / 2))
                elif self.rect.y < min_distance_player.rect.y:
                    self.ypos += self.speed * self.dt * abs(self.rect.y - player.rect.y) / (minvalue ** (1 / 2))

                self.rect.x = int(self.xpos)
                self.rect.y = int(self.ypos)

    def update(self):

        if self.spawn_time > self.pick_up_cooldown:
            self.can_pick_up = True

        if self.spawn_time > self.despawn_time:
            self.actions.append(Client.Output.ItemActionUpdate(action_type='despawn'))
            self.die = True
        else:
            self.spawn_time += self.dt

    def reset_actions(self):
        self.actions: deque = deque()

    def get_pos(self):
        return self.rect.x, self.rect.y
