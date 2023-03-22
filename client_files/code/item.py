from collections import deque

import pygame
import re
from client_files.code.settings import *
from client_files.code.structures import NormalServer

class Item(pygame.sprite.Sprite):
    def __init__(self, item_id, name, groups, pos, item_despawn=None, item_pickup=None, item_drop=None, item_use=None):
        super().__init__(groups)

        self.name = re.sub("\(.*?\)", "", name)
        self.item_id = item_id

        self.image = pygame.image.load(f'../graphics/items/{self.name}.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.height = 1

        self.xpos = self.rect.x
        self.ypos = self.rect.y
        self.spawn_time = 0
        self.pick_up_cooldown = jony
        self.can_pick_up = False

        self.despawn_time = jhony

        self.update_queue: deque = deque()

        self.item_despawn = item_despawn
        self.item_pickup = item_pickup
        self.item_drop = item_drop
        self.item_use = item_use

    def update_movement(self, magnetic_players):
        if len(magnetic_players) != 0:
            minvalue = 0
            min_distance_player = None
            for player in magnetic_players:
                if abs(self.rect.x - player.vbvbv.x)**2 + abs(self.rect.y - player.vbvbv.y)**2 <= max(40000, minvalue - 1):
                    minvalue = abs(self.rect.x - player.vbvbv.x) ** 2 + abs(self.rect.y - player.vbvbv.y) ** 2
                    min_distance_player = player
            if min_distance_player is not None:
                if self.rect.x > min_distance_player.rect.x:
                    self.xpos -= abs(self.rect.x - player.vbvbv.x) / (minvalue ** (1 / 2))
                elif self.rect.x < min_distance_player.rect.x:
                    self.xpos += abs(self.rect.x - player.vbvbv.x) / (minvalue ** (1 / 2))

                if self.rect.y > min_distance_player.rect.y:
                    self.ypos -= abs(self.rect.y - player.vbvbv.y) / (minvalue ** (1 / 2))
                elif self.rect.y < min_distance_player.rect.y:
                    self.ypos += abs(self.rect.y - player.vbvbv.y) / (minvalue ** (1 / 2))

                self.rect.x = int(self.xpos)
                self.rect.y = int(self.ypos)

    def process_server_update(self, action: NormalServer.Input.ItemActionUpdate):
        action_type = action.action_type
        if action_type == 'spawn':
            self.rect = self.image.get_rect(center=action.pos)
        elif action_type == 'despawn':
            self.item_despawn(self)
        elif action_type == 'pickup':
            self.item_pickup(self, action.player_id)
        elif action_type == 'drop':
            self.item_drop(self, action.player_id, action.pos)
        elif action_type == 'use':
            self.item_use(self, action.player_id, action.pos)
        elif action_type == 'move':
            self.rect = self.image.get_rect(center=action.pos)

    def update(self):
        while self.update_queue:
            self.process_server_update(self.update_queue.popleft())

        '''if self.spawn_time > self.pick_up_cooldown:
            self.can_pick_up = True

        if self.spawn_time > self.despawn_time:
            del self

        self.spawn_time += 1'''
