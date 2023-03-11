from typing import Tuple, List

from server_files_normal.serializable import Serializable


class Client:
    class Output:

        class StateUpdate(Serializable):
            """Like StateUpdate but with an acknowledgement number"""

            def __init__(self, ack: int, state_update: 'Client.Output.StateUpdateNoAck'):
                super().__init__(ser=b'')
                self.ack: int = ack
                self.state_update: Client.Output.StateUpdateNoAck = state_update

            def _get_attr(self) -> dict:
                return {'ack': (int, 'u_4'), 'state_update': (Client.Output.StateUpdateNoAck, 'o')}

        class StateUpdateNoAck(Serializable):
            """ A class that describes the message to the client, which contains the current state of relevant game changes"""

            def __init__(self, player_changes: Tuple['Client.Output.PlayerUpdate'],
                         enemy_changes: Tuple['Client.Output.EnemyUpdate'],
                         item_changes: Tuple['Client.Output.ItemUpdate']):
                super().__init__(ser=b'')
                self.player_changes: Tuple[Client.Output.PlayerUpdate] = player_changes
                self.enemy_changes: Tuple[Client.Output.EnemyUpdate] = enemy_changes
                self.item_changes: Tuple[Client.Output.ItemUpdate] = item_changes

            def _get_attr(self) -> dict:
                return {'player_changes': (tuple, (Client.Output.PlayerUpdate, 'o')),
                        'enemy_changes': (tuple, (Client.Output.EnemyUpdate, 'o')),
                        'item_changes': (tuple, (Client.Output.ItemUpdate, 'o'))}

        class PlayerUpdate(Serializable):

            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.id = kwargs.pop('id')

                changes = kwargs.pop('changes')
                pos = changes['pos']
                self._pos_x = pos[0]
                self._pos_y = pos[1]
                self.attacks = changes['attacks']
                status_str = changes['status']
                self.status: int = {'up': 0,
                                    'down': 1,
                                    'left': 2,
                                    'right': 3,
                                    'up_idle': 4,
                                    'down_idle': 5,
                                    'left_idle': 6,
                                    'right_idle': 7,
                                    'dead': 8
                                    }.get(status_str)
                self.health = changes['health']

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'), '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2'),
                        'attacks': (tuple, (Client.Output.AttackUpdate, 'o')), 'status': (int, 'u_1'),
                        'health': (int, 'u_1')}

        class AttackUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.weapon_id = kwargs.pop('weapon_id')  # 0 = sword, 1 = rifle, 2 = kettle
                self.attack_type = kwargs.pop('attack_type')  # switch=0, attack=1, lightning=2
                direction = kwargs.pop('direction')
                self._direction_x = direction[0]
                self._direction_y = direction[1]

            def _get_attr(self) -> dict:
                return {'weapon_id': (int, 'u_1'), 'attack_type': (int, 'u_1'), '_direction_x': (int, 's_2'),
                        '_direction_y': (int, 's_2')}

        class EnemyUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.id = kwargs.pop('id')
                type_str = kwargs.pop('type')
                self.type = {'white_cow': 0, 'green_cow': 1, 'red_cow': 2, 'yellow_cow': 3}.get(type_str)
                changes = kwargs.pop('changes')
                pos = changes['pos']
                self._pos_x = pos[0]
                self._pos_y = pos[1]
                status = changes['status']
                self._is_dead = True if status == 'dead' else False
                self.attacks = changes['attacks']

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'), '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2'), 'type': (int, 'u_1'),
                        'attacks': (tuple, (Client.Output.EnemyAttackUpdate, 'o')), '_is_dead': (bool, 'b')}

        class EnemyAttackUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                direction = kwargs.pop('direction')  # if it's (0, 0) then it's an exploding red cow
                self._direction_x = direction[0]
                self._direction_y = direction[1]

            def _get_attr(self) -> dict:
                return {'_direction_x': (int, 's_2'), '_direction_y': (int, 's_2')}

        class ItemUpdate(Serializable):

            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.id = kwargs.pop('id')
                name = kwargs.pop('name')
                self.name = {'heal': 0,
                             'strength': 1,
                             'kettle': 2,
                             'shield': 3,
                             'spawn_white': 4,
                             'spawn_green': 5,
                             'spawn_red': 6,
                             'spawn_yellow': 7,
                             'xp': 8,
                             }.get(name, 9)
                if 'grave_player' in name:
                    self.name = 10 + int(name[13:-1])
                self.actions = kwargs.pop('actions')

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_3'), 'name': (int, 'u_1'),
                        'actions': (tuple, (Client.Output.ItemActionUpdate, 'o'))}

        class ItemActionUpdate(Serializable):

            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.player_id = kwargs.pop('player_id', 0)  # id of player
                action_type = kwargs.pop('action_type',
                                              'spawn')  # 'spawn' or 'despawn' or 'pickup' or 'drop' or 'move' or 'use'
                self.action_type = {'spawn': 0, 'despawn': 1, 'pickup': 2, 'drop': 3, 'move': 4, 'use': 5}.get(action_type)
                pos = kwargs.pop('pos', (0, 0))  # tuple of item position
                self._pos_x = pos[0]
                self._pos_y = pos[1]

            def _get_attr(self) -> dict:
                return {'player_id': (int, 'u_2'), 'action_type': (int, 'u_1'), '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2')}

    class Input:
        class ClientCMD(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)

                if s != b'':
                    return

                self.seq: int = None
                self.player_changes: Client.Input.PlayerUpdate = None

            def _get_attr(self) -> dict:
                return {'seq': (int, 'u_4'), 'player_changes': (Client.Input.PlayerUpdate, 'o')}

        class PlayerUpdate(Serializable):
            """
            A class of messages from the client - inputs
            corresponds to PlayerUpdate in the client

            Also used as a format for updating clients about other clients' updates
            """

            def __init__(self, **kwargs):
                self.id: int = None
                self.pos: Tuple[int, int] = None
                self.attacks: Tuple[Client.Input.AttackUpdate] = None
                self.status: str = None
                self.item_actions: Tuple[Client.Input.ItemActionUpdate] = None

                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    self.status: str = {0: 'up', 1: 'down', 2: 'left', 3: 'right', 4: 'up_idle', 5: 'down_idle',
                                        6: 'left_idle', 7: 'right_idle', 8: 'dead'}.get(self.status)
                    self.pos = (self._pos_x, self._pos_y)
                    return

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'),
                        '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2'),
                        'attacks': (tuple, (Client.Input.AttackUpdate, 'o')),
                        'status': (int, 'u_1'),
                        'item_actions': (tuple, (Client.Input.ItemActionUpdate, 'o'))}

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

        class ItemActionUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    self.action_type = {0: 'drop', 1: 'use', 2: 'skill'}.get(self.action_type)
                    self.item_name = {0: 'heal',
                                 1: 'strength',
                                 2: 'kettle',
                                 3: 'shield',
                                 4: 'spawn_white',
                                 5: 'spawn_green',
                                 6: 'spawn_red',
                                 7: 'spawn_yellow',
                                 8: 'xp',
                                 9: ''
                                 }.get(self.item_name_int)
                    if self.item_name is None:
                        self.item_name = f'grave_player({self.item_name_int-10})'
                    return

                self.item_name: str = None
                self.action_type: str = None  # 'drop' or 'use' or 'skill
                self.item_id: int = None

            def _get_attr(self) -> dict:
                return {'item_name_int': (int, 'u_1'), 'action_type': (int, 'u_1'), 'item_id': (int, 'u_3')}


class Login:
    class Output:
        class PlayerData(Serializable):
            def __init__(self, **kwargs):
                super().__init__(ser=b'')
                self.entity_id = kwargs.pop('entity_id')  # 2 bytes unsigned integer

                self.pos = kwargs.pop('pos')

                self.health = kwargs.pop('health')  # 1 byte unsigned integer
                self.strength = kwargs.pop('strength')  # 1 byte unsigned integer
                self.resistance = kwargs.pop('resistance')  # 1 byte unsigned integer
                self.xp = kwargs.pop('xp')  # 2 bytes unsigned integer

                self.inventory = kwargs.pop('inventory')  # a dictionary: {'heal': 3, 'shield': 0, 'spawn_red': 21,...}
                # max item count: 255

            def _get_attr(self) -> dict:
                return {'entity_id': (int, 'u_2'),
                        'pos': (tuple, 'u_2'),
                        'health': (int, 'u_1'),
                        'strength': (int, 'u_1'),
                        'resistance': (int, 'u_1'),
                        'xp': (int, 'u_2'),
                        'inventory': (dict, (tuple, (str, 'str'), (int, 'u_1')))}
