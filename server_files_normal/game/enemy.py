from collections import deque
from random import choice
from typing import List

import random
import pygame

from server_files_normal.game.item import Item
from server_files_normal.game.projectile import Projectile
from server_files_normal.game.support import import_folder
from server_files_normal.game.player import Player
from server_files_normal.game.settings import *
from server_files_normal.structures import Client
from server_files_normal.structures import Point

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_name: str, pos: (int, int), groups, entity_id: int, obstacle_sprites: pygame.sprite.Group,
                 item_sprites, create_explosion, create_bullet, get_free_item_id, layout, enemies_info=enemy_data):
        super().__init__(groups)

        self.entity_id = entity_id

        self.import_graphics(enemy_name)
        self.status = 'idle'
        self.image = self.animations['move'][0]
        self.rect = self.image.get_rect(topleft=pos)

        # Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
        self.hitbox = self.rect

        # stats
        self.enemy_name = enemy_name
        self.enemy_info = enemies_info[enemy_name]
        self.health = self.enemy_info['health']
        self.xp = self.enemy_info['xp']
        self.speed = self.enemy_info['speed']
        self.damage = self.enemy_info['damage']
        self.resistance = self.enemy_info['resistance']
        self.attack_radius = self.enemy_info['attack_radius']
        self.notice_radius = self.enemy_info['notice_radius']

        # Auto walk
        self.distance_to_destination = 0
        self.destination_position = None
        self.is_auto_walk = False
        self.moves_auto_walk = []
        self.block_cords = []
        self.is_on_tile = False
        self.is_done_x = False
        self.is_done_y = False
        self.count_times = 0
        self.path_to_tile = ()
        self.x_value = None
        self.y_value = None
        self.desired_x = None
        self.desired_y = None
        self.last_x = None
        self.last_y = None
        self.auto_count = 0
        self.rand_walk = False
        self.target = None

        # Death
        self.xp = self.enemy_info['xp']
        self.death_items = self.enemy_info['death_items']

        self.obstacle_sprites: pygame.sprite.Group = obstacle_sprites

        self.direction = pygame.math.Vector2()

        self.item_sprites = item_sprites

        # Attack cooldown
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = ENEMY_ATTACK_COOLDOWN

        # Move cooldown
        self.can_move = True
        self.move_time = 0
        self.move_cooldown = self.enemy_info['move_cooldown']

        # Attack actions
        self.create_explosion = create_explosion
        self.create_bullet = create_bullet

        self.dead = False

        self.attacks: deque[Client.Output.EnemyAttackUpdate] = deque()

        self.previous_state = {}

        self.get_free_item_id = get_free_item_id

        self.dt = 1

        self.layout = layout

    def import_graphics(self, name: str):
        self.animations = {'move': []}
        path = f'./graphics/monsters/{name}/move/'
        self.animations['move'] = list(import_folder(path).values())

    def get_closest_player(self, players: List[Player]) -> Player:
        enemy_pos = pygame.Vector2(self.rect.center)
        return min(players, key=lambda p: enemy_pos.distance_squared_to(pygame.Vector2(p.rect.center)))

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        if distance > 10:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()
        return distance, direction

    def get_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius:
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def attack(self, player):
        if self.enemy_name == "white_cow" or self.enemy_name == "green_cow":
            player.deal_damage(self.damage)
        elif self.enemy_name == "red_cow":
            self.create_explosion(self.rect.center, self.damage)
            self.attacks.append(Client.Output.EnemyAttackUpdate(direction=(0, 0)))
            self.die()
        elif self.enemy_name == "yellow_cow":
            self.create_bullet(self, self.rect.center, player.rect.center)

    def actions(self, player):
        self.target = player
        if self.status == 'attack':
            if self.can_attack:
                # TODO stop autowalk if autowalking
                self.stop_auto_walk()
                self.can_attack = False
                self.attack(player)

        elif self.status == 'move':
            if self.can_move:
                self.can_move = False
                if not self.is_auto_walk:
                    self.start_auto_walk()
                # TODO start auto walk
                self.image = self.animations['move'][0 if self.direction.x < 0 else 1]

        else:
            # TODO stop autowalk if autowalking
            self.stop_auto_walk()
            self.direction = pygame.math.Vector2()

    def stop_auto_walk(self) -> None:
        if self.is_auto_walk:
            self.is_auto_walk = False
            self.count_times = 0
            self.destination_position = None
            self.distance_to_destination = 0
            self.is_done_y = False
            self.is_done_x = False
            self.moves_auto_walk = []
            self.block_cords = []
            self.is_on_tile = False
            self.path_to_tile = []
            self.desired_x = None
            self.desired_y = None
            self.x_value = None
            self.y_value = None
            self.last_x = None
            self.last_y = None
            self.auto_count = 0

    def is_good_auto_walk(self, y: int, x: int) -> bool:
        return not (len(self.layout['floor']) > y >= 0 and len(self.layout['floor'][y]) > x >= 0 and not
                    (int(self.layout['floor'][y][x]) in SPAWNABLE_TILES and int(self.layout['objects'][y][x]) == -1))

    def start_auto_walk(self) -> None:
        self.stop_auto_walk()
        self.is_auto_walk = True
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        #x1 = pos.rect.x
        #y1 = pos.rect.y
        #x = self.rect.x
        #y = self.rect.y
        #if abs(x - x1) ** 2 + abs(y - y1) ** 2 > enemy_data[self.enemy_name]['notice_radius'] ** 2:
        #    return
        #x = int(x / 64)
        #y = int(y / 64)
        #x1 = int(x1 / 64)
        #y1 = int(y1 / 64)
        self.distance_to_destination = abs(self.target.rect.x - self.rect.x) ** 2 + abs(self.target.rect.x - self.rect.y
                                                                                        ) ** 2
        x = int(self.rect.x / 64)
        y = int(self.rect.y / 64)
        x1 = int(self.target.rect.x / 64)
        y1 = int(self.target.rect.y / 64)
        max_distance_needed = min(MAX_OBSTACLE_SIZE, 4 * int(((abs(x - x1) ** 2 + abs(y - y1) ** 2)) ** (1 / 2)) + 10)
        self.destination_position = (x1, y1)
        if self.rand_walk:
            self.rand_walk = False
            i = random.randint(0, 3)
            self.path_to_tile = directions[i]
            for j in range(0, 5):
                self.moves_auto_walk.append(directions[i])
            answer = []
            x += self.path_to_tile[0]
            y += self.path_to_tile[1]
            temp = (64 * x, 64 * y)
            for i in range(0, len(self.moves_auto_walk)):
                x += self.moves_auto_walk[len(self.moves_auto_walk) - 1 - i][0]
                y += self.moves_auto_walk[len(self.moves_auto_walk) - 1 - i][1]
                answer.append((x, y))
            for i in range(0, len(answer)):
                self.block_cords.append((answer[len(answer) - 1 - i][0] * 64, answer[len(answer) - 1 - i][1] * 64))
            self.block_cords.append(temp)
            return
        self.last_x = x
        self.last_y = y
        x_values = (max(0, min(x1, x) - max_distance_needed), min(COL_TILES - 1, max(x1, x) + max_distance_needed))
        y_values = []
        is_in_bfs = []
        if x1 > x:
            high = y
        else:
            high = y1
        plus = 1
        if x1 < x:
            plus = -1
        x3 = abs(x1 - x) + 1
        if y == y1:
            for i in range(max(0, min(x1 - max_distance_needed, x - max_distance_needed)),
                           min(COL_TILES - 1, max(x1, x) + max_distance_needed) + 1):
                y_values.append((max(0, min(y1 - max_distance_needed, y - max_distance_needed)),
                                 min(ROW_TILES - 1, max(y1, y) + max_distance_needed)))
                is_in_bfs.append([])
                for j in range(max(0, min(y1 - max_distance_needed, y - max_distance_needed)),
                               min(ROW_TILES - 1, max(y1, y) + max_distance_needed) + 1):
                    is_in_bfs[-1].append(self.is_good_auto_walk(i, j))
        else:
            y3 = (abs(y1 - y) + 1) * abs(y1 - y) / (y - y1)
            if abs(x - x1) <= 200:
                for i in range(max(0, min(x1 - max_distance_needed, x - max_distance_needed)), min(COL_TILES - 1, max(x1, x) + max_distance_needed) + 1):
                    y_values.append((max(0, min(y1 - max_distance_needed, y - max_distance_needed)), min(ROW_TILES - 1, max(y1, y) + max_distance_needed)))
                    is_in_bfs.append([])
                    for j in range(max(0, min(y1 - max_distance_needed, y - max_distance_needed)), min(ROW_TILES - 1, max(y1, y) + max_distance_needed) + 1):
                        is_in_bfs[-1].append(self.is_good_auto_walk(i, j))
            else:
                for i in range(max(0, min(x1, x) - max_distance_needed), min(COL_TILES - 1, max(x1, x) + max_distance_needed) +
                                                                       1):
                    if i < min(x1, x):
                        if x1 <= x:
                            y_values.append((max(y1 - max_distance_needed, 0), min(y1 + max_distance_needed, ROW_TILES - 1)))
                            is_in_bfs.append([])
                            for j in range(max(y1 - max_distance_needed, 0), min(y1 + max_distance_needed, ROW_TILES - 1) + 1):
                                is_in_bfs[-1].append(self.is_good_auto_walk(j, i))
                        else:
                            y_values.append((max(y - max_distance_needed, 0), min(y + max_distance_needed, ROW_TILES - 1)))
                            is_in_bfs.append([])
                            for j in range(max(y - max_distance_needed, 0), min(y + max_distance_needed, ROW_TILES - 1) + 1):
                                is_in_bfs[-1].append(self.is_good_auto_walk(j, i))
                        continue
                    elif i > max(x1, x):
                        if x1 >= x:
                            y_values.append((max(y1 - max_distance_needed, 0), min(y1 + max_distance_needed, ROW_TILES - 1)))
                            is_in_bfs.append([])
                            for j in range(max(y1 - max_distance_needed, 0), min(y1 + max_distance_needed, ROW_TILES - 1) + 1):
                                is_in_bfs[-1].append(self.is_good_auto_walk(j, i))
                        else:
                            y_values.append((max(y - max_distance_needed, 0), min(y + max_distance_needed, ROW_TILES - 1)))
                            is_in_bfs.append([])
                            for j in range(max(y - max_distance_needed, 0), min(y + max_distance_needed, ROW_TILES - 1) + 1):
                                is_in_bfs[-1].append(self.is_good_auto_walk(j, i))
                        continue
                    else:
                        high -= y3 / x3 * plus
                        y_values.append((max(int(high) - max_distance_needed, 0), min(
                            int(high) + max_distance_needed, ROW_TILES - 1)))
                        is_in_bfs.append([])
                        for j in range(max(int(high) - max_distance_needed, 0), min(
                                int(high) + max_distance_needed, ROW_TILES - 1) + 1):
                            is_in_bfs[-1].append(self.is_good_auto_walk(j, i))
        bfs_values = []
        for i in is_in_bfs:
            bfs_values.append([])
            for j in i:
                bfs_values[-1].append(1000000)
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        in_bfs = [(x1, y1)]
        bfs_values[x1 - x_values[0]][y1 - y_values[x1 - x_values[0]][0]] = 0
        count = 0
        while count != len(in_bfs):
            now = in_bfs[count]
            for i in directions:
                x4 = now[0] + i[0]
                y4 = now[1] + i[1]
                x_now = now[0] - x_values[0]
                y_now = now[1] - y_values[x_now][0]
                if x_values[0] <= x4 <= x_values[1] and y_values[x4 - x_values[0]][0] <= y4 <= \
                        y_values[x4 - x_values[0]][1] and bfs_values[x_now][y_now] + 1 < \
                        bfs_values[x4 - x_values[0]][y4 - y_values[x4 - x_values[0]][0]] \
                        and is_in_bfs[x4 - x_values[0]][y4 - y_values[x4 - x_values[0]][0]]:
                    x5 = x4 - x_values[0]
                    y5 = y4 - y_values[x5][0]
                    bfs_values[x5][y5] = bfs_values[x_now][y_now] + 1
                    in_bfs.append((x4, y4))
            count += 1
        path = []
        new_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        min_dst = 10000000
        for i in new_directions:
            min_dst = min(min_dst, bfs_values[x + i[0] - x_values[0]][y + i[1] - y_values[x + i[0] - x_values[0]][0]])
        for i in new_directions:
            if min_dst == bfs_values[x + i[0] - x_values[0]][y + i[1] - y_values[x + i[0] - x_values[0]][0]]:
                self.path_to_tile = i
                break
        if self.path_to_tile[0] > 0:
            x += 1
        if self.path_to_tile[1] > 0:
            y += 1
        x_last = x
        y_last = y
        countywet = 0
        while x_last != x1 or y_last != y1:
            for i in directions:
                now = (x_last, y_last)
                x4 = x_last + i[0]
                y4 = y_last + i[1]
                x_now = now[0] - x_values[0]
                y_now = now[1] - y_values[x_now][0]
                if x_values[0] <= x4 <= x_values[1] and y_values[x4 - x_values[0]][0] <= y4 <= \
                        y_values[x4 - x_values[0]][1]:
                    if bfs_values[x_now][y_now] - 1 == \
                            bfs_values[x4 - x_values[0]][y4 - y_values[x4 - x_values[0]][0]] and \
                            is_in_bfs[x4 - x_values[0]][y4 - y_values[x4 - x_values[0]][0]]:
                        path.append(i)
                        x_last = x4
                        y_last = y4
                        break
            countywet += 1
            if countywet == 1000:
                break
        temp_answer = []
        for i in range(0, len(path)):
            temp_answer.append((path[len(path) - 1 - i][0], path[len(path) - 1 - i][1]))
        before = False
        pos = [x, y]
        for i in range(0, len(temp_answer)):
            if before:
                before = False
                pos[0] += temp_answer[i][0]
                pos[1] += temp_answer[i][1]
                continue
            if i == len(temp_answer) - 1 or temp_answer[i] == temp_answer[i + 1]:
                self.moves_auto_walk.append(temp_answer[i])
                continue
            x_not = temp_answer[i + 1][0] + pos[0]
            y_not = temp_answer[i + 1][1] + pos[1]
            pos[0] += temp_answer[i][0]
            pos[1] += temp_answer[i][1]
            if int(self.layout['floor'][y_not][x_not]) in SPAWNABLE_TILES and int(
                    self.layout['objects'][y_not][x_not]) == -1:
                self.moves_auto_walk.append((temp_answer[i][0] + temp_answer[i + 1][0], temp_answer[i][1] +
                                             temp_answer[i + 1][1]))
                before = True
            else:
                self.moves_auto_walk.append(temp_answer[i])
        answer = []
        temp = (64 * x, 64 * y)
        for i in range(0, len(self.moves_auto_walk)):
            x += self.moves_auto_walk[len(self.moves_auto_walk) - 1 - i][0]
            y += self.moves_auto_walk[len(self.moves_auto_walk) - 1 - i][1]
            answer.append((x, y))
        for i in range(0, len(answer)):
            self.block_cords.append((answer[len(answer) - 1 - i][0] * 64, answer[len(answer) - 1 - i][1] * 64))
        self.block_cords.append(temp)

    def move_auto(self, speed: int):

        if len(self.moves_auto_walk) == 0:
            return

        # Get the direction
        if not self.is_on_tile:
            self.direction.x = self.path_to_tile[0]
            self.direction.y = self.path_to_tile[1]
        else:
            self.direction.x = self.moves_auto_walk[len(self.moves_auto_walk) - 1][0]
            self.direction.y = self.moves_auto_walk[len(self.moves_auto_walk) - 1][1]

        # Normalize direction
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Change animation
        if abs(self.direction.x) > abs(self.direction.y):
            if self.direction.x > 0:
                self.status = 'right'
            else:
                self.status = 'left'
        else:
            if self.direction.y > 0:
                self.status = 'down'
            else:
                self.status = 'up'

        # Move accordingly to the direction
        if not self.is_on_tile:
            if not self.is_done_x:
                if int((self.hitbox.x + self.direction.x * speed) / 64) == int(self.hitbox.x / 64):
                    self.hitbox.x += self.direction.x * speed
                else:
                    self.hitbox.x = self.block_cords[-1][0]
                    self.is_done_x = True
                self.collision('horizontal')  # Check collisions in the horizontal axis

            if not self.is_done_y:
                if int((self.hitbox.y + self.direction.y * speed) / 64) == int(self.hitbox.y / 64):
                    self.hitbox.y += self.direction.y * speed
                else:
                    self.hitbox.y = self.block_cords[-1][1]
                    self.is_done_y = True
                self.collision('vertical')  # Check collisions in the vertical axis

            if self.is_done_x and self.is_done_y:
                self.is_on_tile = True
                self.is_done_x = False
                self.is_done_y = False
                del (self.block_cords[-1])
        else:
            if self.direction.x == 0:
                self.is_done_x = True
            if self.direction.y == 0:
                self.is_done_y = True
            if not self.is_done_x:
                if not (max(self.hitbox.x, self.hitbox.x + self.direction.x * speed) >= self.block_cords[-1][0] > min(
                        self.hitbox.x, self.hitbox.x + self.direction.x * speed)):
                    self.hitbox.x += self.direction.x * speed
                else:
                    self.hitbox.x = self.block_cords[-1][0]
                    self.is_done_x = True
                self.collision('horizontal')  # Check collisions in the horizontal axis

            if not self.is_done_y:
                if not (max(self.hitbox.y, self.hitbox.y + self.direction.y * speed) >= self.block_cords[-1][1] > min(
                        self.hitbox.y, self.hitbox.y + self.direction.y * speed)):
                    self.hitbox.y += self.direction.y * speed
                else:
                    self.hitbox.y = self.block_cords[-1][1]
                    self.is_done_y = True
                self.collision('vertical')  # Check collisions in the vertical axis

        self.rect.center = self.hitbox.center
        if self.hitbox.x == self.block_cords[-1][0] and self.hitbox.y == self.block_cords[-1][1] and self.is_on_tile:
            del (self.moves_auto_walk[-1])
            del (self.block_cords[-1])
            self.is_done_x = False
            self.is_done_y = False
        if self.is_on_tile and len(self.moves_auto_walk) == 0:
            self.start_auto_walk()

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

    def cooldowns(self):
        if not self.can_attack:
            if self.attack_time >= self.attack_cooldown:
                self.can_attack = True
                self.attack_time = 0
            else:
                self.attack_time += self.dt

        if not self.can_move:
            if self.move_time >= self.move_cooldown:
                self.can_move = True
                self.move_time = 0
            else:
                self.move_time += self.dt

    def update(self):
        if self.dead:
            return

        if self.status == 'move':
            # TODO move_auto here
            self.move_auto(self.speed*self.dt)

        if self.health <= 0:
            self.die()

        self.cooldowns()

    def die(self):
        self.dead = True

        for i in range(min(2, len(self.death_items))):
            self.create_dropped_item(choice(self.death_items), self.rect.center, self.get_free_item_id())
        for i in range(self.xp):
            self.create_dropped_item("xp", self.rect.center, self.get_free_item_id())

        # reset stats
        self.xp = 0
        self.health = 0

    def create_dropped_item(self, name, pos, item_id):
        new_item = Item(name, (self.item_sprites,), pos, item_id)
        new_item.actions.append(Client.Output.ItemActionUpdate(player_id=self.entity_id, action_type='drop', pos=pos))

    def enemy_update(self, players):
        if self.dead or not players:
            return
        player: Player = self.get_closest_player(players)
        self.get_status(player)
        self.actions(player)

    def deal_damage(self, damage):
        self.health -= int(damage - (0.1 * self.resistance))

    def reset_attacks(self):
        self.attacks: deque[Client.Output.EnemyAttackUpdate] = deque()

    def get_pos(self):
        return Point(self.rect.x, self.rect.y)
