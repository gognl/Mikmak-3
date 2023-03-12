from __future__ import annotations

import random
import threading
import time
from collections import deque
from queue import Queue, Empty
import socket
from typing import Union, Dict
from struct import unpack, pack

from pygame import Vector2

from server_files_normal.game.explosion import Explosion
from server_files_normal.game.item import Item
from server_files_normal.game.projectile import Projectile
from server_files_normal.game.support import import_csv_layout
from server_files_normal.ClientManager import ClientManager
from server_files_normal.game.barrier import Barrier
from server_files_normal.game.enemy import Enemy
from server_files_normal.game.player import Player
from server_files_normal.game.weapon import Weapon
from server_files_normal.structures import *
from server_files_normal.game.settings import *
from server_files_normal.structures import PlayerCentral, PlayerCentralList
import pygame
from encryption import encrypt, decrypt


class GameManager(threading.Thread):
    def __init__(self, client_managers: deque, cmd_semaphore: threading.Semaphore, my_server_index: int):
        super().__init__()
        self.client_managers: deque[ClientManager] = client_managers
        self.cmd_queue: Queue[Tuple[ClientManager, Client.Input.ClientCMD]] = Queue()
        threading.Thread(target=self.add_messages_to_queue, args=(cmd_semaphore,)).start()

        def generate_enemy_id():
            for i in range(AMOUNT_ENEMIES_PER_SERVER):
                yield my_server_index * AMOUNT_ENEMIES_PER_SERVER + i

        self.generate_entity_id = generate_enemy_id()

        pygame.init()
        self.clock = pygame.time.Clock()

        self.players: pygame.sprite.Group = pygame.sprite.Group()
        self.enemies: pygame.sprite.Group = pygame.sprite.Group()
        self.alive_entities: pygame.sprite.Group = pygame.sprite.Group()
        self.projectiles: pygame.sprite.Group = pygame.sprite.Group()
        self.weapons: pygame.sprite.Group = pygame.sprite.Group()
        self.items: pygame.sprite.Group = pygame.sprite.Group()
        self.magnetic_players: pygame.sprite.Group = pygame.sprite.Group()

        self.players_updates: List[Client.Output.PlayerUpdate] = []
        self.enemy_changes: List[Client.Output.EnemyUpdate] = []
        self.item_changes: List[Client.Output.ItemUpdate] = []

        self.obstacle_sprites: pygame.sprite.Group = pygame.sprite.Group()  # players & walls
        self.all_obstacles: pygame.sprite.Group = pygame.sprite.Group()  # players, cows, and walls
        # self.initialize_obstacle_sprites()

        self.sock_to_login: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_to_LB: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_to_other_normals: list[socket.socket] = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in
                                                           range(4)]

        self.my_server_index = my_server_index
        self.other_server_indices = [i for i in range(4) if i != my_server_index]

        for i in self.other_server_indices:
            self.sock_to_other_normals[i].bind(('0.0.0.0', NORMAL_SERVERS[my_server_index].port + i))
            self.sock_to_other_normals[i].settimeout(0.02)

        self.sock_to_login.connect(LOGIN_SERVER.addr())
        self.sock_to_login.send(NORMAL_SERVERS_FOR_CLIENT[self.my_server_index].port.to_bytes(2, 'little'))
        self.sock_to_LB.connect(LB_SERVER.addr())
        self.sock_to_LB.send(NORMAL_SERVERS_FOR_CLIENT[self.my_server_index].port.to_bytes(2, 'little'))

        self.DH_keys: list[bytes] = [bytes(0) for _ in range(4)]
        self.DH_login_key: bytes = bytes(0)
        a = random.randrange(DH_p)

        def DH_with_normal(server_index: int, keys_list: list[bytes]):
            x = pow(DH_g, a, DH_p)
            other_server_addr = (NORMAL_SERVERS[server_index] + my_server_index).addr()
            self.sock_to_other_normals[server_index].sendto(x.to_bytes(128, 'little'), other_server_addr)
            print('x:', x.to_bytes(128, 'little'))
            y, addr = 0, ('0.0.0.0', 0)
            while not Server(addr[0], addr[1] - my_server_index) == NORMAL_SERVERS[server_index]:
                try:
                    y, addr = self.sock_to_other_normals[server_index].recvfrom(1024)
                    print('y:', y)
                except socket.timeout:
                    continue

            keys_list[server_index] = pow(int.from_bytes(y, 'little'), a, DH_p).to_bytes(128, 'little')

        def DH_with_login():
            x = pow(DH_g, a, DH_p)
            self.sock_to_login.send(x.to_bytes(128, 'little'))
            y = self.sock_to_login.recv(1024)
            self.DH_login_key = pow(int.from_bytes(y, 'little'), a, DH_p).to_bytes(128, 'little')

        DH_threads: list[threading.Thread] = []
        for i in self.other_server_indices:
            if i > 1:
                continue
            DH_threads.append(threading.Thread(target=DH_with_normal, args=(i, self.DH_keys)))

        DH_threads.append(threading.Thread(target=DH_with_login))

        input("Press Enter to start the server")
        for thread in DH_threads:
            thread.start()
        for thread in DH_threads:
            thread.join()

        self.read_only_players = pygame.sprite.Group()
        self.output_overlapped_players_updates: list[dict[int, Client.Output.PlayerUpdate]] = [{}, {}, {}, {}]  # in index i are the (id, update) pairs to server i
        self.output_overlapped_items_updates: list[dict[int, Client.Output.ItemUpdate]] = [{}, {}, {}, {}]
        self.output_overlapped_enemies_updates: list[dict[int, Client.Output.EnemyUpdate]] = [{}, {}, {}, {}]
        self.change_ids: list[int] = []
        self.center: Point = Point(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        threading.Thread(target=self.receive_from_another_normal_servers).start()
        threading.Thread(target=self.recv_from_login).start()

        # TODO temporary
        for i in range(AMOUNT_ENEMIES_PER_SERVER):
            pos_x = random.randrange(my_server_index % 2 * self.center.x, (my_server_index % 2 + 1) * self.center.x)
            pos_y = random.randrange(my_server_index % 2 * self.center.y, (my_server_index % 2 + 1) * self.center.y)
            pos = (pos_x, pos_y)
            Enemy(enemy_name='white_cow', pos=pos, groups=(self.enemies, self.all_obstacles, self.alive_entities),
                  entity_id=next(self.generate_entity_id), obstacle_sprites=self.all_obstacles, item_sprites=self.items,
                  create_explosion=self.create_explosion, create_bullet=self.create_bullet,
                  get_free_item_id=self.get_free_item_id)

        # TODO temporary, item spawning
        self.layout: Dict[str, List[List[str]]] = {
            'floor': import_csv_layout('./graphics/map/map_Ground.csv'),
            'objects': import_csv_layout('./graphics/map/map_Objects.csv'),
            'boundary': import_csv_layout('./graphics/map/map_Barriers.csv'),
        }

        for item_id in range(40):
            while True:
                random_x = random.randint(20, 30)
                random_y = random.randint(20, 30)
                name = item_names[int(random.randint(0, len(item_names) - 1))]

                if int(self.layout['floor'][random_y][random_x]) in SPAWNABLE_TILES and int(
                        self.layout['objects'][random_y][random_x]) == -1:
                    item = Item(name, (self.items,), (random_x * 64 + 32, random_y * 64 + 32), item_id)
                    item.actions.append(Client.Output.ItemActionUpdate(player_id=0, action_type='spawn',
                                                                       pos=(random_x * 64 + 32, random_y * 64 + 32)))
                    break

        self.next_item_id = 40
        self.id_info_dict: dict[int: InfoData] = {}

    def recv_from_login(self):
        while True:
            size = unpack('<H', self.sock_to_login.recv(2))[0]
            data = decrypt(self.sock_to_login.recv(size), self.DH_login_key)
            info_from_login = InfoMsgToNormal(ser=data)
            self.id_info_dict[info_from_login.client_id] = info_from_login.info

    def recv_from_LB(self):
        while True:
            data = self.sock_to_LB.recv(1024)

            center: PointSer = PointSer(ser=data)
            self.center.x = center.x
            self.center.y = center.y

            item_details_to_servers: list[list[NormalServer.ItemDetails]] = [[], [], [], []]
            for item in self.items:
                pos: Tuple[int] = item.get_pos()
                item_details = NormalServer.ItemDetails(id=item.item_id, name=item.str_name, pos=pos)
                pos: Point = Point(pos[0], pos[1])
                if self.my_server_index != 0 and pos in Rect(0, 0, self.center.x + OVERLAPPING_AREA_T,
                                                             self.center.y + OVERLAPPING_AREA_T):
                    item_details_to_servers[0].append(item_details)

                if self.my_server_index != 1 and pos in Rect(self.center.x - OVERLAPPING_AREA_T, 0, MAP_WIDTH,
                                                             self.center.y + OVERLAPPING_AREA_T):
                    item_details_to_servers[1].append(item_details)

                if self.my_server_index != 2 and pos in Rect(0, self.center.x - OVERLAPPING_AREA_T,
                                                             self.center.x + OVERLAPPING_AREA_T, MAP_HEIGHT):
                    item_details_to_servers[2].append(item_details)

                if self.my_server_index != 3 and pos in Rect(self.center.x - OVERLAPPING_AREA_T,
                                                             self.center.y - OVERLAPPING_AREA_T, MAP_WIDTH, MAP_HEIGHT):
                    item_details_to_servers[3].append(item_details)

            for i in self.other_server_indices:
                if len(item_details_to_servers) != 0:
                    self.send_to_normal_server(i, b'\x02' + NormalServer.ItemDetailsList(
                        item_details_list=item_details_to_servers[i]).serialize())

    def get_free_item_id(self):
        self.next_item_id += 1
        return self.next_item_id

    def get_obstacle_sprites(self):
        return self.obstacle_sprites

    def initialize_obstacle_sprites(self):
        layout = import_csv_layout('./graphics/map/map_Barriers.csv')
        for row_index in range(0, ROW_TILES):
            row = layout[row_index]
            for col_index in range(0, COL_TILES):
                col = row[col_index]
                if col != '-1':  # -1 in csv means no tile, don't need to recreate the tile if it already exists
                    x: int = col_index * TILESIZE
                    y: int = row_index * TILESIZE
                    Barrier((x, y), (self.obstacle_sprites, self.all_obstacles))

    def add_messages_to_queue(self, cmd_semaphore: threading.Semaphore):
        while True:
            cmd_semaphore.acquire()  # so its not just busy waiting
            for client_manager in list(self.client_managers):
                if client_manager.has_messages():
                    self.cmd_queue.put(client_manager.get_new_message())

    def broadcast_msg(self, msg: Client.Output.StateUpdateNoAck):
        for client_manager in list(self.client_managers):
            client_manager.send_msg(msg)

    def add_player(self, entity_id: int):
        print(self.id_info_dict[entity_id].info)
        pos: (int, int) = (self.id_info_dict[entity_id].info[0], self.id_info_dict[entity_id].info[1])
        print(pos)
        return Player((self.players, self.obstacle_sprites, self.all_obstacles, self.alive_entities), entity_id, pos,
                      self.id_info_dict[entity_id].info[2], self.id_info_dict[entity_id].info[4],
                      self.id_info_dict[entity_id].info[3],
                      self.id_info_dict[entity_id].info[5], self.id_info_dict[entity_id].info[6],
                      self.create_bullet, self.create_kettle, self.weapons, self.create_attack, self.items,
                      self.get_free_item_id, self.spawn_enemy_from_egg, self.magnetic_players, self.activate_lightning)

    @staticmethod
    def get_player_data(player: Player):
        return {'entity_id': player.entity_id,
                'pos': tuple(player.rect.topleft),
                'health': player.health,
                'strength': player.strength,
                'resistance': player.resistance,
                'xp': player.xp,
                'inventory': player.inventory_items}

    def send_initial_info(self, client_manager: ClientManager):
        player_data: list = []
        enemies_data: list = []
        items_data: List = []

        for player in self.players.sprites():
            initial_weapon_data: Client.Output.AttackUpdate = Client.Output.AttackUpdate(weapon_id=player.weapon_index,
                                                                                         attack_type=0,
                                                                                         direction=(0, 0))
            changes = {'pos': (player.rect.x, player.rect.y), 'attacks': (initial_weapon_data,),
                       'status': player.status, 'health': player.health, 'strength': player.strength}
            player_data.append(Client.Output.PlayerUpdate(id=player.entity_id, changes=changes))

        for enemy in self.enemies.sprites():
            changes = {'pos': (enemy.rect.x, enemy.rect.y), 'direction': (enemy.direction.x, enemy.direction.y),
                       'status': enemy.status, 'attacks': tuple(enemy.attacks)}
            enemies_data.append(Client.Output.EnemyUpdate(id=enemy.entity_id, type=enemy.enemy_name, changes=changes))

        for item in self.items.sprites():
            item_actions = (Client.Output.ItemActionUpdate(pos=tuple(item.rect.center)),)
            items_data.append(Client.Output.ItemUpdate(id=item.item_id, name=item.str_name, actions=item_actions))

        state_update: Client.Output.StateUpdateNoAck = Client.Output.StateUpdateNoAck(tuple(player_data),
                                                                                      tuple(enemies_data),
                                                                                      tuple(items_data))
        client_manager.send_msg(state_update)

    def handle_read_only_player_update(self, player_update: Client.Output.PlayerUpdate):
        for p in self.read_only_players:
            if player_update.id == p.entity_id:
                player = p
                break
        else:
            player = Player((self.read_only_players,), player_update.id, player_update.pos, player_update.health, None,
                            None, None, None, self.create_bullet, self.create_kettle, self.weapons, self.create_attack,
                            self.items,
                            self.get_free_item_id, self.spawn_enemy_from_egg, self.magnetic_players,
                            self.activate_lightning)

        # Update the player
        player.update_pos(player_update.pos)
        player.status = player_update.status
        player.health = player_update.health

    def receive_from_another_normal_servers(self):
        while True:
            for i in self.other_server_indices:
                sock = self.sock_to_other_normals[i]
                try:
                    data, addr = sock.recvfrom(4096)
                except socket.timeout:
                    continue
                except ConnectionResetError:
                    print(i)
                    continue
                if Server(addr[0], addr[1] - self.my_server_index) == NORMAL_SERVERS[i]:
                    data = decrypt(data, self.DH_keys[i])
                    print(data)
                    prefix, data = data[0], data[1:]
                    if prefix == 0:  # overlapped players update
                        state_update = NormalServer.StateUpdateNoAck(ser=data)

                        self.players_updates.extend(state_update.player_changes)
                        self.enemy_changes.extend(state_update.enemy_changes)
                        self.item_changes.extend(state_update.item_changes)

                        for player_update in state_update.player_changes:
                            self.handle_read_only_player_update(player_update)

                    elif prefix == 1:  # enemy control transfer
                        enemy_details: NormalServer.EnemyDetails = NormalServer.EnemyDetails(ser=data)
                        enemy_info = {enemy_details.enemy_name: {'health': enemy_details.health, 'xp': enemy_details.xp,
                                                                 'speed': enemy_details.speed,
                                                                 'damage': enemy_details.damage,
                                                                 'resistance': enemy_details.resistance,
                                                                 'attack_radius': enemy_details.attack_radius,
                                                                 'notice_radius':
                                                                     enemy_details.notice_radius,
                                                                 'death_items': enemy_details.death_items,
                                                                 'move_cooldown': enemy_details.move_cooldown}}
                        print("######################")
                        enemy = Enemy(enemy_name=enemy_details.enemy_name, pos=enemy_details.pos,
                                      groups=(self.enemies, self.all_obstacles, self.alive_entities),
                                      entity_id=enemy_details.entity_id, obstacle_sprites=self.all_obstacles,
                                      item_sprites=self.items,
                                      create_explosion=self.create_explosion, create_bullet=self.create_bullet,
                                      get_free_item_id=self.get_free_item_id, enemies_info=enemy_info)
                        print(enemy.hitbox)

                    elif prefix == 2:  # item in my region
                        item_details_list = NormalServer.ItemDetailsList(ser=data).item_details_list
                        for item_details in item_details_list:
                            item = Item(item_details.name, (self.items,), item_details.pos, item_details.id)
                            item.actions.append(
                                Client.Output.ItemActionUpdate(action_type='move', pos=tuple(item.rect.center)))

                    elif prefix == 3:  # details about player moving to my region
                        player_data = PlayerData(ser=data)
                        for player in self.read_only_players:
                            if player_data.entity_id == player.entity_id:
                                player: Player
                                player.health = player_data.health
                                player.strength = player_data.strength
                                player.resistance = player_data.resistance
                                player.xp = player_data.xp
                                player.inventory_items = player_data.inventory
                                break
                        else:
                            Player((self.read_only_players,), player_data.entity_id, player_data.pos,
                                   player_data.health, player_data.resistance,
                                   player_data.strength, player_data.xp, player_data.inventory, self.create_bullet,
                                   self.create_kettle, self.weapons, self.create_attack, self.items,
                                   self.get_free_item_id, self.spawn_enemy_from_egg, self.magnetic_players,
                                   self.activate_lightning)

    def add_overlapped_update(self,
                              update: Client.Output.PlayerUpdate | Client.Output.EnemyUpdate | Client.Output.ItemUpdate):
        pos = update.pos if isinstance(update, Client.Output.PlayerUpdate) or isinstance(update,
                                                                                         Client.Output.EnemyUpdate) else \
            update.actions[0].pos
        dict_lists = [self.output_overlapped_players_updates, self.output_overlapped_enemies_updates,
                      self.output_overlapped_items_updates]
        dict_list = dict_lists[0] if isinstance(update, Client.Output.PlayerUpdate) else (
            dict_lists[1] if isinstance(update, Client.Output.EnemyUpdate) else dict_lists[2])

        if self.my_server_index != 0 and pos in Rect(0, 0, self.center.x + OVERLAPPING_AREA_T,
                                                     self.center.y + OVERLAPPING_AREA_T):
            dict_list[0][update.id] = update

        if self.my_server_index != 1 and pos in Rect(self.center.x - OVERLAPPING_AREA_T, 0, MAP_WIDTH,
                                                     self.center.y + OVERLAPPING_AREA_T):
            dict_list[1][update.id] = update

        if self.my_server_index != 2 and pos in Rect(0, self.center.x - OVERLAPPING_AREA_T,
                                                     self.center.x + OVERLAPPING_AREA_T, MAP_HEIGHT):
            dict_list[2][update.id] = update

        if self.my_server_index != 3 and pos in Rect(self.center.x - OVERLAPPING_AREA_T,
                                                     self.center.y - OVERLAPPING_AREA_T, MAP_WIDTH, MAP_HEIGHT):
            dict_list[3][update.id] = update

    def find_suitable_server_index(self, pos: Point) -> int:
        b0 = pos.x > self.center.x
        b1 = pos.y > self.center.y
        return 2 * b1 + b0

    def send_change_server(self, client_manager: ClientManager, change_server_msg: Client.Output.ChangeServerMsg):
        time.sleep(0.3)
        client_manager.send_change_server(change_server_msg)
        self.change_ids.remove(client_manager.player.entity_id)
        self.client_managers.remove(client_manager)

    def handle_cmds(self, cmds: List[Tuple[ClientManager, Client.Input.ClientCMD]]):
        for cmd in cmds:
            client_manager = cmd[0]
            client_cmd = cmd[1]

            # TODO what if player died and then cmd arrived
            player_update: Client.Input.PlayerUpdate = client_cmd.player_changes
            player = client_manager.player
            if player.entity_id in self.change_ids:
                continue

            # Update the player
            player.process_client_updates(player_update)

            changes = {'pos': (player.rect.x, player.rect.y), 'attacks': player.attacks, 'status': player.status,
                       'health': player.health}

            player_update = Client.Output.PlayerUpdate(id=player.entity_id, changes=changes)

            self.add_overlapped_update(player_update)

            player_pos = player.get_pos()
            suitable_server_index = self.find_suitable_server_index(player_pos)
            if suitable_server_index != self.my_server_index:
                print('bye')
                encrypted_id: bytes = encrypt(player.entity_id.to_bytes(MAX_ENTITY_ID_SIZE, 'little'),
                                              self.DH_keys[suitable_server_index])
                player_data = PlayerData(entity_id=player.entity_id, pos=(player_pos.x, player_pos.y), health=player.health,
                                         strength=player.strength, resistance=player.resistance,
                                         xp=player.xp, inventory=player.inventory_items)

                self.send_to_normal_server(suitable_server_index, b'\x03' + player_data.serialize())

                self.change_ids.append(player.entity_id)
                threading.Thread(target=self.send_change_server, args=(client_manager, Client.Output.ChangeServerMsg(NORMAL_SERVERS_FOR_CLIENT[suitable_server_index], encrypted_id, self.my_server_index))).start()

                self.players.remove(player)
                self.alive_entities.remove(player)
                self.obstacle_sprites.remove(player)
                self.all_obstacles.remove(player)

                self.read_only_players.add(player)

            client_manager.ack = client_cmd.seq  # The CMD has been taken care of; Update the ack accordingly

    def send_to_normal_server(self, server_index: int, msg: bytes):
        msg = encrypt(msg, self.DH_keys[server_index])
        self.sock_to_other_normals[server_index].sendto(msg,
                                                        (NORMAL_SERVERS[server_index] + self.my_server_index).addr())

    def run(self):

        # Create custom events
        cmd_received_event = pygame.USEREVENT + 1

        tick_count = 0

        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == cmd_received_event:
                    self.handle_cmds(event.cmds)

            dt = self.clock.tick(FPS) / 1000
            tick_count += 1

            # Run enemies simulation
            for enemy in self.enemies.sprites():
                enemy.dt = dt
                enemy.update()
                enemy.enemy_update(self.players)

                if enemy.dead:
                    enemy.status = 'dead'
                current_enemy_state = {'pos': (enemy.rect.x, enemy.rect.y), 'attacks': tuple(enemy.attacks),
                                       'status': enemy.status}
                if enemy.previous_state != current_enemy_state:
                    enemy_pos: Point = enemy.get_pos()
                    suitable_server_index = self.find_suitable_server_index(enemy_pos)
                    if suitable_server_index != self.my_server_index:
                        enemy_pos: Point = enemy.get_pos()
                        enemy_details = NormalServer.EnemyDetails(entity_id=enemy.entity_id,
                                                                  pos=(enemy_pos.x, enemy_pos.y),
                                                                  enemy_name=enemy.enemy_name, health=enemy.health,
                                                                  xp=enemy.xp, speed=enemy.speed, damage=enemy.damage,
                                                                  resistance=enemy.resistance,
                                                                  attack_radius=enemy.attack_radius,
                                                                  notice_radius=enemy.notice_radius,
                                                                  death_items=enemy.death_items,
                                                                  move_cooldown=enemy.move_cooldown)
                        self.send_to_normal_server(suitable_server_index, b'\x01' + enemy_details.serialize())
                        enemy.kill()
                        continue

                    enemy_update = Client.Output.EnemyUpdate(id=enemy.entity_id, type=enemy.enemy_name,
                                                             changes=current_enemy_state)
                    self.enemy_changes.append(enemy_update)
                    self.add_overlapped_update(enemy_update)

                enemy.reset_attacks()
                enemy.previous_state = current_enemy_state
                if enemy.status == 'dead':
                    enemy.kill()

            for proj in self.projectiles.sprites():
                proj.dt = dt
            for player in self.players.sprites():
                player.dt = dt

            self.projectiles.update()
            self.weapons.update()
            self.players.update()
            self.items.update()

            for item in self.items.sprites():
                item.dt = dt
                item.update_movement(self.magnetic_players)

            if tick_count % (FPS // OVERLAPPED_UPDATE_FREQUENCY) == 0:

                for i in self.other_server_indices:
                    if len(self.output_overlapped_players_updates[i]) + len(
                            self.output_overlapped_enemies_updates[i]) + len(
                        self.output_overlapped_items_updates[i]) != 0:
                        state_update: NormalServer.StateUpdateNoAck = NormalServer.StateUpdateNoAck(
                            player_changes=tuple(self.output_overlapped_players_updates[i].values()),
                            enemy_changes=tuple(self.output_overlapped_enemies_updates[i].values()),
                            item_changes=tuple(self.output_overlapped_items_updates[i].values())
                        )

                        self.output_overlapped_players_updates[i] = {}
                        self.output_overlapped_enemies_updates[i] = {}
                        self.output_overlapped_items_updates[i] = {}

                        self.send_to_normal_server(i, b'\x00' + state_update.serialize())

            if tick_count % (FPS // SEND_TO_LB_FREQUENCY) == 0:
                player_central_list = PlayerCentralList(
                    players=[PlayerCentral(pos=PointSer(x=player.get_pos().x, y=player.get_pos().y),
                                           player_id=player.entity_id) for player in
                             self.players])
                self.sock_to_LB.send(player_central_list.serialize())

            if tick_count % (FPS / UPDATE_FREQUENCY) == 0:
                player_changes = []
                for player in self.players.sprites():
                    if player.dead:
                        player.status = 'dead'
                    current_player_state = {'pos': (player.rect.x, player.rect.y), 'attacks': player.attacks,
                                            'status': player.status, 'health': player.health}
                    if player.previous_state != current_player_state:
                        player_update = Client.Output.PlayerUpdate(id=player.entity_id, changes=current_player_state)
                        player_changes.append(player_update)
                    player.reset_attacks()
                    player.previous_state = current_player_state
                    if player.status == 'dead':
                        player.kill()
                self.players_updates.extend(player_changes)

                item: Item
                for item in self.items.sprites():

                    if tuple(item.rect.center) != item.previous_pos and item.previous_pos != ():
                        item.actions.append(
                            Client.Output.ItemActionUpdate(action_type='move', pos=tuple(item.rect.center)))

                    if not item.actions:
                        continue  # don't send if no new actions
                    item_update = Client.Output.ItemUpdate(id=item.item_id, name=item.str_name, actions=item.actions)
                    self.add_overlapped_update(item_update)
                    self.item_changes.append(item_update)
                    item.reset_actions()
                    item.previous_pos = tuple(item.rect.center)
                    if item.die:
                        item.kill()

                state_update: Client.Output.StateUpdateNoAck = Client.Output.StateUpdateNoAck(
                    tuple(self.players_updates), tuple(self.enemy_changes), tuple(self.item_changes))
                self.broadcast_msg(state_update)
                self.players_updates = []
                self.enemy_changes = []
                self.item_changes = []

            # Check if a cmd was received
            cmds: List[(ClientManager, Client.Input.ClientCMD)] = []
            while not self.cmd_queue.empty():

                # Get the message from the queue
                try:
                    client_manager: ClientManager
                    client_msg: Client.Input.ClientCMD
                    client_manager, client_cmd = self.cmd_queue.get_nowait()
                    cmds.append((client_manager, client_cmd))

                except Empty:
                    break

            # Post the event
            if cmds:
                pygame.event.post(pygame.event.Event(cmd_received_event, {"cmds": cmds}))

        pygame.quit()

    def create_attack(self, player):
        player.current_weapon = Weapon(player, (player.weapons_group,), 2, self.alive_entities)

    def create_bullet(self, source: Union[Player, Enemy], pos, mouse):
        direction = pygame.math.Vector2(mouse)
        if not isinstance(source, Enemy):
            source.attacks.append(
                Client.Output.AttackUpdate(weapon_id=source.weapon_index, attack_type=1, direction=mouse))
            damage = int(weapon_data['nerf']['damage'] + (0.1 * source.strength))
        else:
            direction = pygame.math.Vector2(mouse[0] - source.rect.center[0], mouse[1] - source.rect.center[1])
            source.attacks.append(Client.Output.EnemyAttackUpdate(direction=mouse))
            damage = source.damage

        Projectile(source, pos, direction, (self.obstacle_sprites, self.projectiles),
                   self.all_obstacles, 4, 500, 5, './graphics/weapons/bullet.png', damage)

    def create_kettle(self, player: Player, pos, mouse):
        direction = pygame.math.Vector2(mouse)
        player.attacks.append(Client.Output.AttackUpdate(weapon_id=player.weapon_index, attack_type=1, direction=mouse))
        Projectile(player, pos, direction, (self.obstacle_sprites, self.projectiles),
                   self.all_obstacles, 4, 75, 3, './graphics/weapons/kettle/full.png',
                   int(weapon_data['kettle']['damage'] + (0.1 * player.strength)), 'explode', self.create_explosion,
                   True)

    def create_explosion(self, pos, damage):
        Explosion(pos, damage, (), pygame.sprite.Group(self.all_obstacles.sprites() + self.items.sprites()))

    def activate_lightning(self, source: Player):
        for entity in self.alive_entities.sprites():
            if Vector2(source.rect.center).distance_squared_to(
                    Vector2(entity.rect.center)) < LIGHTNING_RADIUS_SQUARED and entity != source:
                entity.deal_damage(LIGHTNING_DAMAGE)

    def spawn_enemy_from_egg(self, pos, name):
        while True:
            random_x = pos[0] // 64 + (random.randint(2, 4) * random.randrange(-1, 2))
            random_y = pos[1] // 64 + (random.randint(2, 4) * random.randrange(-1, 2))

            if int(self.layout['floor'][random_y][random_x]) in SPAWNABLE_TILES and int(
                    self.layout['objects'][random_y][random_x]) == -1:
                Enemy(enemy_name=name, pos=(random_x * 64, random_y * 64),
                      groups=(self.enemies, self.all_obstacles, self.alive_entities),
                      entity_id=next(self.generate_entity_id),
                      obstacle_sprites=self.all_obstacles, item_sprites=self.items,
                      create_explosion=self.create_explosion,
                      create_bullet=self.create_bullet, get_free_item_id=self.get_free_item_id)
                break
