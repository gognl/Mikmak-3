import random
from collections import deque
from typing import Dict, Sequence, Tuple

from client_files.code.explosion import Explosion
from client_files.code.settings import *
from client_files.code.structures import Server, InventorySlot
from client_files.code.support import *
from client_files.code.entity import Entity


class Player(Entity):
    def __init__(self, name, pos, groups, obstacle_sprites, height, create_attack, destroy_attack,
                 create_bullet, create_kettle, create_inventory, destroy_inventory, create_chat,
                 destroy_chat, activate_zen, deactivate_zen, create_minimap, destroy_minimap, create_nametag,
                 nametag_update, get_inventory_box_pressed, create_dropped_item, spawn_enemy_from_egg, entity_id,
                 magnetic_players, layout, create_lightning) -> None:
        super().__init__(groups, entity_id, True, name, create_nametag, nametag_update)

        # Player name TODO: might be temporary
        self.name = name

        # sprite group of magnetic players
        self.magnetic_players = magnetic_players

        # Load player sprite from files
        self.image: pygame.Surface = pygame.image.load('../graphics/player/down_idle/down.png').convert_alpha()

        # Position of player
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)

        # Height of the player on screen - 0 is background
        self.height: int = height

        # Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
        self.hitbox = self.rect.inflate(-20, -26)

        # Obstacle sprites for the player to check collisions
        self.obstacle_sprites: pygame.Group = obstacle_sprites

        # Attacking
        self.attacking: bool = False
        self.attack_cooldown = 0.5
        self.attack_time: int = 0

        # layout
        self.layout = layout

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.create_bullet = create_bullet
        self.create_kettle = create_kettle
        self.weapon_index = 0
        self.on_screen = [1, 2]  # Indices of weapons that stay on screen
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = 0
        self.switch_duration_cooldown = 1.5
        # attack sprites
        self.current_weapon = None

        # Auto walk
        self.is_auto_walk = False
        self.moves_auto_walk = []
        self.is_on_tile = False
        self.is_done_x = False
        self.is_done_y = False
        self.path_to_tile = ()
        self.x_value = None
        self.y_value = None
        self.desired_x = None
        self.desired_y = None
        self.last_x = None
        self.last_y = None
        self.auto_count = 0
        self.rand_walk = False

        # Animations
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.import_player_assets()
        self.status = 'down'

        # Server
        self.attacks: deque = deque()
        self.item_actions: deque = deque()  # also used as skills update
        self.changes = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.status, 'item_actions': tuple(self.item_actions)}  # Changes made in this tick

        # Stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 0, 'speed': 400}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.max_energy = self.stats['energy']
        self.xp = 0
        self.speed = self.stats['speed']
        self.strength = self.stats['attack']
        self.resistance = 0

        # Nametag
        self.initialize_nametag()

        # Shooting cooldown
        self.can_shoot = True
        self.shoot_time = 0
        self.shoot_cooldown = 1

        # Mouse press
        self.release_mouse = [False, False]

        # Magnet skill
        self.can_magnet = True
        self.is_magnet = False
        self.magnet_start = 0
        self.magnet_time = 10
        self.magnet_skill_cooldown = 40
        self.magnet_cost = 20

        # Speed skill
        self.can_speed = True
        self.is_fast = False
        self.speed_start = 0
        self.speed_time = 3
        self.speed_skill_cooldown = 20
        self.speed_skill_factor = 2
        self.speed_cost = 40

        # Lightning skill
        self.can_lightning = True
        self.lightning_start = 0
        self.lightning_skill_cooldown = 30
        self.lightning_cost = 30
        self.create_lightning = create_lightning

        # Inventory
        self.create_inventory = create_inventory
        self.destroy_inventory = destroy_inventory
        self.inventory_active: bool = False
        self.can_change_inventory: bool = True
        self.inventory_time: int = 0
        self.inventory_cooldown: int = 6
        self.last_inventory: bool = True

        # Chat
        self.create_chat = create_chat
        self.destroy_chat = destroy_chat
        self.last_chat = True
        self.chat_time = 0
        self.chat_cooldown = 6
        self.chat_active = False
        self.can_change_chat = True

        # Zen
        self.activate_zen = activate_zen
        self.deactivate_zen = deactivate_zen
        self.last_zen = True
        self.zen_time = 0
        self.zen_cooldown = 6
        self.zen_active = False
        self.can_change_zen = True

        # Minimap
        self.create_minimap = create_minimap
        self.destroy_minimap = destroy_minimap
        self.last_minimap = True
        self.minimap_time = 0
        self.minimap_cooldown = 6
        self.minimap_active = False
        self.can_change_minimap = True

        # Items
        self.item_sprites = None
        self.inventory_items: Dict[str, InventorySlot] = {}
        self.get_inventory_box_pressed = get_inventory_box_pressed
        self.create_dropped_item = create_dropped_item
        self.spawn_enemy_from_egg = spawn_enemy_from_egg

        # Energy
        self.can_energy = True
        self.energy_cooldown = 6
        self.energy_time = 0
        self.energy_point_cooldown = 5
        self.energy_point_time = 0

        self.dt = 1

        self.inputs_disabled: bool = False

    def import_player_assets(self) -> None:
        """
        Import all player assets
        :return: None
        """
        path: str = '../graphics/player/'

        self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [],
                           'left_idle': [], 'right_idle': []}
        for animation in self.animations.keys():
            self.animations[animation] = list(import_folder(path + animation).values())

    def stop_auto_walk(self) -> None:
        if self.is_auto_walk:
            self.is_auto_walk = False
            self.is_done_y = False
            self.is_done_x = False
            self.moves_auto_walk = []
            self.is_on_tile = False
            self.path_to_tile = []
            self.desired_x = None
            self.desired_y = None
            self.x_value = None
            self.y_value = None
            self.last_x = None
            self.last_y = None
            self.auto_count = 0

    def is_good_auto_walk(self, y: int, x: int, y_place: int, x_place: int) -> bool:
        temp = True
        for i in range(-3, 4):
            for j in range(-3, 4):
                if j + y == y_place and i + x == x_place:
                    return True
        for i in range(-1, 2):
            for j in range(-1, 2):
                if len(self.layout['floor']) > y + j >= 0 and len(self.layout['floor'][y + j]) > x + i >= 0 and \
                    not (int(self.layout['floor'][y + j][x + i]) in SPAWNABLE_TILES and
                              int(self.layout['objects'][y + j][x + i]) == -1):
                    temp = False
        return temp

    def start_auto_walk(self) -> None:
        self.stop_auto_walk()
        self.is_auto_walk = True
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        if self.rand_walk:
            self.rand_walk = False
            i = random.randint(0, 3)
            self.path_to_tile = directions[i]
            for j in range(0, 5):
                self.moves_auto_walk.append(directions[i])
            return
        x = self.rect.x
        y = self.rect.y
        self.last_x = x
        self.last_y = y
        x = int(x / 64)
        y = int(y / 64)
        x1 = 0
        y1 = 0
        while not (int(self.layout['floor'][y1][x1]) in SPAWNABLE_TILES and int(self.layout['objects'][y1][x1]) == -1
                   and abs(x - x1) >= 200):
            x1 = random.randint(0, 1280 * 40 // 64 - 1)
            y1 = random.randint(0, 720 * 40 // 64 - 1)
        x_values = (max(0, min(x1, x) - MAX_OBSTACLE_SIZE), min(COL_TILES - 1, max(x1, x) + MAX_OBSTACLE_SIZE))
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
        y3 = (abs(y1 - y) + 1) * abs(y1 - y) / (y - y1)
        for i in range(max(0, min(x1, x) - MAX_OBSTACLE_SIZE), min(COL_TILES - 1, max(x1, x) + MAX_OBSTACLE_SIZE) + 1):
            if i < min(x1, x):
                if x1 <= x:
                    y_values.append((max(y1 - MAX_OBSTACLE_SIZE, 0), min(y1 + MAX_OBSTACLE_SIZE, ROW_TILES - 1)))
                    is_in_bfs.append([])
                    for j in range(max(y1 - MAX_OBSTACLE_SIZE, 0), min(y1 + MAX_OBSTACLE_SIZE, ROW_TILES - 1) + 1):
                        is_in_bfs[-1].append(self.is_good_auto_walk(j, i, y, x))
                else:
                    y_values.append((max(y - MAX_OBSTACLE_SIZE, 0), min(y + MAX_OBSTACLE_SIZE, ROW_TILES - 1)))
                    is_in_bfs.append([])
                    for j in range(max(y - MAX_OBSTACLE_SIZE, 0), min(y + MAX_OBSTACLE_SIZE, ROW_TILES - 1) + 1):
                        is_in_bfs[-1].append(self.is_good_auto_walk(j, i, y, x))
                continue
            elif i > max(x1, x):
                if x1 >= x:
                    y_values.append((max(y1 - MAX_OBSTACLE_SIZE, 0), min(y1 + MAX_OBSTACLE_SIZE, ROW_TILES - 1)))
                    is_in_bfs.append([])
                    for j in range(max(y1 - MAX_OBSTACLE_SIZE, 0), min(y1 + MAX_OBSTACLE_SIZE, ROW_TILES - 1) + 1):
                        is_in_bfs[-1].append(self.is_good_auto_walk(j, i, y, x))
                else:
                    y_values.append((max(y - MAX_OBSTACLE_SIZE, 0), min(y + MAX_OBSTACLE_SIZE, ROW_TILES - 1)))
                    is_in_bfs.append([])
                    for j in range(max(y - MAX_OBSTACLE_SIZE, 0), min(y + MAX_OBSTACLE_SIZE, ROW_TILES - 1) + 1):
                        is_in_bfs[-1].append(self.is_good_auto_walk(j, i, y, x))
                continue
            else:
                high -= y3 / x3 * plus
                y_values.append((max(int(high) - MAX_OBSTACLE_SIZE, 0), min(
                    int(high) + MAX_OBSTACLE_SIZE, ROW_TILES - 1)))
                is_in_bfs.append([])
                for j in range(max(int(high) - MAX_OBSTACLE_SIZE, 0), min(
                        int(high) + MAX_OBSTACLE_SIZE, ROW_TILES - 1) + 1):
                    is_in_bfs[-1].append(self.is_good_auto_walk(j, i, y, x))
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
        mini = 1000000
        i = random.randint(0, 3)
        self.path_to_tile = new_directions[i]
        x += self.path_to_tile[0]
        y += self.path_to_tile[1]
        x_last = x
        y_last = y
        while x_last != x1 and y_last != y1:
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

    def move_auto(self, speed: int):
        # Update name tag right after moving
        if self.nametag is not None:
            self.nametag_update(self.nametag)

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
            if self.direction.x == 0 or (self.hitbox.centerx - 32) % 64 == 0:
                self.is_done_x = True
            if self.direction.y == 0 or (self.hitbox.centery - 32) % 64 == 0:
                self.is_done_y = True
            if not self.is_done_x and self.direction.x < 0:
                if int((self.hitbox.x + self.direction.x * speed) / 64) == int(self.hitbox.x / 64):
                    self.hitbox.x += self.direction.x * speed
                else:
                    self.hitbox.x -= (self.hitbox.centerx - 32) % 64
                    self.is_done_x = True
            elif not self.is_done_x:
                if int((self.hitbox.x + self.direction.x * speed) / 64) == int(self.hitbox.x / 64):
                    self.hitbox.x += self.direction.x * speed
                else:
                    self.hitbox.x = int((self.hitbox.x + self.direction.x * speed) / 64) * 64
                    self.is_done_x = True
            if not self.is_done_y and self.direction.y < 0:
                if int((self.hitbox.y + self.direction.y * speed) / 64) == int(self.hitbox.y / 64):
                    self.hitbox.y += self.direction.y * speed
                else:
                    self.hitbox.y -= (self.hitbox.centery - 32) % 64
                    self.is_done_y = True
            elif not self.is_done_y:
                if int((self.hitbox.y + self.direction.y * speed) / 64) == int(self.hitbox.y / 64):
                    self.hitbox.y += self.direction.y * speed
                else:
                    self.hitbox.y = int((self.hitbox.y + self.direction.y * speed) / 64) * 64
                    self.is_done_y = True
            if self.is_done_x and self.is_done_y:
                self.is_on_tile = True
                self.x_value = self.hitbox.x
                self.y_value = self.hitbox.y
                self.is_done_x = False
                self.is_done_y = False
        else:
            if not self.is_done_x:
                self.desired_x = self.x_value
                if self.direction.x < 0:
                    self.desired_x -= 64
                elif self.direction.x > 0:
                    self.desired_x += 64
                if not (max(self.hitbox.x, self.hitbox.x + self.direction.x * speed) >= self.desired_x > min(
                        self.hitbox.x, self.hitbox.x + self.direction.x * speed)):
                    self.hitbox.x += self.direction.x * speed
                else:
                    self.hitbox.x = self.desired_x
                    self.is_done_x = True
            if not self.is_done_y:
                self.desired_y = self.y_value
                if self.direction.y < 0:
                    self.desired_y -= 64
                elif self.direction.y > 0:
                    self.desired_y += 64
                if not (max(self.hitbox.y, self.hitbox.y + self.direction.y * speed) >= self.desired_y > min(
                        self.hitbox.y, self.hitbox.y + self.direction.y * speed)):
                    self.hitbox.y += self.direction.y * speed
                else:
                    self.hitbox.y = self.desired_y
                    self.is_done_y = True

        self.collision('horizontal')  # Check collisions in the horizontal axis
        self.collision('vertical')  # Check collisions in the vertical axis

        self.rect.center = self.hitbox.center
        if self.hitbox.x == self.last_x and self.hitbox.y == self.last_y:
            self.auto_count += 1
        else:
            self.last_x = self.hitbox.x
            self.last_y = self.hitbox.y
            self.auto_count = 0

        if self.hitbox.x == self.desired_x and self.hitbox.y == self.desired_y:
            del (self.moves_auto_walk[-1])
            self.is_done_x = False
            self.is_done_y = False
            self.x_value = self.desired_x
            self.y_value = self.desired_y
        if self.is_on_tile and len(self.moves_auto_walk) == 0:
            self.start_auto_walk()
        if self.auto_count == 3:
            self.rand_walk = True
            self.start_auto_walk()

    def input(self) -> None:
        """
        Get keyboard input and process it
        :return: None
        """

        keys: Sequence[pygame.Key] = pygame.key.get_pressed()
        mouse: Sequence[bool] = pygame.mouse.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
            self.status = 'up'
            self.stop_auto_walk()
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'down'
            self.stop_auto_walk()
        else:  # If no keys are pressed, the direction should reset to 0
            self.direction.y = 0

        if keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'
            self.stop_auto_walk()
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
            self.stop_auto_walk()
        else:  # If no keys are pressed, the direction should reset to 0
            self.direction.x = 0

        if keys[pygame.K_p] and not self.is_auto_walk:
            self.start_auto_walk()

        # Check if using speed skill
        if self.can_speed and keys[pygame.K_1] and self.energy >= self.speed_cost:
            self.can_speed = False
            self.energy -= self.speed_cost
            self.can_energy = False
            self.energy_time = 0
            self.is_fast = True
            self.speed *= self.speed_skill_factor
            self.speed_start = 0
            self.item_actions.append(Server.Output.ItemActionUpdate(action_type='skill', item_id=1, item_name=''))

        # Check if using magnet skill
        if self.can_magnet and keys[pygame.K_2] and self.energy >= self.magnet_cost:
            self.can_magnet = False
            self.energy -= self.magnet_cost
            self.can_energy = False
            self.energy_time = 0
            self.add(self.magnetic_players)
            self.is_magnet = True
            self.magnet_start = 0
            self.item_actions.append(Server.Output.ItemActionUpdate(action_type='skill', item_id=2, item_name=''))

        # Check if using lightning skill
        if self.can_lightning and keys[pygame.K_3] and self.energy >= self.lightning_cost:
            self.can_lightning = False
            self.energy -= self.lightning_cost
            self.can_energy = False
            self.energy_time = 0
            self.lightning_start = 0
            self.create_lightning()
            self.item_actions.append(Server.Output.ItemActionUpdate(action_type='skill', item_id=3, item_name=''))

        # Move nametag right after moving
        self.nametag_update(self.nametag)

        if keys[pygame.K_e] and not self.zen_active:
            if self.can_change_inventory and not self.last_inventory:
                if not self.inventory_active:
                    self.create_inventory()
                else:
                    self.destroy_inventory()

                self.inventory_active = not self.inventory_active
                self.can_change_inventory = False
            self.last_inventory = True
        else:
            self.last_inventory = False

        if keys[pygame.K_t]:
            if self.can_change_chat and not self.last_chat:
                if not self.chat_active:
                    self.create_chat()
                else:
                    self.destroy_chat()

                self.chat_active = not self.chat_active
                self.can_change_chat = False
                self.chat_time = 0
            self.last_chat = True
        else:
            self.last_chat = False

        if keys[pygame.K_m]:
            if self.can_change_minimap and not self.last_minimap:
                if not self.minimap_active:
                    self.create_minimap()
                else:
                    self.destroy_minimap()

                self.minimap_active = not self.minimap_active
                self.can_change_minimap = False
                self.minimap_time = 0
            self.last_minimap = True
        else:
            self.last_minimap = False

        if keys[pygame.K_z]:
            if self.can_change_zen and not self.last_zen:
                if not self.zen_active:
                    self.activate_zen()
                else:
                    self.deactivate_zen()

                self.zen_active = not self.zen_active
                self.can_change_zen = False
                self.zen_time = 0
            self.last_zen = True
        else:
            self.last_zen = False

        if self.release_mouse[0] and not mouse[0]:
            self.release_mouse[0] = False
        if self.release_mouse[1] and not mouse[2]:
            self.release_mouse[1] = False

        if mouse[0] and not self.attacking and not self.release_mouse[0]:
            if not self.inventory_active or pygame.mouse.get_pos()[0] < SCREEN_WIDTH - INVENTORY_WIDTH:
                if self.weapon_index not in self.on_screen:
                    self.attacks.append(
                        Server.Output.AttackUpdate(weapon_id=self.weapon_index, attack_type=1, direction=(0, 0)))
                    self.create_attack(self)
                    self.attacking = True
                    self.release_mouse[0] = True
                    self.attack_time = 0
                else:
                    if self.weapon_index == 1:
                        if self.can_shoot:
                            self.create_bullet(self, self.current_weapon.rect.center)
                            self.can_shoot = False
                    elif self.weapon_index == 2:
                        self.attacking = True
                        self.release_mouse[0] = True
                        self.attack_time = 0

                        self.create_kettle(self, self.current_weapon.rect.center)
                        self.inventory_items['kettle'].count -= 1
                        if self.inventory_items['kettle'].count == 0:
                            del self.inventory_items['kettle']

                        if 'kettle' not in self.inventory_items:
                            self.switch_weapon()

        if self.inventory_active and pygame.mouse.get_pos()[0] > SCREEN_WIDTH - INVENTORY_WIDTH:
            mouse_pos = pygame.mouse.get_pos()
            box = self.get_inventory_box_pressed(mouse_pos)

            if box is not None and box < len(self.inventory_items):
                item = list(self.inventory_items.keys())[box]

                if mouse[0] and not self.release_mouse[0]:
                    self.release_mouse[0] = True
                    used = True

                    if item == "heal":
                        self.health += 20
                        if self.health > self.stats['health']:
                            self.health = self.stats['health']
                    elif item == "strength":
                        self.strength += 1
                    elif item == "kettle":
                        if self.can_switch_weapon and not self.attacking and self.weapon_index != 2:
                            self.switch_weapon(2)
                        used = False
                    elif item == "shield":
                        self.resistance += 1

                    if used:
                        item_id = self.inventory_items[item].remove_item()
                        self.item_actions.append(Server.Output.ItemActionUpdate(item_name=item, action_type='use', item_id=item_id))

                        if self.inventory_items[item].count == 0:
                            del self.inventory_items[item]

                elif mouse[2] and not self.release_mouse[1]:
                    self.release_mouse[1] = True

                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        for i in range(self.inventory_items[item].count):
                            item_id = self.inventory_items[item].remove_item()
                            self.create_dropped_item(item, (self.rect.centerx, self.rect.centery), item_id)
                            self.item_actions.append(Server.Output.ItemActionUpdate(item_name=item, action_type='drop', item_id=item_id))
                    else:
                        item_id = self.inventory_items[item].remove_item()
                        self.create_dropped_item(item, (self.rect.centerx, self.rect.centery), item_id)
                        self.item_actions.append(Server.Output.ItemActionUpdate(item_name=item, action_type='drop', item_id=item_id))

                    if self.inventory_items[item].count == 0:
                        if item == "kettle" and self.weapon_index == 2:
                            self.switch_weapon()
                        del self.inventory_items[item]

        if keys[pygame.K_q] and self.can_switch_weapon and not self.attacking:
            self.switch_weapon()

    def switch_weapon(self, known_index=None) -> None:
        """
        switch current held weapon
        :return:
        """
        self.release_mouse[0] = True

        if self.weapon_index in self.on_screen:
            self.destroy_attack(self)

        self.can_switch_weapon = False

        if known_index is None:
            if self.weapon_index < len(list(weapon_data.keys())) - 1:
                self.weapon_index += 1
            else:
                self.weapon_index = 0
        else:
            self.weapon_index = known_index
        self.weapon = list(weapon_data.keys())[self.weapon_index]

        self.attacking = False

        if self.weapon_index in self.on_screen:
            self.create_attack(self)

        self.attacks.append(Server.Output.AttackUpdate(weapon_id=self.weapon_index, attack_type=0, direction=(0, 0)))

        # if switched to kettle and have no kettle, reswitch
        if self.weapon_index == 2 and 'kettle' not in self.inventory_items:
            self.switch_weapon()

    def get_status(self) -> None:
        """
        update player status
        :return: None
        """

        # idle
        if self.direction.x == 0 and self.direction.y == 0 and not self.is_auto_walk:
            if 'idle' not in self.status:
                self.status += '_idle'

    def cooldowns(self) -> None:
        """
        Manage cooldowns
        :return: None
        """

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
                self.energy_point_time += 1

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
                    self.destroy_attack(self)
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

        if not self.can_change_inventory:
            if self.inventory_time >= self.inventory_cooldown:
                self.can_change_inventory = True
                self.inventory_time = 0
            else:
                self.inventory_time += 1

        if not self.can_change_chat:
            if self.chat_time >= self.chat_cooldown:
                self.can_change_chat = True
                self.chat_time = 0
            else:
                self.chat_time += 1

        if not self.can_change_zen:
            if self.zen_time >= self.zen_cooldown:
                self.can_change_zen = True
                self.zen_time = 0
            else:
                self.zen_time += 1

        if not self.can_change_minimap:
            if self.minimap_time >= self.minimap_cooldown:
                self.can_change_minimap = True
                self.minimap_time = 0
            else:
                self.minimap_time += 1

    def animate(self) -> None:
        """
        animate through images
        :return: None
        """
        animation: List[pygame.Surface] = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self) -> None:
        """
        Update the player based on input
        :return: None
        """

        # Clear the changes dict
        self.attacks: deque = deque()
        self.item_actions: deque = deque()
        previous_state: dict = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.status,
                                'item_actions': self.item_actions}

        # Get keyboard inputs
        if not self.inputs_disabled:
            self.input()

        # Process cooldowns
        self.cooldowns()

        # Animation
        self.get_status()
        self.animate()

        # Apply keyboard inputs
        if not self.is_auto_walk:
            self.move(self.speed*self.dt)
        else:
            self.move_auto(self.speed*self.dt)

        self.changes = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.status,
                        'item_actions': tuple(self.item_actions)}
        if self.changes == previous_state:
            self.changes = None

    def die(self):

        self.nametag.kill = True
        if self.current_weapon is not None:
            self.current_weapon.kill()
        self.kill()  # TODO - add death screen

    def update_items(self, item_sprites: pygame.sprite.Group) -> None:
        self.item_sprites = item_sprites

    def get_pos(self) -> (int, int):
        """
        Returns the player's position
        """
        return self.rect.x, self.rect.y
