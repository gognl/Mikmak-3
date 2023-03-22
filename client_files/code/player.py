import random
from collections import deque
from typing import Dict, Sequence, Tuple

from client_files.code.explosion import Explosion
from client_files.code.settings import *
from client_files.code.structures import NormalServer, InventorySlot
from client_files.code.support import *
from client_files.code.entity import Entity


class Player(Entity):
    def __init__(self, name, pos, groups, obstacle_sprites, height, create_attack, destroy_attack,
                 create_bullet, create_kettle, create_inventory, destroy_inventory, create_chat,
                 destroy_chat, activate_zen, deactivate_zen, create_minimap, destroy_minimap, create_nametag,
                 nametag_update, get_inventory_box_pressed, create_dropped_item, spawn_enemy_from_egg, entity_id,
                 magnetic_players, layout, create_lightning, create_magnet) -> None:
        super().__init__(groups, entity_id, True, name, create_nametag, nametag_update)

        self.name = name

        self.magnetic_players = magnetic_players

        self.image: pygame.Surface = pygame.image.load('../graphics/player/down_idle/down.png').convert_alpha()

        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)

        self.height: int = height
        self.hitbox = self.rect.inflate(-20, -26)

        self.obstacle_sprites: pygame.Group = obstacle_sprites

        self.fdy: bool = False
        self.attack_cooldown = 0.5
        self.fvbvbc: int = 0

        self.djj32 = layout

        self.edjdwwij = create_attack
        self.destroy_attack = destroy_attack
        self.create_bullet = create_bullet
        self.create_kettle = create_kettle
        self.oi3u = 0
        self.on_screen = [1, 2]
        self.weapon = list(one12.keys())[self.oi3u]
        self.ffhfhvnvn = True
        self.weapon_switch_time = 0
        self.switch_duration_cooldown = 1.5
        self.current_weapon = None

        self.ijhcv = False
        self.qwuywyu = []
        self.cknv = []
        self.paokasdo = False
        self.oifuio = False
        self.dh = False
        self.lefuigfgluh = 0
        self.pdof = ()
        self.fdhujh4 = None
        self.askdj1 = None
        self.uudfdi8 = None
        self.dfuj3 = None
        self.sdkfjh7 = None
        self.fy4 = None
        self.fheh78 = 0
        self.rand_walk = False

        # TODO - do liroin
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.speed_animations: Dict[str, List[pygame.Surface]] = {}
        self.import_player_assets()
        self.cnnnj = 'down'

        # sdf
        self.attacks: deque = deque()
        self.item_actions: deque = deque()  # also used as skills update
        self.changes = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.cnnnj, 'item_actions': tuple(self.item_actions)}  # Changes made in this tick

        # asdf
        self.ddkkpk = {'health': 100, 'energy': 60, 'attack': 0, 'speed': 400}
        self.health = self.ddkkpk['health']
        self.ghhohg = self.ddkkpk['energy']
        self.max_energy = self.ddkkpk['energy']
        self.jkhkjhkjhp = 0
        self.cmmlm = self.ddkkpk['speed']
        self.z7777 = self.ddkkpk['attack']
        self.zzzmz = 0

        # gg
        self.initialize_nametag()

        # dfasdf
        self.can_shoot = True
        self.shoot_time = 0
        self.shoot_cooldown = 1

        # 213
        self.dfh73 = [False, False]

        # 3
        self.can_magnet = True
        self.is_magnet = False
        self.magnet_start = 0
        self.magnet_time = 10
        self.magnet_skill_cooldown = 40
        self.magnet_cost = 20
        self.create_magnet = create_magnet
        self.can_speed = True
        self.is_fast = False
        self.speed_start = 0
        self.speed_time = 3
        self.speed_skill_cooldown = 20
        self.speed_skill_factor = 2
        self.speed_cost = 40

        # d
        self.can_lightning = True
        self.lightning_start = 0
        self.lightning_skill_cooldown = 30
        self.lightning_cost = 30
        self.create_lightning = create_lightning

        # a
        self.create_inventory = create_inventory
        self.destroy_inventory = destroy_inventory
        self.inventory_active: bool = False
        self.can_change_inventory: bool = True
        self.inventory_time: int = 0
        self.inventory_cooldown: int = 6
        self.last_inventory: bool = True

        # sdasd
        self.create_chat = create_chat
        self.destroy_chat = destroy_chat
        self.last_chat = True
        self.chat_time = 0
        self.chat_cooldown = 6
        self.chat_active = False
        self.can_change_chat = True

        # Zefdedfn
        self.activate_zen = activate_zen
        self.dchnjns = deactivate_zen
        self.last_zen = True
        self.fjj = 0
        self.zen_cooldown = 6
        self.dvbchb = False
        self.sisj = True

        # dsfasdfZSFD
        self.create_minimap = create_minimap
        self.destroy_minimap = destroy_minimap
        self.woeiurwert = True
        self.minimap_time = 0
        self.minimap_cooldown = 6
        self.minimap_active = False
        self.can_change_minimap = True

        self.item_sprites = None
        self.inventory_items: Dict[str, InventorySlot] = {}
        self.get_inventory_box_pressed = get_inventory_box_pressed
        self.create_dropped_item = create_dropped_item
        self.spawn_enemy_from_egg = spawn_enemy_from_egg

        self.can_energy = True
        self.energy_cooldown = 6
        self.energy_time = 0
        self.energy_point_cooldown = 5
        self.energy_point_time = 0

        self.oooa = 1

        self.inputs_disabled: bool = False

    def import_player_assets(self) -> None:
        path: str = '../graphics/player/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [],
                           'left_idle': [], 'right_idle': []}
        for animation in self.animations.keys():
            self.animations[animation] = list(import_folder(path + animation).values())

        speed_path: str = '../graphics/player_speed/'
        self.speed_animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [],
                           'left_idle': [], 'right_idle': []}
        for speed_animation in self.speed_animations.keys():
            self.speed_animations[speed_animation] = list(import_folder(speed_path + speed_animation).values())


    def stop_auto_walk(self) -> None:
        if self.ijhcv:
            self.lefuigfgluh = 0
            self.ijhcv = False
            self.dh = False
            self.oifuio = False
            self.qwuywyu = []
            self.cknv = []
            self.paokasdo = False
            self.pdof = []
            self.uudfdi8 = None
            self.dfuj3 = None
            self.fdhujh4 = None
            self.askdj1 = None
            self.sdkfjh7 = None
            self.fy4 = None
            self.fheh78 = 0

    def is_good_auto_walk(self, sum: int, counter: int, y_place: int, x_place: int) -> bool:
        return not (len(self.djj32['floor']) > sum >= 0 and len(self.djj32['floor'][sum]) > counter >= 0 and not
                    (int(self.djj32['floor'][sum][counter]) in onetwo and int(self.djj32['objects'][sum][counter]) == -1))

    def start_auto_walk(self) -> None:
        self.stop_auto_walk()
        self.ijhcv = True
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        if self.rand_walk:
            self.rand_walk = False
            i = random.randint(0, 3)
            self.pdof = directions[i]
            for j in range(0, 5):
                self.qwuywyu.append(directions[i])
            return
        x = self.rect.x
        y = self.rect.y
        self.sdkfjh7 = x
        self.fy4 = y
        x = int(x / 64)
        y = int(y / 64)
        x1 = 0
        y1 = 0
        while not (int(self.djj32['floor'][y1][x1]) in onetwo and int(self.djj32['objects'][y1][x1]) == -1
                   and abs(x - x1) >= 200):
            x1 = random.randint(0, 1280 * 40 // 64 - 1)
            y1 = random.randint(0, 720 * 40 // 64 - 1)
        x_values = (max(0, min(x1, x) - three4), min(whatis - 1, max(x1, x) + three4))
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
        for i in range(max(0, min(x1, x) - three4), min(whatis - 1, max(x1, x) + three4) + 1):
            if i < min(x1, x):
                if x1 <= x:
                    y_values.append((max(y1 - three4, 0), min(y1 + three4, andthat - 1)))
                    is_in_bfs.append([])
                    for j in range(max(y1 - three4, 0), min(y1 + three4, andthat - 1) + 1):
                        is_in_bfs[-1].append(self.is_good_auto_walk(j, i, y, x))
                else:
                    y_values.append((max(y - three4, 0), min(y + three4, andthat - 1)))
                    is_in_bfs.append([])
                    for j in range(max(y - three4, 0), min(y + three4, andthat - 1) + 1):
                        is_in_bfs[-1].append(self.is_good_auto_walk(j, i, y, x))
                continue
            elif i > max(x1, x):
                if x1 >= x:
                    y_values.append((max(y1 - three4, 0), min(y1 + three4, andthat - 1)))
                    is_in_bfs.append([])
                    for j in range(max(y1 - three4, 0), min(y1 + three4, andthat - 1) + 1):
                        is_in_bfs[-1].append(self.is_good_auto_walk(j, i, y, x))
                else:
                    y_values.append((max(y - three4, 0), min(y + three4, andthat - 1)))
                    is_in_bfs.append([])
                    for j in range(max(y - three4, 0), min(y + three4, andthat - 1) + 1):
                        is_in_bfs[-1].append(self.is_good_auto_walk(j, i, y, x))
                continue
            else:
                high -= y3 / x3 * plus
                y_values.append((max(int(high) - three4, 0), min(
                    int(high) + three4, andthat - 1)))
                is_in_bfs.append([])
                for j in range(max(int(high) - three4, 0), min(
                        int(high) + three4, andthat - 1) + 1):
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
        min_dst = 10000000
        for i in new_directions:
            min_dst = min(min_dst, bfs_values[x + i[0] - x_values[0]][y + i[1] - y_values[x + i[0] - x_values[0]][0]])
        for i in new_directions:
            if min_dst == bfs_values[x + i[0] - x_values[0]][y + i[1] - y_values[x + i[0] - x_values[0]][0]]:
                self.pdof = i
                break
        x += self.pdof[0]
        y += self.pdof[1]
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
                self.qwuywyu.append(temp_answer[i])
                continue
            x_not = temp_answer[i + 1][0] + pos[0]
            y_not = temp_answer[i + 1][1] + pos[1]
            pos[0] += temp_answer[i][0]
            pos[1] += temp_answer[i][1]
            if int(self.djj32['floor'][y_not][x_not]) in onetwo and int(
                    self.djj32['objects'][y_not][x_not]) == -1:
                self.qwuywyu.append((temp_answer[i][0] + temp_answer[i + 1][0], temp_answer[i][1] +
                                     temp_answer[i + 1][1]))
                before = True
            else:
                self.qwuywyu.append(temp_answer[i])
        answer = []
        temp = (64 * x, 64 * y)
        for i in range(0, len(self.qwuywyu)):
            x += self.qwuywyu[len(self.qwuywyu) - 1 - i][0]
            y += self.qwuywyu[len(self.qwuywyu) - 1 - i][1]
            answer.append((x, y))
        for i in range(0, len(answer)):
            self.cknv.append((answer[len(answer) - 1 - i][0] * 64, answer[len(answer) - 1 - i][1] * 64))
        self.cknv.append(temp)

    def move_auto(self, speed: int):

        if self.lefuigfgluh < 4:
            self.lefuigfgluh += 1
            return

        # Update name tag right after moving
        if self.nametag is not None:
            self.nametag_update(self.nametag)

        # Get the direction
        if not self.paokasdo:
            self.direction.x = self.pdof[0]
            self.direction.y = self.pdof[1]
        else:
            self.direction.x = self.qwuywyu[len(self.qwuywyu) - 1][0]
            self.direction.y = self.qwuywyu[len(self.qwuywyu) - 1][1]

        # Normalize direction
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Change animation
        if abs(self.direction.x) > abs(self.direction.y):
            if self.direction.x > 0:
                self.cnnnj = 'right'
            else:
                self.cnnnj = 'left'
        else:
            if self.direction.y > 0:
                self.cnnnj = 'down'
            else:
                self.cnnnj = 'up'

        # Move accordingly to the direction
        if not self.paokasdo:
            if not self.oifuio:
                if int((self.hitbox.x + self.direction.x * speed) / 64) == int(self.hitbox.x / 64):
                    self.hitbox.x += self.direction.x * speed
                else:
                    self.hitbox.x = self.cknv[-1][0]
                    self.oifuio = True
                self.collision('horizontal')  # Check collisions in the horizontal axis

            if not self.dh:
                if int((self.hitbox.y + self.direction.y * speed) / 64) == int(self.hitbox.y / 64):
                    self.hitbox.y += self.direction.y * speed
                else:
                    self.hitbox.y = self.cknv[-1][1]
                    self.dh = True
                self.collision('vertical')  # Check collisions in the vertical axis

            if self.oifuio and self.dh:
                self.paokasdo = True
                self.oifuio = False
                self.dh = False
                del (self.cknv[-1])
        else:
            if self.direction.x == 0:
                self.oifuio = True
            if self.direction.y == 0:
                self.dh = True
            if not self.oifuio:
                if not (max(self.hitbox.x, self.hitbox.x + self.direction.x * speed) >= self.cknv[-1][0] > min(
                        self.hitbox.x, self.hitbox.x + self.direction.x * speed)):
                    self.hitbox.x += self.direction.x * speed
                else:
                    self.hitbox.x = self.cknv[-1][0]
                    self.oifuio = True
                self.collision('horizontal')  # Check collisions in the horizontal axis

            if not self.dh:
                if not (max(self.hitbox.y, self.hitbox.y + self.direction.y * speed) >= self.cknv[-1][1] > min(
                        self.hitbox.y, self.hitbox.y + self.direction.y * speed)):
                    self.hitbox.y += self.direction.y * speed
                else:
                    self.hitbox.y = self.cknv[-1][1]
                    self.dh = True
                self.collision('vertical')  # Check collisions in the vertical axis

        self.rect.center = self.hitbox.center
        if self.hitbox.x == self.cknv[-1][0] and self.hitbox.y == self.cknv[-1][1] and self.paokasdo:
            del (self.qwuywyu[-1])
            del (self.cknv[-1])
            self.oifuio = False
            self.dh = False
        if self.paokasdo and len(self.qwuywyu) == 0:
            self.start_auto_walk()
        if self.fheh78 == 3:
            self.rand_walk = True
            self.start_auto_walk()

    def input(self) -> None:

        dasdasd: Sequence[pygame.Key] = pygame.key.get_pressed()
        asddj: Sequence[bool] = pygame.mouse.get_pressed()

        if dasdasd[pygame.K_w]:
            self.direction.y = -1
            self.cnnnj = 'up'
            self.stop_auto_walk()
        elif dasdasd[pygame.K_s]:
            self.direction.y = 1
            self.cnnnj = 'down'
            self.stop_auto_walk()
        else:  # If no keys are pressed, the direction should reset to 0
            self.direction.y = 0

        if dasdasd[pygame.K_a]:
            self.direction.x = -1
            self.cnnnj = 'left'
            self.stop_auto_walk()
        elif dasdasd[pygame.K_d]:
            self.direction.x = 1
            self.cnnnj = 'right'
            self.stop_auto_walk()
        else:  # If no keys are pressed, the direction should reset to 0
            self.direction.x = 0

        if dasdasd[pygame.K_p] and not self.ijhcv:
            self.start_auto_walk()

        # Check if using speed skill
        if self.can_speed and dasdasd[pygame.K_1] and self.ghhohg >= self.speed_cost:
            self.can_speed = False
            self.ghhohg -= self.speed_cost
            self.can_energy = False
            self.energy_time = 0
            self.is_fast = True
            self.cmmlm *= self.speed_skill_factor
            self.speed_start = 0
            self.item_actions.append(NormalServer.Output.ItemActionUpdate(action_type='skill', item_id=1, item_name=''))

        # Check if using magnet skill
        if self.can_magnet and dasdasd[pygame.K_2] and self.ghhohg >= self.magnet_cost:
            self.can_magnet = False
            self.ghhohg -= self.magnet_cost
            self.can_energy = False
            self.energy_time = 0
            self.add(self.magnetic_players)
            self.is_magnet = True
            self.magnet_start = 0
            self.create_magnet()
            self.item_actions.append(NormalServer.Output.ItemActionUpdate(action_type='skill', item_id=2, item_name=''))

        # Check if using lightning skill
        if self.can_lightning and dasdasd[pygame.K_3] and self.ghhohg >= self.lightning_cost:
            self.can_lightning = False
            self.ghhohg -= self.lightning_cost
            self.can_energy = False
            self.energy_time = 0
            self.lightning_start = 0
            self.create_lightning()
            self.item_actions.append(NormalServer.Output.ItemActionUpdate(action_type='skill', item_id=3, item_name=''))

        # Move nametag right after moving
        self.nametag_update(self.nametag)

        if dasdasd[pygame.K_e] and not self.dvbchb:
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

        if dasdasd[pygame.K_t]:
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

        if dasdasd[pygame.K_m]:
            if self.can_change_minimap and not self.woeiurwert:
                if not self.minimap_active:
                    self.create_minimap()
                else:
                    self.destroy_minimap()

                self.minimap_active = not self.minimap_active
                self.can_change_minimap = False
                self.minimap_time = 0
            self.woeiurwert = True
        else:
            self.woeiurwert = False

        if dasdasd[pygame.K_z]:
            if self.sisj and not self.last_zen:
                if not self.dvbchb:
                    self.activate_zen()
                else:
                    self.dchnjns()

                self.dvbchb = not self.dvbchb
                self.sisj = False
                self.fjj = 0
            self.last_zen = True
        else:
            self.last_zen = False

        if self.dfh73[0] and not asddj[0]:
            self.dfh73[0] = False
        if self.dfh73[1] and not asddj[2]:
            self.dfh73[1] = False

        if asddj[0] and not self.fdy and not self.dfh73[0]:
            if not self.inventory_active or pygame.mouse.get_pos()[0] < kljh - tontwo:
                if self.oi3u not in self.on_screen:
                    self.attacks.append(
                        NormalServer.Output.AttackUpdate(weapon_id=self.oi3u, attack_type=1, direction=(0, 0)))
                    self.edjdwwij(self)
                    self.fdy = True
                    self.dfh73[0] = True
                    self.fvbvbc = 0
                else:
                    if self.oi3u == 1:
                        if self.can_shoot:
                            self.create_bullet(self, self.current_weapon.vbvbv.center)
                            self.can_shoot = False
                    elif self.oi3u == 2:
                        self.fdy = True
                        self.dfh73[0] = True
                        self.fvbvbc = 0

                        self.create_kettle(self, self.current_weapon.vbvbv.center)
                        self.inventory_items['kettle'].count -= 1
                        if self.inventory_items['kettle'].count == 0:
                            del self.inventory_items['kettle']

                        if 'kettle' not in self.inventory_items:
                            self.fjklj2()

        if self.inventory_active and pygame.mouse.get_pos()[0] > kljh - tontwo:
            poiuiu = pygame.mouse.get_pos()
            dfkhdsf3 = self.get_inventory_box_pressed(poiuiu)

            if dfkhdsf3 is not None and dfkhdsf3 < len(self.inventory_items):
                hfdjfhkjdshf = list(self.inventory_items.keys())[dfkhdsf3]

                if asddj[0] and not self.dfh73[0]:
                    self.dfh73[0] = True
                    fjfdnv = True

                    if hfdjfhkjdshf == "heal":
                        self.health += 20
                        if self.health > self.ddkkpk['health']:
                            self.health = self.ddkkpk['health']
                    elif hfdjfhkjdshf == "strength":
                        self.z7777 += 1
                    elif hfdjfhkjdshf == "kettle":
                        if self.ffhfhvnvn and not self.fdy and self.oi3u != 2:
                            self.fjklj2(2)
                        fjfdnv = False
                    elif hfdjfhkjdshf == "shield":
                        self.zzzmz += 1

                    if fjfdnv:
                        item_id = self.inventory_items[hfdjfhkjdshf].remove_item()
                        self.item_actions.append(NormalServer.Output.ItemActionUpdate(item_name=hfdjfhkjdshf, action_type='use', item_id=item_id))

                        if self.inventory_items[hfdjfhkjdshf].count == 0:
                            del self.inventory_items[hfdjfhkjdshf]

                elif asddj[2] and not self.dfh73[1]:
                    self.dfh73[1] = True

                    if dasdasd[pygame.K_LSHIFT] or dasdasd[pygame.K_RSHIFT]:
                        for i in range(self.inventory_items[hfdjfhkjdshf].count):
                            item_id = self.inventory_items[hfdjfhkjdshf].remove_item()
                            self.create_dropped_item(hfdjfhkjdshf, (self.rect.centerx, self.rect.centery), item_id)
                            self.item_actions.append(NormalServer.Output.ItemActionUpdate(item_name=hfdjfhkjdshf, action_type='drop', item_id=item_id))
                    else:
                        item_id = self.inventory_items[hfdjfhkjdshf].remove_item()
                        self.create_dropped_item(hfdjfhkjdshf, (self.rect.centerx, self.rect.centery), item_id)
                        self.item_actions.append(NormalServer.Output.ItemActionUpdate(item_name=hfdjfhkjdshf, action_type='drop', item_id=item_id))

                    if self.inventory_items[hfdjfhkjdshf].count == 0:
                        if hfdjfhkjdshf == "kettle" and self.oi3u == 2:
                            self.fjklj2()
                        del self.inventory_items[hfdjfhkjdshf]

        if dasdasd[pygame.K_q] and self.ffhfhvnvn and not self.fdy:
            self.fjklj2()

    def fjklj2(self, known_index=None) -> None:
        """Get the last comment in chat
        """
        self.dfh73[0] = True

        if self.oi3u in self.on_screen:
            self.destroy_attack(self)

        self.ffhfhvnvn = False

        if known_index is None:
            if self.oi3u < len(list(one12.keys())) - 1:
                self.oi3u += 1
            else:
                self.oi3u = 0
        else:
            self.oi3u = known_index
        self.weapon = list(one12.keys())[self.oi3u]

        self.fdy = False

        if self.oi3u in self.on_screen:
            self.edjdwwij(self)

        self.attacks.append(NormalServer.Output.AttackUpdate(weapon_id=self.oi3u, attack_type=0, direction=(0, 0)))

        # if switched to kettle and have no kettle, reswitch
        if self.oi3u == 2 and 'kettle' not in self.inventory_items:
            self.fjklj2()

    def get_status(self) -> None:
        """
       auto walk to nearest hoe
        """

        # idle
        if self.direction.x == 0 and self.direction.y == 0 and not self.ijhcv:
            if 'idle' not in self.cnnnj:
                self.cnnnj += '_idle'

    def cooldowns(self) -> None:
        """sad
        """

        # Energy
        if not self.can_energy:
            if self.energy_time >= self.energy_cooldown:
                self.can_energy = True
                self.energy_time = 0
            else:
                self.energy_time += self.oooa
        elif self.ghhohg < self.max_energy:
            if self.energy_point_time >= self.energy_point_cooldown:
                self.ghhohg += 1
                self.energy_point_time = 0
            else:
                self.energy_point_time += 1

        # Speed skill timers
        if not self.can_speed:
            if self.speed_start >= self.speed_time and self.is_fast:
                self.cmmlm = int(self.cmmlm / self.speed_skill_factor)
                self.is_fast = False
            elif self.speed_start >= self.speed_skill_cooldown:
                self.can_speed = True
                self.speed_start = 0
            else:
                self.speed_start += self.oooa

        # Magnet skill timers
        if not self.can_magnet:
            if self.magnet_start >= self.magnet_time and self.is_magnet:
                self.is_magnet = False
                self.remove(self.magnetic_players)
            elif self.magnet_start >= self.magnet_skill_cooldown:
                self.can_magnet = True
                self.magnet_start = 0
            else:
                self.magnet_start += self.oooa

        # Lightning skill timers
        if not self.can_lightning:
            if self.lightning_start >= self.lightning_skill_cooldown:
                self.can_lightning = True
                self.lightning_start = 0
            else:
                self.lightning_start += self.oooa

        if self.fdy:
            if self.fvbvbc >= self.attack_cooldown:
                self.fdy = False
                self.fvbvbc = 0
                if self.oi3u not in self.on_screen:
                    self.destroy_attack(self)
            else:
                self.fvbvbc += self.oooa

        if not self.ffhfhvnvn:
            if self.weapon_switch_time >= self.switch_duration_cooldown:
                self.ffhfhvnvn = True
                self.weapon_switch_time = 0
            else:
                self.weapon_switch_time += self.oooa

        if not self.can_shoot:
            if self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True
                self.shoot_time = 0
            else:
                self.shoot_time += self.oooa

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

        if not self.sisj:
            if self.fjj >= self.zen_cooldown:
                self.sisj = True
                self.fjj = 0
            else:
                self.fjj += 1

        if not self.can_change_minimap:
            if self.minimap_time >= self.minimap_cooldown:
                self.can_change_minimap = True
                self.minimap_time = 0
            else:
                self.minimap_time += 1

    def animate(self) -> None:
        """
        Add hp to player base in the base of the plaster
        """
        if self.is_fast:
            animation: List[pygame.Surface] = self.speed_animations[self.cnnnj]
        else:
            animation: List[pygame.Surface] = self.animations[self.cnnnj]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self) -> None:
        """
        Nobody nobdy"""

        # Clear the changes dict
        self.attacks: deque = deque()
        self.item_actions: deque = deque()
        previous_state: dict = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.cnnnj,
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
        if not self.ijhcv:
            self.move(self.cmmlm * self.oooa)
        else:
            self.move_auto(self.cmmlm * self.oooa)

        self.changes = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.cnnnj,
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
