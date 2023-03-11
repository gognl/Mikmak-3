from typing import Tuple, List

from server_files_normal.serializable import Serializable
from server_files_normal.game.settings import Server


class ServerSer(Serializable, Server):
    def __init__(self, **kwargs):
        ser = kwargs.get("ser", b'')
        Serializable.__init__(self, ser)
        if ser != b'':
            return
        Server.__init__(self, kwargs['ip'], kwargs['port'])

    def _get_attr(self) -> dict:
        return {'ip': (str, 'str'),
                'port': (int, 'u_2')}


class Client:
    class Output:
        class ChangeServerMsg(Serializable):
            def __init__(self, server: ServerSer, encrypted_client_id: bytes, src_server_index: int):
                super().__init__(ser=b'')

                self.server: ServerSer = server
                self.encrypted_client_id: bytes = encrypted_client_id
                self.src_server_index: int = src_server_index

            def _get_attr(self) -> dict:
                return {'server': (ServerSer, 'o'), 'encrypted_client_id': (bytes, 'by'),
                        'src_server_index': (int, 's_1')}

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
                self.pos = pos
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
                self.pos = pos
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
                self.pos = pos

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


class NormalServer:
    class EnemyDetails(Serializable):
        def __init__(self, **kwargs):
            s: bytes = kwargs.pop('ser', b'')
            super().__init__(ser=s)
            if s != b'':
                return

            self.entity_id = kwargs.get('entity_id')
            self.pos = kwargs.get('pos')
            self.enemy_name = kwargs.get('enemy_name')

            self.health = kwargs.get('health')
            self.xp = kwargs.get('xp')
            self.speed = kwargs.get('speed')
            self.damage = kwargs.get('damage')
            self.resistance = kwargs.get('resistance')
            self.attack_radius = kwargs.get('attack_radius')
            self.notice_radius = kwargs.get('notice_radius')
            self.death_items = kwargs.get('death_items')
            self.move_cooldown = kwargs.get('move_cooldown')



        def _get_attr(self) -> dict:
            return {'entity_id': (int, 'u_6'), 'pos': (tuple, (int, 'u_2')), 'enemy_name': (str, 'str'), 'health': (int, 'u_1'), 'xp': (int, 'u_1'),
                    'speed': (int, 'u_1'), 'damage': (int, 'u_1'), 'resistance': (int, 'u_1'),  'attack_radius': (int, 'u_2'), 'notice_radius': (int, 'u_2'),
                    'death_items': (list, (str, 'str')), 'move_cooldown': (int, 'u_1')
                    }


    class ItemDetails(Serializable):
        def __init__(self, **kwargs):
            s: bytes = kwargs.pop('ser', b'')
            super().__init__(ser=s)
            if s != b'':
                return

            self.id = kwargs.pop('id')
            self.name = kwargs.pop('name')
            self.pos = kwargs.pop('actions')

        def _get_attr(self) -> dict:
            return {'id': (int, 'u_3'), 'name': (str, 'str'),
                    'pos': (tuple, (int, 'u_6'))}

    class ItemDetailsList(Serializable):
        def __init__(self, **kwargs):
            ser = kwargs.get('ser', b'')
            super().__init__(ser=ser)
            if ser != b'':
                return

            self.item_details_list: list[NormalServer.ItemDetails] = kwargs['item_details_list']

        def _get_attr(self) -> dict:
            return {'item_details_list': (list, (NormalServer.ItemDetails, 'o'))}

    class PlayerUpdate(Serializable):
        def __init__(self, **kwargs):
            s: bytes = kwargs.pop('ser', b'')
            super().__init__(ser=s)
            if s != b'':
                return
            self.id: int = kwargs['player_id']
            self.pos: Tuple[int, int] = kwargs['pos']
            self.attacks: Tuple[Client.Input.AttackUpdate] = kwargs['attacks']
            self.status: str = kwargs['status']
            self.item_actions: Tuple[Client.Input.ItemActionUpdate] = kwargs['item_actions']

        def _get_attr(self) -> dict:
            return {'id': (int, 'u_6'),
                    'pos': (tuple, (int, 'u_8')),
                    'attacks': (tuple, (Client.Input.AttackUpdate, 'o')),
                    'status': (str, 'str'),
                    'item_actions': (tuple, (Client.Input.ItemActionUpdate, 'o'))}

    class StateUpdateNoAck(Serializable):
        def __init__(self, **kwargs):
            s: bytes = kwargs.pop('ser', b'')
            super().__init__(ser=s)
            if s != b'':
                return

            self.player_changes: Tuple[Client.Output.PlayerUpdate] = kwargs.pop('player_changes')
            self.enemy_changes: Tuple[Client.Output.EnemyUpdate] = kwargs.pop('enemy_changes')
            self.item_changes: Tuple[Client.Output.ItemUpdate] = kwargs.pop('item_changes')

        def _get_attr(self) -> dict:
            return {'player_changes': (tuple, (Client.Output.PlayerUpdate, 'o')),
                    'enemy_changes': (tuple, (Client.Output.EnemyUpdate, 'o')),
                    'item_changes': (tuple, (Client.Output.ItemUpdate, 'o'))}


