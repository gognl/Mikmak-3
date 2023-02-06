class ID(int):
	def __init__(self):
		super().__init__()

class Point:
	def __init__(self, x: int, y: int):
		self.x: int = x
		self.y: int = y

	def __repr__(self):
		return f"({self.x}, {self.y})"

	def dist2(self, other):
		assert isinstance(other, Point)
		return (self.x - other.x)**2 + (self.y - other.y)**2

class Client:
	def __init__(self, pos: Point, client_id: ID):
		self.pos: Point = pos
		self.id: ID = client_id

class MsgToClient:
	def __init__(self, dest_id: ID, msg):
		self.dest_id: ID = dest_id
		self.msg = msg

class Server:
	def __init__(self):
		self.ip: str
		self.port: int