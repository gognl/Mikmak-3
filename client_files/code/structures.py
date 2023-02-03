from typing import Tuple

from client_files.code.serializable import Serializable


class StateUpdateMsg(Serializable):
	"""A class of an incoming message from the server"""

	def __init__(self, **kwargs):
		self.changes: Tuple[ServerEntityUpdate] = None  # id & update

		s: bytes = kwargs.pop('ser', b'')
		super().__init__(ser=s)
		if s != b'':
			return

	def _get_attr(self) -> dict:
		return {'changes': (tuple, (ServerEntityUpdate, 'o'))}


class ServerEntityUpdate(Serializable):
	"""
	A class of messages from the server - input
	"""

	def __init__(self, **kwargs):
		self.id: int = None
		self.pos: Tuple[int, int] = None
		self.attacking: bool = None
		self.weapon: str = None
		self.status: str = None

		s: bytes = kwargs.pop('ser', b'')
		super().__init__(ser=s)
		if s != b'':
			return

	def _get_attr(self) -> dict:
		return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'attacking': (bool, 'b'), 'weapon': (str, 'str'),
				'status': (str, 'str')}


class ServerOutputMsg(Serializable):
	"""
    A class of messages to the server - output
    corresponds to ClientCMD

    SIZE = 43 BYTES
    """

	def __init__(self, **kwargs):
		s: bytes = kwargs.pop('ser', b'')
		super().__init__(ser=s)
		if s != b'':
			return

		changes = kwargs.pop('changes')
		self.player_changes = changes[0]
		self.enemies_changes = changes[1]
		self.items_changes = changes[2]

	def _get_attr(self) -> dict:
		return {'player_changes': (list, (PlayerUpdate, 'o'))}

class PlayerUpdate(Serializable):
	"""A class containing data about player updates in the last tick"""

	def __init__(self, **kwargs):
		s: bytes = kwargs.pop('ser', b'')
		super().__init__(ser=s)
		if s != b'':
			return

		self.id = kwargs.pop('id')

		changes = kwargs.pop('changes')
		self.pos = changes['pos']
		self.attacking = changes['attacking']
		self.weapon = changes['weapon']
		self.status = changes['status']

	def _get_attr(self) -> dict:
		return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'attacking': (bool, 'b'), 'weapon': (str, 'str'), 'status': (str, 'str')}
