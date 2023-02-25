import threading
from collections import deque
from queue import Queue, Empty
from typing import Union, Dict

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
from random import randint
import pygame


class GameManager(threading.Thread):
	def __init__(self, client_managers: deque, cmd_semaphore: threading.Semaphore):
		super().__init__()
		self.client_managers: deque[ClientManager] = client_managers
		self.cmd_queue: Queue[Tuple[ClientManager, Client.Input.ClientCMD]] = Queue()
		threading.Thread(target=self.add_messages_to_queue, args=(cmd_semaphore, )).start()

		pygame.init()
		self.clock = pygame.time.Clock()

		self.players: pygame.sprite.Group = pygame.sprite.Group()
		self.enemies: pygame.sprite.Group = pygame.sprite.Group()
		self.alive_entities: pygame.sprite.Group = pygame.sprite.Group()
		self.projectiles: pygame.sprite.Group = pygame.sprite.Group()
		self.weapons: pygame.sprite.Group = pygame.sprite.Group()
		self.items: pygame.sprite.Group = pygame.sprite.Group()

		self.obstacle_sprites: pygame.sprite.Group = pygame.sprite.Group()  # players & walls
		self.all_obstacles: pygame.sprite.Group = pygame.sprite.Group()  # players, cows, and walls
		#self.initialize_obstacle_sprites()

		# TODO temporary
		for i in range(20):
			pos = (randint(2000, 3000), randint(2000, 3000))
			Enemy(enemy_name='white_cow', pos=pos, groups=(self.enemies, self.all_obstacles, self.alive_entities), entity_id=i, obstacle_sprites=self.all_obstacles)

		# TODO temporary, item spawning
		self.layout: Dict[str, List[List[str]]] = {
			'floor': import_csv_layout('./graphics/map/map_Ground.csv'),
			'objects': import_csv_layout('./graphics/map/map_Objects.csv'),
			'boundary': import_csv_layout('./graphics/map/map_Barriers.csv'),
		}
		for item_id in range(1):
			while True:
				random_x = randint(20, 30)
				random_y = randint(20, 30)
				name = item_names[int(randint(0, len(item_names) - 1))]

				if int(self.layout['floor'][random_y][random_x]) in SPAWNABLE_TILES and int(
						self.layout['objects'][random_y][random_x]) == -1:
					Item(name, (self.items,), (random_x * 64 + 32, random_y * 64 + 32), item_id)
					break

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
		return Player((self.players, self.obstacle_sprites, self.all_obstacles, self.alive_entities), entity_id, pos, self.create_bullet, self.create_kettle, self.weapons, self.create_attack, self.items)

	def send_initial_info(self, client_manager: ClientManager):
		player_data: list = []
		enemies_data: list = []
		items_data: List = []

		for player in self.players.sprites():
			initial_weapon_data: Client.Output.AttackUpdate = Client.Output.AttackUpdate(weapon_id=player.weapon_index, attack_type=0, direction=(0, 0))
			changes = {'pos': (player.rect.x, player.rect.y), 'attacks': (initial_weapon_data,), 'status': player.status}
			player_data.append(Client.Output.PlayerUpdate(id=player.entity_id, changes=changes))

		for enemy in self.enemies.sprites():
			changes = {'pos': (enemy.rect.x, enemy.rect.y), 'direction': (enemy.direction.x, enemy.direction.y)}
			enemies_data.append(Client.Output.EnemyUpdate(id=enemy.entity_id, type=enemy.enemy_name, changes=changes))

		for item in self.items.sprites():
			item_actions = (Client.Output.ItemActionUpdate(pos=tuple(item.rect.center)),)
			items_data.append(Client.Output.ItemUpdate(id=item.item_id, name=item.str_name, actions=item_actions))

		state_update: Client.Output.StateUpdateNoAck = Client.Output.StateUpdateNoAck(tuple(player_data), tuple(enemies_data), tuple(items_data))
		client_manager.send_msg(state_update)

	def handle_cmds(self, cmds: List[Tuple[ClientManager, Client.Input.ClientCMD]]):
		for cmd in cmds:
			client_manager = cmd[0]
			client_cmd = cmd[1]

			# TODO what if player died and then cmd arrived
			player_update: Client.Input.PlayerUpdate = client_cmd.player_changes
			player = client_manager.player

			# Update the player
			player.process_client_updates(player_update)

			client_manager.ack = client_cmd.seq  # The CMD has been taken care of; Update the ack accordingly

	def run(self):

		# Create custom events
		cmd_received_event = pygame.USEREVENT + 1

		tick_count = 0
		enemy_changes = []

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
				enemy_changes.append(Client.Output.EnemyUpdate(id=enemy.entity_id, type=enemy.enemy_name, changes=changes))

			for i in range(CLIENT_FPS // FPS):
				self.players.update()
				self.weapons.update()
				self.projectiles.update()
				self.items.update()

			if tick_count % (FPS/UPDATE_FREQUENCY) == 0:
				player_changes = []
				for player in self.players.sprites():
					current_player_state = {'pos': (player.rect.x, player.rect.y), 'attacks': player.attacks, 'status': player.status}
					if player.previous_state != current_player_state:
						player_update = Client.Output.PlayerUpdate(id=player.entity_id, changes=current_player_state)
						player_changes.append(player_update)
					player.reset_attacks()
					player.previous_state = current_player_state
					if player.status == 'dead':
						player.kill()

				item_changes = []
				item: Item
				for item in self.items.sprites():
					if not item.actions:
						continue  # don't send if no new actions
					item_update = Client.Output.ItemUpdate(id=item.item_id, name=item.str_name, actions=item.actions)
					item_changes.append(item_update)
					item.reset_actions()
					if item.die:
						item.kill()

				state_update: Client.Output.StateUpdateNoAck = Client.Output.StateUpdateNoAck(tuple(player_changes), tuple(enemy_changes), tuple(item_changes))
				self.broadcast_msg(state_update)

				enemy_changes = []

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

	def create_attack(self, player):
		player.current_weapon = Weapon(player, (player.weapons_group,), 2, self.alive_entities)

	def create_bullet(self, source: Union[Player, Enemy], pos, mouse):
		direction = pygame.math.Vector2(mouse)
		source.attacks.append(Client.Output.AttackUpdate(weapon_id=source.weapon_index, attack_type=1, direction=mouse))

		if not isinstance(source, Enemy):
			damage = int(weapon_data['nerf']['damage'] + (0.1 * source.strength))
		else:
			damage = source.damage

		Projectile(source, pos, direction, (self.obstacle_sprites, self.projectiles),
				   self.players, 3, 15, 120, './graphics/weapons/bullet.png', damage)

	def create_kettle(self, player: Player, pos, mouse):
		direction = pygame.math.Vector2(mouse)
		player.attacks.append(Client.Output.AttackUpdate(weapon_id=player.weapon_index, attack_type=1, direction=mouse))
		Projectile(player, pos, direction, (self.obstacle_sprites, self.projectiles),
				   self.all_obstacles, 3, 5, 45, './graphics/weapons/kettle/full.png', int(weapon_data['kettle']['damage'] + (0.1 * player.strength)), 'explode', self.create_explosion, True)

	def create_explosion(self, pos, damage):
		pass
		#Explosion(pos, damage, (self.visible_sprites,), self.visible_sprites)
