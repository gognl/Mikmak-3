from __future__ import annotations

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

		self.sock_to_other_normals: list[socket.socket] = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(4)]

		for i in range(4):
			if i != my_server_index:
				self.sock_to_other_normals[i].bind(('0.0.0.0', NORMAL_SERVERS[my_server_index].port+i))
				self.sock_to_other_normals[i].settimeout(0.02)

		self.my_server_index = my_server_index

		self.read_only_players = pygame.sprite.Group()
		self.output_seqs = {}
		self.input_seqs = {}
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

		changes = {'pos': (player.rect.x, player.rect.y), 'attacks': player.attacks,
		           'status': player.status}

		player.reset_attacks()
		player_update = Client.Output.PlayerUpdate(id=player.entity_id, changes=changes)

		self.players_updates.append(player_update)

	def receive_from_another_normal_server(self):
		while True:
			for i in range(4):
				if i == self.my_server_index:
					continue

				sock = self.sock_to_other_normals[i]
				try:
					#size: int = unpack("<H", sock.recvfrom(2)[0])[0]
					#print(size)
					data, addr = sock.recvfrom(1024)
				except socket.timeout:
					continue
				except ConnectionResetError:
					print(i)
					continue

				if Server(addr[0], addr[1]-self.my_server_index) in NORMAL_SERVERS:
					if data[0] == 0:  # Player
						player_update = Client.Output.PlayerUpdate(ser=data[3:])
						current_seq: int = unpack("<H", data[1:3])[0]
						seq = self.input_seqs.get(player_update.id, -1)
						if current_seq > seq:
							self.handle_read_only_player_update(player_update)
							self.input_seqs[player_update.id] = current_seq

					else:
						enemy_update = Client.Output.EnemyUpdate(ser=data[3:])
						current_seq: int = unpack("<H", data[1:3])[0]
						seq = self.input_seqs.get(enemy_update.id, -1)
						if current_seq > seq:
							self.enemy_changes.append(enemy_update)
							self.input_seqs[enemy_update.id] = current_seq

	def send_entity_update_to_another_normal_server(self, server_index: int, entity_update: Client.Output.PlayerUpdate | Client.Output.EnemyUpdate, prefix: bytes, seq: int):
		msg = entity_update.serialize()
		size: bytes = pack("<H", 3+len(msg))
		seq: bytes = pack("<H", seq)
		#self.sock_to_other_normals[server_index].sendto(size, (NORMAL_SERVERS[server_index]+self.my_server_index).addr())
		self.sock_to_other_normals[server_index].sendto(prefix + seq + msg, (NORMAL_SERVERS[server_index]+self.my_server_index).addr())

	def send_overlapped_entities_details(self, entity_update: Client.Output.PlayerUpdate | Client.Output.EnemyUpdate):
		pos = entity_update.pos
		is_overlapped = False
		prefix = b'\x00' if isinstance(entity_update, Client.Output.PlayerUpdate) else b'\x01'
		seq = self.output_seqs.get(entity_update.id, 0)

		if self.my_server_index != 0 and pos in Rect(0, 0, self.center.x + OVERLAPPING_AREA_T, self.center.y + OVERLAPPING_AREA_T):
			self.send_entity_update_to_another_normal_server(0, entity_update, prefix, seq)
			is_overlapped = True

		if self.my_server_index != 1 and pos in Rect(self.center.x - OVERLAPPING_AREA_T, 0, MAP_WIDTH, self.center.y + OVERLAPPING_AREA_T):
			self.send_entity_update_to_another_normal_server(1, entity_update, prefix, seq)
			is_overlapped = True

		if self.my_server_index != 2 and pos in Rect(0, self.center.x - OVERLAPPING_AREA_T, self.center.x + OVERLAPPING_AREA_T, MAP_HEIGHT):
			self.send_entity_update_to_another_normal_server(2, entity_update, prefix, seq)
			is_overlapped = True

		if self.my_server_index != 3 and pos in Rect(self.center.x - OVERLAPPING_AREA_T, self.center.y - OVERLAPPING_AREA_T, MAP_WIDTH, MAP_HEIGHT):
			self.send_entity_update_to_another_normal_server(3, entity_update, prefix, seq)
			is_overlapped = True

		if is_overlapped:
			self.output_seqs[entity_update.id] = seq+1

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

			self.send_overlapped_entities_details(player_update)

			self.players_updates.append(player_update)

			client_manager.ack = client_cmd.seq  # The CMD has been taken care of; Update the ack accordingly

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
				self.send_overlapped_entities_details(enemy_update)
				self.enemy_changes.append(enemy_update)

			for i in range(CLIENT_FPS // FPS):
				self.players.update()
				self.projectiles.update()

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
