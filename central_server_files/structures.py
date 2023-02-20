ID = int


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

class MsgToClient:
	def __init__(self, dest_id: ID, msg):
		self.dest_id: ID = dest_id
		self.msg = msg

class Server:
	def __init__(self, ip, port):
		self.ip: str = ip
		self.port: int = port
		self.key: bytes = bytes(0)

	def addr(self):
		return self.ip, self.port

class Rect:
	def __init__(self, x1: int, y1: int, x2: int, y2: int):
		self.x1: int = x1
		self.y1: int = y1
		self.x2: int = x2
		self.y2: int = y2

	def __contains__(self, item):
		assert isinstance(item, Point)
		return self.x1 <= item.x <= self.x2 and self.y1 <= item.y <= self.y2
