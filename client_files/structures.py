from time import time

class ServerMessage:  # TODO
	"""A class of an incoming message from the server"""

	def __init__(self, pkt: bytes):
		"""Unpacks the packet, creates the object"""
		pass
		self.timestamp = time()
		self.ack: int

		self.entities_positions: list
		self.entities_actions: list

	def get_ack(self) -> int:
		"""Returns the sequence number of the last accepted cmd at the time of sending the server message"""
		return self.ack

	def get_timestamp(self) -> float:
		"""Returns the time when the message was received (Approx.)"""
		return self.timestamp

	def get_entities_positions(self) -> list:
		"""Returns the positions of all the entities (Excluding this client) in this update"""
		return self.entities_positions

	def get_entities_actions(self) -> list:
		"""Returns the actions of all the entities (Excluding the client) in this update"""
		return self.entities_actions
