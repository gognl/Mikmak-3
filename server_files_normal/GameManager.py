import threading
from collections import deque
from queue import Queue, Empty
from server_files_normal.ClientManager import ClientManager
from server_files_normal.game.player import Player
from server_files_normal.structures import *
from server_files_normal.game.settings import *
import pygame

class GameManager(threading.Thread):
	def __init__(self, client_managers: deque):
		super().__init__()
		self.client_managers: deque[ClientManager] = client_managers
		self.cmd_queue: Queue[Tuple[ClientManager, Client.Input.ClientCMD]] = Queue()
		threading.Thread(target=self.add_messages_to_queue).start()

		pygame.init()
		self.clock = pygame.time.Clock()

		self.players: pygame.sprite.Group = pygame.sprite.Group()
		self.enemies: pygame.sprite.Group = pygame.sprite.Group()

	def add_messages_to_queue(self):
		while True:
			for client_manager in list(self.client_managers):
				if client_manager.has_messages():
					self.cmd_queue.put(client_manager.get_new_message())

	def broadcast_msg(self, msg: Client.Output.StateUpdateNoAck):
		for client_manager in list(self.client_managers):
			client_manager.send_msg(msg)

	def add_player(self, entity_id: int):
		pos: (int, int) = (1024, 1024)
		return Player(self.players, entity_id, pos)

	def handle_cmds(self, client_manager: ClientManager, client_cmd: Client.Input.ClientCMD):
		player_update: Client.Input.EntityUpdate = client_cmd.player_changes[0]
		player = client_manager.player

		# Update the player
		player.rect = player.image.get_rect(topleft=player_update.pos)
		player.attacking = player_update.attacking
		player.weapon = player_update.weapon
		player.status = player_update.status

		changes = {'pos': (player.rect.x, player.rect.y), 'attacking': player.attacking, 'weapon': player.weapon, 'status': player.status}
		entity_update = Client.Output.EntityUpdate(id=player.entity_id, changes=changes)
		state_update: Client.Output.StateUpdateNoAck = Client.Output.StateUpdateNoAck((entity_update,))

		client_manager.ack = client_cmd.seq  # The CMD has been taken care of; Update the ack accordingly
		self.broadcast_msg(state_update)

	def run(self):

		# Create custom events
		cmd_received_event = pygame.USEREVENT + 1

		running: bool = True
		while running:
			for event in pygame.event.get():
				if event.type == cmd_received_event:
					self.handle_cmds(event.client_manager, event.client_cmd)

			pass  # Run enemies simulation
			self.clock.tick(FPS)

			# Check if a cmd was received
			if not self.cmd_queue.empty():

				# Get the message from the queue
				try:
					client_manager: ClientManager
					client_msg: Client.Input.ClientCMD
					client_manager, client_cmd = self.cmd_queue.get_nowait()
				except Empty:
					continue

				# Post the event
				pygame.event.post(pygame.event.Event(cmd_received_event, {"client_manager": client_manager, "client_cmd": client_cmd}))

		pygame.quit()
