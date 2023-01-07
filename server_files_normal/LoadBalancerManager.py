import socket
import threading
from collections import deque
from server_files_normal.structures import LBMsg
from server_files_normal.Entity import Entity

class LoadBalancerManager(threading.Thread):
	"""Handles the interactions with the load-balancing server"""
	def __init__(self, lb_addr: (str, int)):
		super().__init__()

		# Connect to the load-balancing server
		self.lb_sock: socket.socket = socket.socket()
		self.lb_sock.connect(lb_addr)

		# The update lists - contain information about changes in the world.
		self.granted_entities_write: deque[Entity] = deque()  # A list of entities that are added to the server's region with write access.
		self.taken_entities_write: deque[int] = deque()  # A list of the IDs of the entities that are removed from the server's region (write access removed).
		self.granted_entities_read: deque[Entity] = deque()  # A list of entities that are added to the server's region with read access.
		self.taken_entities_read: deque[int] = deque()  # A list of the IDs of the entities that are removed from the server's region (read access removed).
		self.new_clients: deque[((str, int), int)] = deque()  # A list of the new clients to accept: [((ip, port), entity_id),...]

		# TODO - Do some initialization stuff with the lb server
		pass

	def run(self) -> None:
		self.handle_lb_connection()

	def get_lb_pkt(self) -> bytes:
		"""
		Gets a packet from the load-balancing server; decrypts it if needed.
		:return: The decrypted message in bytes form.
		"""
		pass

	def handle_lb_connection(self) -> None:
		"""
		Handles the connection with the lb server; Updates the update lists, which are read by the main code.
		:return: None
		"""
		while True:
			# Receive a message from the lb server
			msg: LBMsg = LBMsg(self.get_lb_pkt())

			# Update the update lists
			self.granted_entities_write.extend(msg.granted_entities_write)
			self.taken_entities_write.extend(msg.taken_entities_write)
			self.granted_entities_read.extend(msg.granted_entities_read)
			self.taken_entities_read.extend(msg.taken_entities_read)
			self.new_clients.extend(msg.new_clients)
