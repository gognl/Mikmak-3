import threading
from collections import deque
from typing import Tuple

from server_files_normal.ClientManager import ClientManager
from server_files_normal.structures import EntityUpdateMsg, StateUpdateMsg, ClientCMD

import pygame


class GameManager(threading.Thread):
	def __init__(self, client_managers: deque):
		super().__init__()
		self.client_managers: deque[ClientManager] = client_managers
		self.client_msgs_queue: deque[Tuple[ClientManager, EntityUpdateMsg]] = deque()
		threading.Thread(target=self.add_messages_to_queue).start()

	def add_messages_to_queue(self):
		while True:
			for client_manager in list(self.client_managers):
				if client_manager.has_messages():
					self.client_msgs_queue.append(client_manager.get_new_message())

	def broadcast_msg(self, msg: StateUpdateMsg):
		for client_manager in self.client_managers:
			client_manager.send_msg(msg)

	def run(self):
		while True:
			if len(self.client_msgs_queue) == 0:
				continue

			client_manager: ClientManager
			client_msg: ClientCMD
			client_manager, client_msg = self.client_msgs_queue.pop()

			changes = client_msg.player_changes[0],  # notice the comma here - it's a tuple of tuples
			state_update: StateUpdateMsg = StateUpdateMsg(changes)
			self.broadcast_msg(state_update)
			# TODO: deal with this message