class Rect:
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1: int = x1
        self.y1: int = y1
        self.x2: int = x2
        self.y2: int = y2

    def __contains__(self, item):
        assert isinstance(item, tuple) and isinstance(item[0], int), isinstance(item[1], int)
        return self.x1 <= item[0] <= self.x2 and self.y1 <= item[1] <= self.y2


class Point:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y


class PointSer(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser=ser)
        self.x = kwargs['x']
        self.y = kwargs['y']

    def _get_attr(self) -> dict:
        return {'x': (int, 'u_2'),
                'y': (int, 'u_2')}

class PlayerCentral(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser)
        if ser != b'':
            return

        self.pos: PointSer = kwargs['pos']
        self.id: int = kwargs['player_id']

    def _get_attr(self) -> dict:
        return {'pos': (PointSer, 'o'),
                'id': (int, 'u_6')}


class PlayerCentralList(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser)
        if ser != b'':
            return

        self.players: list[PlayerCentral] = kwargs['players']

    def _get_attr(self) -> dict:
        return {'players': (list, (PlayerCentral, 'o'))}

class HelloMsg(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser=ser)
        if ser != b'':
            return

        self.encrypted_client_id: bytes = kwargs['encrypted_id']
        self.src_server_index: int = kwargs['src_server_index']

    def _get_attr(self) -> dict:
        return {'encrypted_client_id': (bytes, 'by'), 'src_server_index': (int, 's_1')}


class InfoData(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser)
        if ser != b'':
            return

        self.info: list = kwargs['info']

    def _get_attr(self) -> dict:
        return {'info': (list, (int, 'u_2'), (int, 'u_2'), (int, 'u_1'), (int, 'u_2'), (int, 'u_2'), (int, 'u_2'),
                         (dict, (tuple, (str, 'str'), (int, 'u_2'))))}

class InfoMsgToNormal(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser)
        if ser != b'':
            return

        self.client_id: int = kwargs['client_id']
        self.info: InfoData = kwargs['info_list']

    def _get_attr(self) -> dict:
        return {'client_id': (int, 'u_6'), 'info': (InfoData, 'o')}


class PlayerData(Serializable):
    def __init__(self, **kwargs):
        s: bytes = kwargs.pop('ser', b'')
        super().__init__(ser=s)
        if s != b'':
            return
        self.entity_id = kwargs.pop('entity_id')  # 2 bytes unsigned integer

        self.pos = kwargs.pop('pos')

        self.health = kwargs.pop('health')  # 1 byte unsigned integer
        self.strength = kwargs.pop('strength')  # 1 byte unsigned integer
        self.resistance = kwargs.pop('resistance')  # 1 byte unsigned integer
        self.xp = kwargs.pop('xp')  # 2 bytes unsigned integer

        self.inventory = kwargs.pop('inventory')  # a dictionary: {'heal': 3, 'shield': 0, 'spawn_red': 21,...}

    def _get_attr(self) -> dict:
        return {'entity_id': (int, 'u_6'),
                'pos': (tuple, 'u_2'),
                'health': (int, 'u_1'),
                'strength': (int, 'u_1'),
                'resistance': (int, 'u_1'),
                'xp': (int, 'u_2'),
                'inventory': (dict, (tuple, (str, 'str'), (int, 'u_1')))}
