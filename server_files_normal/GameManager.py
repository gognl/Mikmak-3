from __future__ import annotations

import random
import threading
from collections import deque
from queue import Queue, Empty
import socket
from struct import unpack, pack

import client_files.code.settings
from server_files_normal.game.projectile import Projectile
from server_files_normal.game.support import import_csv_layout
from server_files_normal.ClientManager import ClientManager
from server_files_normal.game.barrier import Barrier
from server_files_normal.game.enemy import Enemy
from server_files_normal.game.player import Player
from server_files_normal.structures import *
from server_files_normal.game.settings import *
from random import randint
import pygame

class GameManager(threading.Thread):
    def __init__(self, client_managers: deque, cmd_semaphore: threading.Semaphore, my_server_index: int):
        super().__init__()
        self.client_managers: deque[ClientManager] = client_managers
        self.cmd_queue: Queue[Tuple[ClientManager, Client.Input.ClientCMD]] = Queue()
        threading.Thread(target=self.add_messages_to_queue, args=(cmd_semaphore, )).start()

        pygame.init()
        self.clock = pygame.time.Clock()

        self.players: pygame.sprite.Group = pygame.sprite.Group()
        self.enemies: pygame.sprite.Group = pygame.sprite.Group()
        self.projectiles: pygame.sprite.Group = pygame.sprite.Group()

        self.players_updates: List[Client.Output.PlayerUpdate] = []
        self.enemy_changes: List[Client.Output.EnemyUpdate] = []

        self.obstacle_sprites: pygame.sprite.Group = pygame.sprite.Group()  # players & walls
        self.all_obstacles: pygame.sprite.Group = pygame.sprite.Group()  # players, cows, and walls
        self.sock_to_login: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_to_other_normals: list[socket.socket] = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(4)]

        self.my_server_index = my_server_index
        self.other_server_indices = [i for i in range(4) if i != my_server_index]

        for i in self.other_server_indices:
            self.sock_to_other_normals[i].bind(('0.0.0.0', NORMAL_SERVERS[my_server_index].port+i))
            self.sock_to_other_normals[i].settimeout(0.02)

        # self.sock_to_login.connect(CENTRAL_SERVER.addr())

        self.DH_keys: list[bytes] = [bytes(0) for _ in range(4)]
        self.DH_login_key: bytes = bytes(0)
        a = random.randrange(DH_p)

        def DH_with_normal(server_index: int, keys_list: list[bytes]):
            x = pow(DH_g, a, DH_p)
            self.sock_to_other_normals[server_index].sendto(x.to_bytes(128, 'little'), (NORMAL_SERVERS[server_index]+my_server_index).addr())
            y, addr = 0, ('0.0.0.0', 0)
            while not Server(addr[0], addr[1]-my_server_index) == NORMAL_SERVERS[server_index]:
                try:
                    y, addr = self.sock_to_other_normals[server_index].recvfrom(1024)
                except socket.timeout:
                    continue

            keys_list[server_index] = pow(int.from_bytes(y, 'little'), a, DH_p).to_bytes(128, 'little')

        def DH_with_login():
            x = pow(DH_g, a, DH_p)
            self.sock_to_login.send(x.to_bytes(128, 'little'))
            y, addr = 0, ('0.0.0.0', 0)
            y = self.sock_to_login.recv(1024)
            self.DH_login_key = pow(int.from_bytes(y, 'little'), a, DH_p).to_bytes(128, 'little')


        DH_threads: list[threading.Thread] = []
        for i in self.other_server_indices:
            DH_threads.append(threading.Thread(target=DH_with_normal, args=(i, self.DH_keys)))

        DH_threads.append(threading.Thread(target=DH_with_login))

        # for thread in DH_threads:
        # 	thread.start()
        # for thread in DH_threads:
        # 	thread.join()

        self.read_only_players = pygame.sprite.Group()
        self.output_overlapped_players_updates: list[dict[int, Client.Output.PlayerUpdate]] = [{}, {}, {}, {}]
        self.output_overlapped_enemies_updates: list[dict[int, Client.Output.EnemyUpdate]] = [{}, {}, {}, {}]
        self.center: Point = Point(MAP_WIDTH//2, MAP_HEIGHT//2)
        threading.Thread(target=self.receive_from_another_normal_server).start()

        #self.initialize_obstacle_sprites()

        # TODO temporary
        for i in range(20):
            pos = (randint(2000, 3000), randint(2000, 3000))
            Enemy(enemy_name='white_cow', pos=pos, groups=(self.enemies, self.all_obstacles), entity_id=i, obstacle_sprites=self.all_obstacles)

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
                    Barrier((x, y), (self.obstacle_sprites,))

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
        pos: (int, int) = (1024, 1024)
        return Player((self.players, self.obstacle_sprites, self.all_obstacles), entity_id, pos, self.create_bullet, self.create_kettle)

    def handle_read_only_player_update(self, player_update: Client.Input.PlayerUpdate):
        for p in self.read_only_players:
            if player_update.id == p.entity_id:
                player = p
                break
        else:
            player = Player((self.read_only_players,), player_update.id, player_update.pos, self.create_bullet,
                            self.create_kettle)

        # Update the player
        player.process_client_updates(player_update)

        player.reset_attacks()

    def receive_from_another_normal_server(self):
        while True:
            for i in self.other_server_indices:
                sock = self.sock_to_other_normals[i]
                try:
                    data, addr = sock.recvfrom(1024)
                except socket.timeout:
                    continue
                except ConnectionResetError:
                    print(i)
                    continue
                if Server(addr[0], addr[1]-self.my_server_index) == NORMAL_SERVERS[i]:
                    data = Encryption.decrypt(data, self.DH_keys[i])

                    state_update = NormalServer.Output.StateUpdateNoAck(ser=data)
                    self.players_updates.extend(state_update.player_changes)
                    self.enemy_changes.extend(state_update.enemy_changes)

                    for player_update in state_update.player_changes:
                        self.handle_read_only_player_update(player_update)

    def add_overlapped_entity_update(self, entity_update: Client.Output.PlayerUpdate | Client.Output.EnemyUpdate):
        pos = entity_update.pos
        dict_list = self.output_overlapped_players_updates if isinstance(entity_update, Client.Output.PlayerUpdate) else self.output_overlapped_enemies_updates

        if self.my_server_index != 0 and pos in Rect(0, 0, self.center.x + OVERLAPPING_AREA_T, self.center.y + OVERLAPPING_AREA_T):
            dict_list[0][entity_update.id] = entity_update

        if self.my_server_index != 1 and pos in Rect(self.center.x - OVERLAPPING_AREA_T, 0, MAP_WIDTH, self.center.y + OVERLAPPING_AREA_T):
            dict_list[1][entity_update.id] = entity_update

        if self.my_server_index != 2 and pos in Rect(0, self.center.x - OVERLAPPING_AREA_T, self.center.x + OVERLAPPING_AREA_T, MAP_HEIGHT):
            dict_list[2][entity_update.id] = entity_update

        if self.my_server_index != 3 and pos in Rect(self.center.x - OVERLAPPING_AREA_T, self.center.y - OVERLAPPING_AREA_T, MAP_WIDTH, MAP_HEIGHT):
            dict_list[3][entity_update.id] = entity_update

    def handle_cmds(self, cmds: List[Tuple[ClientManager, Client.Input.ClientCMD]]):
        for cmd in cmds:
            client_manager = cmd[0]
            client_cmd = cmd[1]

            player_update: Client.Input.PlayerUpdate = client_cmd.player_changes
            player = client_manager.player

            # Update the player
            player.process_client_updates(player_update)

            changes = {'pos': (player.rect.x, player.rect.y), 'attacks': player.attacks, 'status': player.status}
            player.reset_attacks()
            player_update = Client.Output.PlayerUpdate(id=player.entity_id, changes=changes)

            self.add_overlapped_entity_update(player_update)

            self.players_updates.append(player_update)

            client_manager.ack = client_cmd.seq  # The CMD has been taken care of; Update the ack accordingly

    def send_update_to_normal_server(self, server_index: int, update: Client.Output.StateUpdateNoAck):
        msg = update.serialize()
        msg = Encryption.encrypt(msg, self.DH_keys[server_index])
        self.sock_to_other_normals[server_index].sendto(msg, (NORMAL_SERVERS[server_index]+self.my_server_index).addr())

    def run(self):

        # Create custom events
        cmd_received_event = pygame.USEREVENT + 1

        tick_count = 0

        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == cmd_received_event:
                    self.handle_cmds(event.cmds)

            # Run enemies simulation
            for enemy in self.enemies.sprites():
                previous_pos = (enemy.rect.x, enemy.rect.y)
                for i in range(CLIENT_FPS//FPS):
                    enemy.update()
                    enemy.enemy_update(self.players)
                if previous_pos == (enemy.rect.x, enemy.rect.y):
                    continue
                changes = {'pos': (enemy.rect.x, enemy.rect.y), 'direction': (enemy.direction.x, enemy.direction.y)}
                enemy_update = Client.Output.EnemyUpdate(id=enemy.entity_id, type=enemy.enemy_name, changes=changes)
                self.add_overlapped_entity_update(enemy_update)
                self.enemy_changes.append(enemy_update)

            for i in range(CLIENT_FPS // FPS):
                self.players.update()
                self.projectiles.update()

            if tick_count % (FPS // OVERLAPPED_UPDATE_FREQUENCY) == 0:

                for i in self.other_server_indices:
                    state_update: NormalServer.Output.StateUpdateNoAck = NormalServer.Output.StateUpdateNoAck(
                        player_changes=tuple(self.output_overlapped_players_updates[i].values()),
                        enemy_changes=tuple(self.output_overlapped_enemies_updates[i].values()))

                    self.output_overlapped_players_updates[i] = {}
                    self.output_overlapped_enemies_updates[i] = {}

                    self.send_update_to_normal_server(i, state_update)

            if tick_count % (FPS/UPDATE_FREQUENCY) == 0:
                state_update: Client.Output.StateUpdateNoAck = Client.Output.StateUpdateNoAck(tuple(self.players_updates), tuple(self.enemy_changes))
                self.broadcast_msg(state_update)
                self.players_updates.clear()  # clear the list
                self.enemy_changes = []

            self.clock.tick(FPS)
            tick_count += 1

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

    def create_bullet(self, player: Player, mouse):
        direction = pygame.math.Vector2(mouse)
        player.attacks.append(Client.Output.AttackUpdate(weapon_id=player.weapon_index, attack_type=1, direction=mouse))
        Projectile(player, player.current_weapon, direction, (self.obstacle_sprites, self.projectiles),
                   self.obstacle_sprites, 3, 15, 2000, './graphics/weapons/bullet.png')

    def create_kettle(self, player: Player, mouse):
        direction = pygame.math.Vector2(mouse)
        player.attacks.append(Client.Output.AttackUpdate(weapon_id=player.weapon_index, attack_type=1, direction=mouse))
        Projectile(player, player.current_weapon, direction, (self.obstacle_sprites, self.projectiles),
                   self.obstacle_sprites, 3, 5, 750, './graphics/weapons/kettle/full.png', 'explode', True)
