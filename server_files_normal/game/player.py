from collections import deque
from time import time

import pygame
from pygame.math import Vector2

from server_files_normal import ClientManager
from server_files_normal.game.settings import *
from server_files_normal.structures import *
from server_files_normal.game.item import Item


class Player(pygame.sprite.Sprite):
    def __init__(self, groups, entity_id: int, pos: (int, int), health, resistance,
                 strength, xp, inventory, create_bullet, create_kettle, weapons_group,
                 create_attack, item_sprites, get_free_item_id, spawn_enemy_from_egg,
                 magnetic_players, activate_lightning, layout):
                 
        self.client_manager: ClientManager = None
        self.entity_id = entity_id

        # Load player sprite from files
        self.image: pygame.Surface = pygame.image.load('./graphics/player/down_idle/down.png')

        # Position of player
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-20, -26)

        # Animations
        self.status = 'down'

        # Shooting cooldown
        self.can_shoot = True
        self.shoot_time = None
        self.shoot_cooldown = 1

        # Switch cooldown
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 1.5

        # violence
        self.attacking: bool = False
        self.attack_cooldown = 0.5
        self.attack_time: int = 0

        # Projectiles
        self.create_attack = create_attack
        self.create_bullet = create_bullet
        self.create_kettle = create_kettle

        # Weapons
        self.weapon_index = 0
        self.on_screen = (1, 2)  # Indices of weapons that stay on screen
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.current_weapon = None

        self.attacks: deque = deque()

        # updates queue
        self.update_queue: deque = deque()

        # Stats
        self.stats = {'health': health, 'energy': 60, 'attack': strength, 'speed': 10}
        self.health = self.stats['health']
        self.max_energy = self.stats['energy']
        self.energy = self.max_energy
        self.xp = xp
        self.speed = self.stats['speed']
        self.strength = self.stats['attack']
        self.resistance = resistance

        self.weapons_group = weapons_group

        self.previous_state = {}

        self.item_sprites = item_sprites

        self.inventory_items = inventory

        self.get_free_item_id = get_free_item_id

        self.dead = False

        self.spawn_enemy_from_egg = spawn_enemy_from_egg

        # Speed skill
        self.can_speed = True
        self.is_fast = False
        self.speed_start = None
        self.speed_time = 3
        self.speed_skill_cooldown = 20
        self.speed_skill_factor = 2
        self.speed_cost = 40

        # Magnet skill
        self.can_magnet = True
        self.is_magnet = False
        self.magnet_start = None
        self.magnet_time = 10
        self.magnet_skill_cooldown = 40
        self.magnetic_players = magnetic_players
        self.magnet_cost = 20

        # Lightning skill
        self.can_lightning = True
        self.lightning_start = 0
        self.lightning_skill_cooldown = 30
        self.activate_lightning = activate_lightning
        self.lightning_cost = 30

        # Energy
        self.can_energy = True
        self.energy_cooldown = 6
        self.energy_time = 0
        self.energy_point_cooldown = 5
        self.energy_point_time = 0

        self.disconnected = False

        self.dt = 1

        self.free_item_ids = []

        self.time_since_last_update = time()

        self.layout = layout

        super().__init__(groups)

    def process_client_updates(self, update: Client.Input.PlayerUpdate):

        if self.dead:
            return

        # Anti-cheat
        pos = Vector2(self.rect.topleft)
        current_time = time()
        if current_time != self.time_since_last_update:
            speed = pos.distance_to(update.pos)/(current_time - self.time_since_last_update)
            if (speed > MAX_SPEED and not self.is_fast) or (speed > self.speed_skill_factor*MAX_SPEED and self.is_fast):
                self.client_manager.hack_points -= 1
            self.time_since_last_update = current_time

        # Check that the player isn't on water or obstacles
        player_center_tile = ((update.pos[0]+32)//64, (update.pos[1]+32)//64)
        if int(self.layout['floor'][player_center_tile[1]][player_center_tile[0]]) in SPAWNABLE_TILES and int(
                self.layout['objects'][player_center_tile[1]][player_center_tile[0]]) == -1:
            self.update_pos(update.pos)
        else:
            self.client_manager.hack_points -= 2

        self.status = update.status

        self.cooldowns()

        for attack in update.attacks:
            if attack.attack_type == 0:  # switch
                self.switch_weapon(attack.weapon_id)
            elif attack.attack_type == 1:  # attack
                if self.attacking:
                    self.client_manager.hack_points -= 0.5
                if self.weapon_index not in self.on_screen:
                    self.attacks.append(Client.Output.AttackUpdate(weapon_id=self.weapon_index, attack_type=1, direction=(0, 0)))
                    self.create_attack(self)
                    self.attacking = True
                    self.attack_time = 0
                else:
                    if self.weapon_index == 1:
                        if self.can_shoot:
                            self.create_bullet(self, self.current_weapon.rect.center, attack.direction)
                            self.can_shoot = False
                            self.shoot_time = 0
                    elif self.weapon_index == 2:
                        self.attacking = True
                        self.attack_time = 0

                        self.create_kettle(self, self.current_weapon.rect.center, attack.direction)

                        self.inventory_items['kettle'] -= 1
                        if self.inventory_items['kettle'] == 0:
                            del self.inventory_items['kettle']

                        if 'kettle' not in self.inventory_items:
                            self.switch_weapon(0)

        for item_action in update.item_actions:
            if item_action.action_type == 'use':
                item_name = item_action.item_name
                used = True
                if item_name == "heal":
                    self.health += 20
                    if self.health > MAX_PLAYER_HEALTH:
                        self.health = MAX_PLAYER_HEALTH
                elif item_name == "strength":
                    self.strength += 1
                elif item_name == "kettle":
                    if self.weapon_index != 2:
                        self.switch_weapon(2)
                    used = False
                elif item_name == "shield":
                    self.resistance += 1
                elif item_name == "spawn_white":
                    self.spawn_enemy_from_egg(self.rect.topleft, "white_cow")
                elif item_name == "spawn_green":
                    self.spawn_enemy_from_egg(self.rect.topleft, "green_cow")
                elif item_name == "spawn_red":
                    self.spawn_enemy_from_egg(self.rect.topleft, "red_cow")
                elif item_name == "spawn_yellow":
                    self.spawn_enemy_from_egg(self.rect.topleft, "yellow_cow")

                if used:
                    # remove the item from the player's inventory
                    self.inventory_items[item_action.item_name] -= 1
                    if self.inventory_items[item_action.item_name] == 0:
                        del self.inventory_items[item_action.item_name]

            elif item_action.action_type == 'drop' and self.inventory_items[item_action.item_name] > 0:
                if item_action.item_id in self.free_item_ids:
                    self.free_item_ids.remove(item_action.item_id)
                    self.create_dropped_item(item_action.item_name, (self.rect.centerx, self.rect.centery), item_action.item_id)
                    self.inventory_items[item_action.item_name] -= 1
                    if self.inventory_items[item_action.item_name] == 0:
                        if item_action.item_name == "kettle" and self.weapon_index == 2:
                            self.switch_weapon(0)
                        del self.inventory_items[item_action.item_name]
                else:
                    self.client_manager.hack_points -= 3

            elif item_action.action_type == 'skill':
                if item_action.item_id == 1:  # speed
                    if self.can_speed and self.energy >= self.speed_cost:
                        self.can_speed = False
                        self.is_fast = True
                        self.speed *= self.speed_skill_factor
                        self.speed_start = 0
                        self.attacks.append(Client.Output.AttackUpdate(weapon_id=0, attack_type=4, direction=(0, 0)))
                        self.energy -= self.speed_cost
                        self.can_energy = False
                    else:
                        self.client_manager.hack_points -= 1
                elif item_action.item_id == 2:  # magnet
                    if self.can_magnet and self.energy >= self.magnet_cost:
                        self.can_magnet = False
                        self.add(self.magnetic_players)
                        self.is_magnet = True
                        self.magnet_start = 0
                        self.attacks.append(Client.Output.AttackUpdate(weapon_id=0, attack_type=3, direction=(0, 0)))
                        self.energy -= self.magnet_cost
                        self.can_energy = False
                    else:
                        self.client_manager.hack_points -= 1
                elif item_action.item_id == 3:  # damage
                    if self.can_lightning and self.energy >= self.lightning_cost:
                        self.can_lightning = False
                        self.lightning_start = 0
                        self.activate_lightning(self)
                        self.attacks.append(Client.Output.AttackUpdate(weapon_id=0, attack_type=2, direction=(0, 0)))
                        self.energy -= self.lightning_cost
                        self.can_energy = False
                    else:
                        self.client_manager.hack_points -= 1

    def die(self):
        self.dead = True

        # kill weapon
        if self.current_weapon is not None:
            self.current_weapon.kill()

        # drop inventory items
        for item in list(self.inventory_items.keys()):
            for i in range(self.inventory_items[item]):
                self.create_dropped_item(item, self.rect.center, self.get_free_item_id())
        self.inventory_items = {}

        # drop xp
        for i in range(self.xp):
            self.create_dropped_item("xp", self.rect.center, self.get_free_item_id())

        # drop grave
        self.create_dropped_item("grave_player(0)", self.rect.center, self.get_free_item_id())

        # reset stats
        self.xp = 0
        self.health = 0

    def update(self):

        if self.dead:
            return

        # Death
        if self.health <= 0:
            self.die()
            return

        self.cooldowns()

        # Pick up items
        self.item_collision()

    def cooldowns(self):

        # Energy
        if not self.can_energy:
            if self.energy_time >= self.energy_cooldown:
                self.can_energy = True
                self.energy_time = 0
            else:
                self.energy_time += self.dt
        elif self.energy < self.max_energy:
            if self.energy_point_time >= self.energy_point_cooldown:
                self.energy += 1
                self.energy_point_time = 0
            else:
                self.energy_point_time += self.dt

        # Speed skill timers
        if not self.can_speed:
            if self.speed_start >= self.speed_time and self.is_fast:
                self.speed = int(self.speed / self.speed_skill_factor)
                self.is_fast = False
            elif self.speed_start >= self.speed_skill_cooldown:
                self.can_speed = True
                self.speed_start = 0
            else:
                self.speed_start += self.dt
        
        # Magnet skill timers
        if not self.can_magnet:
            if self.magnet_start >= self.magnet_time and self.is_magnet:
                self.is_magnet = False
                self.remove(self.magnetic_players)
            elif self.magnet_start >= self.magnet_skill_cooldown:
                self.can_magnet = True
                self.magnet_start = 0
            else:
                self.magnet_start += self.dt

        # Lightning skill timers
        if not self.can_lightning:
            if self.lightning_start >= self.lightning_skill_cooldown:
                self.can_lightning = True
                self.lightning_start = 0
            else:
                self.lightning_start += self.dt

        if self.attacking:
            if self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.attack_time = 0
                if self.weapon_index not in self.on_screen:
                    self.destroy_attack()
            else:
                self.attack_time += self.dt

        if not self.can_switch_weapon:
            if self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True
                self.weapon_switch_time = 0
            else:
                self.weapon_switch_time += self.dt

        if not self.can_shoot:
            if self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True
                self.shoot_time = 0
            else:
                self.shoot_time += self.dt

    def switch_weapon(self, weapon_id: int) -> None:
        """
        switch current held weapon
        :return:
        """

        if self.weapon_index in self.on_screen:
            self.destroy_attack()

        self.can_switch_weapon = False
        self.weapon_switch_time = 0
        self.weapon_index = weapon_id
        self.weapon = list(weapon_data.keys())[self.weapon_index]

        self.attacking = False

        if self.weapon_index in self.on_screen:
            self.create_attack(self)

        # if switched to kettle and have no kettle, reswitch
        if self.weapon_index == 2 and 'kettle' not in self.inventory_items:
            self.switch_weapon(0)

        self.attacks.append(Client.Output.AttackUpdate(weapon_id=self.weapon_index, attack_type=0, direction=(0, 0)))

    def destroy_attack(self):
        if self.current_weapon:
            self.current_weapon.kill()
        self.current_weapon = None

    def update_pos(self, pos):
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(-20, -26)

    def deal_damage(self, damage):
        self.health -= int(damage - (0.1 * self.resistance))
        if self.health < 0:
            self.health = 0

    def item_collision(self):
        item: Item
        for item in self.item_sprites:
            if item.die:
                continue
            if self.rect.colliderect(item.rect):
                if item.can_pick_up:
                    if item.name == "xp":
                        item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='pickup'))
                        self.xp += 1
                        item.die = True
                    elif item.name == "grave_player":
                        if len(self.inventory_items) < INVENTORY_ITEMS:
                            item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='pickup'))
                            self.inventory_items[item.name + f'({len(self.inventory_items)})'] = 1
                            item.die = True
                    else:
                        if item.name in self.inventory_items:
                            item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='pickup'))
                            self.inventory_items[item.name] += 1
                            item.die = True
                        elif len(self.inventory_items) < INVENTORY_ITEMS:
                            item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='pickup'))
                            self.inventory_items[item.name] = 1
                            item.die = True
                    self.free_item_ids.append(item.item_id)

    def create_dropped_item(self, name, pos, item_id):
        new_item = Item(name, (self.item_sprites,), pos, item_id)
        new_item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='drop', pos=pos))

    def reset_attacks(self):
        self.attacks: deque = deque()

    def get_pos(self):
        return Point(self.rect.x, self.rect.y)
