from typing import Tuple, List

from client_files.code.serializable import Serializable

class Server:
	class Input:

		class StateUpdate(Serializable):
			"""Like StateUpdate but with an acknowledgement number"""

			def __init__(self, **kwargs):
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return
				self.ack: int = None
				self.state_update: Server.Input.StateUpdateNoAck = None

			def _get_attr(self) -> dict:
				return {'ack': (int, 'u_4'), 'state_update': (Server.Input.StateUpdateNoAck, 'o')}

		class StateUpdateNoAck(Serializable):
			"""A class of an incoming message from the server"""

			def __init__(self, **kwargs):

				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return
				self.player_changes: Tuple[Server.Input.PlayerUpdate] = None
				self.enemy_changes: Tuple[Server.Input.EnemyUpdate] = None

			def _get_attr(self) -> dict:
				return {'player_changes': (tuple, (Server.Input.PlayerUpdate, 'o')),
						'enemy_changes': (tuple, (Server.Input.EnemyUpdate, 'o'))}

		class PlayerUpdate(Serializable):
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
				return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'attacking': (bool, 'b'),
						'weapon': (str, 'str'),
						'status': (str, 'str')}

		class EnemyUpdate(Serializable):
			def __init__(self, **kwargs):
				self.id: int = None
				self.pos: Tuple[int, int] = None
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return

			def _get_attr(self) -> dict:
				return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8'))}

	class Output:
		class StateUpdate(Serializable):
			"""
		    A class of messages to the server - output
		    corresponds to ClientCMD
		    """

			seq_count: int = 0

			def __init__(self, **kwargs):
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return

				self.seq = Server.Output.StateUpdate.seq_count

				changes = kwargs.pop('changes')
				self.player_changes: List[Server.Output.PlayerUpdate] = changes[0]
				self.enemies_changes = changes[1]
				self.items_changes = changes[2]

			def _get_attr(self) -> dict:
				return {'seq': (int, 'u_4'), 'player_changes': (list, (Server.Output.PlayerUpdate, 'o'))}

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
				return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'attacking': (bool, 'b'),
						'weapon': (str, 'str'), 'status': (str, 'str')}
