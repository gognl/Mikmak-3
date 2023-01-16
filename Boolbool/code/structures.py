
class ServerMessage:  # TODO
	"""A class of an incoming message from the server"""

	def __init__(self, pkt: bytes):
		"""Unpacks the packet, creates the object"""
		pass
		self.ack: int

	def get_ack(self) -> int:
		"""Returns the sequence number of the last accepted cmd at the time of sending the server message"""
		return self.ack
