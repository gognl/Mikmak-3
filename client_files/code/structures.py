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
				self.item_changes: Tuple[Server.Input.ItemUpdate] = None

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
				self.attacks: Tuple[Server.Input.AttackUpdate] = None
				self.status: str = None

				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return

			def _get_attr(self) -> dict:
				return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'attacks': (tuple, (Server.Output.AttackUpdate, 'o')),
						'status': (str, 'str')}

		class AttackUpdate(Serializable):
			def __init__(self, **kwargs):
				self.weapon_id: int = None
				self.attack_type: int = None
				self.direction: (int, int) = None

				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return

			def _get_attr(self) -> dict:
				return {'weapon_id': (int, 'u_1'), 'attack_type': (int, 'u_1'), 'direction': (tuple, (float, 'f_8'))}

		class EnemyUpdate(Serializable):
			def __init__(self, **kwargs):
				self.id: int = None
				self.pos: (int, int) = None
				self.type: str = None
				self.direction: (int, int) = None
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return

			def _get_attr(self) -> dict:
				return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'type': (str, 'str'), 'direction': (tuple, (float, 'f_8'))}

		class ItemUpdate(Serializable):

			def __init__(self, **kwargs):
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return

				self.id = kwargs.pop('id')
				self.name = kwargs.pop('name')
				self.actions = kwargs.pop('actions')

			def _get_attr(self) -> dict:
				return {'id': (int, 'u_3'), 'name': (str, 'str'),
						'actions': (tuple, (Server.Input.ItemActionUpdate, 'o'))}

		class ItemActionUpdate(Serializable):

			def __init__(self, **kwargs):
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return

				self.player = kwargs.pop('player')  # id of player
				self.action = kwargs.pop('action')  # 'spawn' or 'despawn' or 'pickup' or 'drop' or 'move'
				self.pos = kwargs.pop('pos')  # tuple of item position

			def _get_attr(self) -> dict:
				return {'player': (int, 'u_2'), 'action': (str, 'str'), 'pos': (tuple, (int, 'u_8'))}

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
				self.player_changes = kwargs.pop('player_changes')

			def _get_attr(self) -> dict:
				return {'seq': (int, 'u_4'), 'player_changes': (Server.Output.PlayerUpdate, 'o')}

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
				self.attacks = changes['attacks']
				self.status = changes['status']

			def _get_attr(self) -> dict:
				return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'attacks': (tuple, (Server.Input.AttackUpdate, 'o')), 'status': (str, 'str')}

		class AttackUpdate(Serializable):
			def __init__(self, **kwargs):
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return

				self.weapon_id = kwargs.pop('weapon_id')  # 0 = sword, 1 = rifle, 2 = kettle
				self.attack_type = kwargs.pop('attack_type')  # switch=0, attack=1
				self.direction = kwargs.pop('direction')

			def _get_attr(self) -> dict:
				return {'weapon_id': (int, 'u_1'), 'attack_type': (int, 'u_1'), 'direction': (tuple, (float, 'f_8'))}

class EnemyUpdate:
	def __init__(self, entity_id: int, pos: (int, int)):
		self.entity_id = entity_id
		self.pos = pos

class TickUpdate:
	def __init__(self, player_update: Server.Output.PlayerUpdate, enemies_update: List[EnemyUpdate]):
		self.player_update:  Server.Output.PlayerUpdate = player_update
		self.enemies_update: List[EnemyUpdate] = enemies_update
		self.seq: int = Server.Output.StateUpdate.seq_count
