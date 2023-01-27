from typing import Tuple

from client_files.code.serializable import Serializable


class StateUpdateMsg(Serializable):
	"""A class of an incoming message from the server"""

	def __init__(self, **kwargs):
		self.changes: Tuple[(int, ServerOutputMsg)] = None  # id & update

		s: bytes = kwargs.pop('ser', b'')
		super().__init__(ser=s)
		if s != b'':
			return

	def _get_attr(self) -> dict:
		return {'changes': (tuple, (tuple, (int, 'u_2'), (ServerOutputMsg, 'o')))}

class ServerOutputMsg(Serializable):
	"""
    A class of messages to the server - output
    corresponds to ClientInputMsg
    """

	def __init__(self, **kwargs):
		s: bytes = kwargs.pop('ser', b'')
		super().__init__(ser=s)
		if s != b'':
			return

		self.pos: (int, int) = kwargs.pop('new_pos')

	def _get_attr(self) -> dict:
		return {'pos': (tuple, (int, 'u_8'))}
