import threading
from collections import deque
from queue import Queue, Empty
from server_files_normal.ClientManager import ClientManager
from server_files_normal.game.enemy import Enemy
from server_files_normal.game.player import Player
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

		self.players_updates: List[Client.Output.PlayerUpdate] = []

		# TODO temporary
		for i in range(20):
			pos = (randint(1000, 2000), randint(1000, 2000))
			Enemy(enemy_name='white_cow', pos=pos, groups=(self.enemies,), entity_id=i)

	def add_messages_to_queue(self, cmd_semaphore: threading.Semaphore):
		while True:
			cmd_semaphore.acquire()
			for client_manager in list(self.client_managers):
				if client_manager.has_messages():
					self.cmd_queue.put(client_manager.get_new_message())

	def broadcast_msg(self, msg: Client.Output.StateUpdateNoAck):
		for client_manager in list(self.client_managers):
			client_manager.send_msg(msg)

	def add_player(self, entity_id: int):
		pos: (int, int) = (1024, 1024)
		return Player(self.players, entity_id, pos)

	def handle_cmds(self, cmds: List[Tuple[ClientManager, Client.Input.ClientCMD]]):
		for cmd in cmds:
			client_manager = cmd[0]
			client_cmd = cmd[1]

			player_update: Client.Input.PlayerUpdate = client_cmd.player_changes[0]
			player = client_manager.player

			# Update the player
			player.rect = player.image.get_rect(topleft=player_update.pos)
			player.attacking = player_update.attacking
			player.weapon = player_update.weapon
			player.status = player_update.status

			changes = {'pos': (player.rect.x, player.rect.y), 'attacking': player.attacking, 'weapon': player.weapon, 'status': player.status}
			player_update = Client.Output.PlayerUpdate(id=player.entity_id, changes=changes)
			self.players_updates.append(player_update)

			client_manager.ack = client_cmd.seq  # The CMD has been taken care of; Update the ack accordingly

	def run(self):

		# Create custom events
		cmd_received_event = pygame.USEREVENT + 1

		running: bool = True
		while running:
			for event in pygame.event.get():
				if event.type == cmd_received_event:
					self.handle_cmds(event.cmds)

			# Run enemies simulation
			enemy_changes = []
			self.enemies.update()
			for enemy in self.enemies.sprites():
				enemy.enemy_update(self.players)
				changes = {'pos': (enemy.rect.x, enemy.rect.y)}
				enemy_changes.append(Client.Output.EnemyUpdate(id=enemy.entity_id, changes=changes))

			state_update: Client.Output.StateUpdateNoAck = Client.Output.StateUpdateNoAck(tuple(self.players_updates), tuple(enemy_changes))
			self.broadcast_msg(state_update)

			self.clock.tick(FPS)

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
				pygame.event.post(pygame.event.Event(cmd_received_event, {"cmds": cmds}))

		pygame.quit()
