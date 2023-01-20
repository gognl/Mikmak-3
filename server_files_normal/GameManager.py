import threading
from collections import deque
from typing import Tuple

from server_files_normal.ClientManager import ClientManager
from server_files_normal.structures import ClientInputMsg

import pygame


class GameManager(threading.Thread):
	def __init__(self, client_managers: deque):
		super().__init__()
		self.client_managers: deque[ClientManager] = client_managers
		self.queue: deque[Tuple[ClientManager, ClientInputMsg]] = deque()
		threading.Thread(target=self.add_messages_to_queue).start()

	def add_messages_to_queue(self):
		while True:
			for client_manager in self.client_managers:
				self.queue.append(client_manager.get_new_message())

	def run(self):
		while True:
			if len(self.queue) == 0:
				continue

			client_msg = self.queue.pop()


			# TODO: deal with this message
