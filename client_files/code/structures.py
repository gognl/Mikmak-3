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
				self.player_changes: Tuple[Server.Input.PlayerUpdate] = kwargs.pop('player_changes', ())
				self.enemy_changes: Tuple[Server.Input.EnemyUpdate] = kwargs.pop('enemy_changes', ())
				self.item_changes: Tuple[Server.Input.ItemUpdate] = kwargs.pop('item_changes', ())

			def _get_attr(self) -> dict:
				return {'player_changes': (tuple, (Server.Input.PlayerUpdate, 'o')),
						'enemy_changes': (tuple, (Server.Input.EnemyUpdate, 'o')),
						'item_changes': (tuple, (Server.Input.ItemUpdate, 'o'))}

		class PlayerUpdate(Serializable):
			"""
			A class of messages from the server - input
			"""

			def __init__(self, **kwargs):

				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					self.status: str = {0: 'up', 1: 'down', 2: 'left', 3: 'right', 4: 'up_idle', 5: 'down_idle', 6: 'left_idle', 7: 'right_idle', 8: 'dead'}.get(self.status)
					self.pos: Tuple[int, int] = (self._pos_x, self._pos_y)
					return

				# For interpolation
				data: dict = kwargs.pop('data')
				self.id: int = data.pop('id')
				self.pos: Tuple[int, int] = data.pop('pos')
				self.attacks: Tuple[Server.Input.AttackUpdate] = data.pop('attacks')
				self.status: str = data.pop('status')
				self.health: int = data.pop('health')

			def _get_attr(self) -> dict:
				return {'id': (int, 'u_2'), '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2'), 'attacks': (tuple, (Server.Input.AttackUpdate, 'o')),
						'status': (int, 'u_1'), 'health': (int, 'u_1')}

		class AttackUpdate(Serializable):
			def __init__(self, **kwargs):
				self.weapon_id: int = None
				self.attack_type: int = None
				self.direction: (int, int) = None

				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					self.direction = (self._direction_x, self._direction_y)
					return

			def _get_attr(self) -> dict:
				return {'weapon_id': (int, 'u_1'), 'attack_type': (int, 'u_1'), '_direction_x': (int, 's_2'), '_direction_y': (int, 's_2')}

		class EnemyUpdate(Serializable):
			def __init__(self, **kwargs):

				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					self.pos = (self._pos_x, self._pos_y)
					self.type = {0: 'white_cow', 1: 'green_cow', 2: 'red_cow', 3: 'yellow_cow'}.get(self.type)
					self.status = 'dead' if self._is_dead else ''
					return

				# For interpolation
				data = kwargs.pop('data')
				self.id: int = data.pop('id')
				self.pos: (int, int) = data.pop('pos')
				self.type: str = data.pop('type')
				self.status: str = data.pop('status')
				self.attacks: Tuple[Server.Input.EnemyAttackUpdate] = data.pop('attacks')

			def _get_attr(self) -> dict:
				return {'id': (int, 'u_2'), '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2'), 'type': (int, 'u_1'), 'attacks': (tuple, (Server.Input.EnemyAttackUpdate, 'o')), '_is_dead': (bool, 'b')}

		class EnemyAttackUpdate(Serializable):
			def __init__(self, **kwargs):
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					self.direction = (self._direction_x, self._direction_y)
					return

				self.direction = None  # if it's (0, 0) then it's an exploding red cow

			def _get_attr(self) -> dict:
				return {'_direction_x': (int, 's_2'), '_direction_y': (int, 's_2')}

		class ItemUpdate(Serializable):

			def __init__(self, **kwargs):
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					self.name = {0: 'heal',
								 1: 'strength',
								 2: 'kettle',
								 3: 'shield',
								 4: 'spawn_white',
								 5: 'spawn_green',
								 6: 'spawn_red',
								 7: 'spawn_yellow',
								 8: 'xp'
								 }.get(self.name)
					return

				self.id = kwargs.pop('id')
				self.name = kwargs.pop('name')
				self.actions = kwargs.pop('actions')

			def _get_attr(self) -> dict:
				return {'id': (int, 'u_3'), 'name': (int, 'u_1'),
						'actions': (tuple, (Server.Input.ItemActionUpdate, 'o'))}

		class ItemActionUpdate(Serializable):

			def __init__(self, **kwargs):
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					self.action_type = {0: 'spawn', 1: 'despawn', 2: 'pickup', 3: 'drop', 4: 'move', 5: 'use'}.get(self.action_type)
					self.pos = (self._pos_x, self._pos_y)
					return

				self.player_id = kwargs.pop('player_id')  # id of player
				self.action_type = kwargs.pop('action_type')  # 'spawn' or 'despawn' or 'pickup' or 'drop' or 'move' or 'use'
				self.pos = kwargs.pop('pos')  # tuple of item position

			def _get_attr(self) -> dict:
				return {'player_id': (int, 'u_2'), 'action_type': (int, 'u_1'), '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2')}

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
				self.item_actions = changes['item_actions']

			def _get_attr(self) -> dict:
				return {'id': (int, 'u_2'),
						'pos': (tuple, (int, 'u_8')),
						'attacks': (tuple, (Server.Input.AttackUpdate, 'o')),
						'status': (str, 'str'),
						'item_actions': (tuple, (Server.Output.ItemActionUpdate, 'o'))}

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
				return {'weapon_id': (int, 'u_1'), 'attack_type': (int, 'u_1'), 'direction': (tuple, (int, 's_2'))}

		class ItemActionUpdate(Serializable):
			def __init__(self, **kwargs):
				s: bytes = kwargs.pop('ser', b'')
				super().__init__(ser=s)
				if s != b'':
					return

				self.item_name = kwargs.pop('item_name')
				self.action_type = kwargs.pop('action_type')  # 'drop' or 'use' or 'skill'
				self.item_id = kwargs.pop('item_id')  # if skill, then 1=speed, 2=magnet, 3=damage

			def _get_attr(self) -> dict:
				return {'item_name': (str, 'str'), 'action_type': (str, 'str'), 'item_id': (int, 'u_3')}

class EnemyUpdate:
	def __init__(self, entity_id: int, pos: (int, int)):
		self.entity_id = entity_id
		self.pos = pos

class TickUpdate:
	def __init__(self, player_update: Server.Output.PlayerUpdate):
		self.player_update:  Server.Output.PlayerUpdate = player_update
		self.seq: int = Server.Output.StateUpdate.seq_count

class InventorySlot:
	def __init__(self, item_id):
		self.count = 1
		self.item_ids: List[int] = [item_id]  # free ids pool

	def add_item(self, item_id):
		self.count += 1
		self.item_ids.append(item_id)

	def remove_item(self) -> int:
		self.count -= 1
		return self.item_ids.pop()
