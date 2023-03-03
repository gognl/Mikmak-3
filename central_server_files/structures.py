from central_server_files.serializable import Serializable

ID = bytes

class Point:
	def __init__(self, x: int, y: int):
		self.x: int = x
		self.y: int = y

	def add(self, other):
		assert isinstance(other, Point)
		self.x += other.x
		self.y += other.y

	def div(self, num):
		assert isinstance(num, int) and num != 0
		self.x //= num
		self.y //= num

	def __repr__(self):
		return f"({self.x}, {self.y})"

	def dist2(self, other):
		assert isinstance(other, Point)
		return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

class PlayerCentral:
	def __init__(self, pos: Point, client_id: ID):
		self.pos: Point = pos
		self.id: ID = client_id

class Server:
	def __init__(self, ip, port):
		self.ip: str = ip
		self.port: int = port

	def addr(self):
		return self.ip, self.port

	def __eq__(self, other):
		assert isinstance(other, Server)
		return self.ip == other.ip and self.port == other.port

class ServerSer(Serializable, Server):
	def __init__(self, **kwargs):
		ser = kwargs.get("ser", b'')
		Serializable.__init__(self, ser)
		if ser != b'':
			return
		Server.__init__(self, kwargs['ip'], kwargs['port'])


		Server.__init__(self, kwargs['ip'], kwargs['port'])

class LB_to_login_msgs:
	def __init__(self, client_id: ID, server: Server):
		self.client_id: ID = client_id
		self.server = server

class LoginResponseToClient(Serializable):
	def __init__(self, **kwargs):
		ser = kwargs.get('ser', b'')
		super().__init__(ser)
		if ser != b'':
			return

		self.encrypted_client_id: bytes = kwargs['encrypted_id']
		self.server: ServerSer = kwargs['server']

class InfoData(Serializable):
	def __init__(self, **kwargs):
		ser = kwargs.get('ser', b'')
		super().__init__(ser)
		if ser != b'':
			return

		self.info: tuple = kwargs['info']

class InfoMsgToNormal(Serializable):
	def __init__(self, **kwargs):
		ser = kwargs.get('ser', b'')
		super().__init__(ser)
		if ser != b'':
			return

		self.encrypted_client_id: bytes = kwargs['encrypted_id']
		self.encrypted_info_list: bytes = kwargs['info']

class Rect:
	def __init__(self, x1: int, y1: int, x2: int, y2: int):
		self.x1: int = x1
		self.y1: int = y1
		self.x2: int = x2
		self.y2: int = y2

	def __contains__(self, item):
		assert isinstance(item, Point)
		return self.x1 <= item.x <= self.x2 and self.y1 <= item.y <= self.y2
