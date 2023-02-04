import threading
from collections import deque
from server_files_normal.ClientManager import ClientManager
from server_files_normal.structures import *


class GameManager(threading.Thread):
	def __init__(self, client_managers: deque):
		super().__init__()
		self.client_managers: deque[ClientManager] = client_managers
		self.client_msgs_queue: deque[Tuple[ClientManager, Client.Input.ClientCMD]] = deque()
		threading.Thread(target=self.add_messages_to_queue).start()

	def add_messages_to_queue(self):
		while True:
			for client_manager in list(self.client_managers):
				if client_manager.has_messages():
					self.client_msgs_queue.append(client_manager.get_new_message())

	def broadcast_msg(self, msg: Client.Output.StateUpdateNoAck):
		for client_manager in list(self.client_managers):
			client_manager.send_msg(msg)

	def run(self):
		while True:
			if len(self.client_msgs_queue) == 0:
				continue

			# Receive a CMD
			client_manager: ClientManager
			client_msg: Client.Input.ClientCMD
			client_manager, client_msg = self.client_msgs_queue.pop()

			# Calculations here

			client_manager.ack = client_msg.seq  # The CMD has been taken care of; Update the ack accordingly

			# Send the update
			changes = client_msg.player_changes[0],  # notice the comma here - it's a tuple of tuples
			state_update: Client.Output.StateUpdateNoAck = Client.Output.StateUpdateNoAck(changes)
			self.broadcast_msg(state_update)
			# TODO: deal with this message
