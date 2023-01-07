from server_files_normal.serializable import Entity

class LBMsg:
	"""TODO - A class of incoming messages from the load-balancing server"""

	def __init__(self, pkt: bytes):
		"""Unpacks the packet, creates the object"""

		self.granted_entities_write: tuple[Entity] = ()  # A list of entities that are added to the server's region with write access.
		self.taken_entities_write: tuple[int] = ()  # A list of the IDs of the entities that are removed from the server's region (write access removed).
		self.granted_entities_read: tuple[Entity] = ()  # A group of entities that are added to the server's region with read access.
		self.taken_entities_read: tuple[int] = ()  # A list of the IDs of the entities that are removed from the server's region (read access removed).

		self.new_clients: tuple[((str, int), int)] = ()  # A tuple of the new clients to accept: (((ip, port), entity_id),...)
