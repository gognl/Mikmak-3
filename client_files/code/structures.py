from typing import Tuple, List

from client_files.code.serializable import Serializable

class Server:
    def __init__(self, ip, port):
        self.ip: str = ip
        self.port: int = port

    def addr(self):
        return self.ip, self.port

    def __eq__(self, other):
        assert isinstance(other, Server)
        return self.ip == other.ip and self.port == other.port

    def __add__(self, other):
        assert isinstance(other, int)
        return Server(self.ip, self.port + other)

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

class NormalServer:
    class Input:
        class ChangeServerMsg(Serializable):
            def __init__(self, **kwargs):
                ser = kwargs.get('ser', b'')
                super().__init__(ser=ser)
                if ser != b'':
                    return

                self.server: ServerSer = kwargs['encrypted_id']
                self.encrypted_client_id: bytes = kwargs['encrypted_id']
                self.src_server_index: int = kwargs['src_server_index']

            def _get_attr(self) -> dict:
                return {'server': (ServerSer, 'o'), 'encrypted_client_id': (bytes, 'by'), 'src_server_index': (int, 'u_1')}

        class StateUpdate(Serializable):
            """Like StateUpdate but with an acknowledgement number"""

            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return
                self.ack: int = None
                self.state_update: NormalServer.Input.StateUpdateNoAck = None

            def _get_attr(self) -> dict:
                return {'ack': (int, 'u_4'), 'state_update': (NormalServer.Input.StateUpdateNoAck, 'o')}

        class StateUpdateNoAck(Serializable):
            """A class of an incoming message from the server"""

            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return
                self.player_changes: Tuple[NormalServer.Input.PlayerUpdate] = kwargs.pop('player_changes', ())
                self.enemy_changes: Tuple[NormalServer.Input.EnemyUpdate] = kwargs.pop('enemy_changes', ())
                self.item_changes: Tuple[NormalServer.Input.ItemUpdate] = kwargs.pop('item_changes', ())

            def _get_attr(self) -> dict:
                return {'player_changes': (tuple, (NormalServer.Input.PlayerUpdate, 'o')),
                        'enemy_changes': (tuple, (NormalServer.Input.EnemyUpdate, 'o')),
                        'item_changes': (tuple, (NormalServer.Input.ItemUpdate, 'o'))}

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
                self.attacks: Tuple[NormalServer.Input.AttackUpdate] = data.pop('attacks')
                self.status: str = data.pop('status')
                self.health: int = data.pop('health')

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_6'), '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2'), 'attacks': (tuple, (NormalServer.Input.AttackUpdate, 'o')),
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
                self.attacks: Tuple[NormalServer.Input.EnemyAttackUpdate] = data.pop('attacks')

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_6'), '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2'), 'type': (int, 'u_1'), 'attacks': (tuple, (NormalServer.Input.EnemyAttackUpdate, 'o')), '_is_dead': (bool, 'b')}

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
                                 8: 'xp',
                                 }.get(self.name_int)
                    if self.name is None:
                        self.name = f'grave_player({self.name_int - 10})'
                    return

                self.id = kwargs.pop('id')
                self.name = kwargs.pop('name')
                self.actions = kwargs.pop('actions')

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_3'), 'name_int': (int, 'u_1'),
                        'actions': (tuple, (NormalServer.Input.ItemActionUpdate, 'o'))}

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
                return {'player_id': (int, 'u_6'), 'action_type': (int, 'u_1'), '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2')}

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

                self.seq = NormalServer.Output.StateUpdate.seq_count
                self.player_changes = kwargs.pop('player_changes')

            def _get_attr(self) -> dict:
                return {'seq': (int, 'u_4'), 'player_changes': (NormalServer.Output.PlayerUpdate, 'o')}

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
                self._pos_x = self.pos[0]
                self._pos_y = self.pos[1]
                self.attacks = changes['attacks']
                self.status = changes['status']
                self._status_int: int = {'up': 0,
                                         'down': 1,
                                         'left': 2,
                                         'right': 3,
                                         'up_idle': 4,
                                         'down_idle': 5,
                                         'left_idle': 6,
                                         'right_idle': 7,
                                         'dead': 8
                                         }.get(self.status)
                self.item_actions = changes['item_actions']

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_6'),
                        '_pos_x': (int, 'u_2'), '_pos_y': (int, 'u_2'),
                        'attacks': (tuple, (NormalServer.Input.AttackUpdate, 'o')),
                        '_status_int': (int, 'u_1'),
                        'item_actions': (tuple, (NormalServer.Output.ItemActionUpdate, 'o'))}

        class AttackUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.weapon_id = kwargs.pop('weapon_id')  # 0 = sword, 1 = rifle, 2 = kettle
                self.attack_type = kwargs.pop('attack_type')  # switch=0, attack=1
                self.direction = kwargs.pop('direction')
                self._direction_x = self.direction[0]
                self._direction_y = self.direction[1]

            def _get_attr(self) -> dict:
                return {'weapon_id': (int, 'u_1'), 'attack_type': (int, 'u_1'), '_direction_x': (int, 's_2'), '_direction_y': (int, 's_2')}

        class ItemActionUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                item_name = kwargs.pop('item_name')
                self.item_name = {'heal': 0,
                                  'strength': 1,
                                  'kettle': 2,
                                  'shield': 3,
                                  'spawn_white': 4,
                                  'spawn_green': 5,
                                  'spawn_red': 6,
                                  'spawn_yellow': 7,
                                  'xp': 8,
                                  }.get(item_name, 9)
                if 'grave_player' in item_name:
                    self.item_name = 10 + int(item_name[13:-1])
                action_type = kwargs.pop('action_type')  # 'drop' or 'use' or 'skill'
                self.action_type = {'drop': 0, 'use': 1, 'skill': 2}.get(action_type)  # 'drop' or 'use' or 'skill'
                self.item_id = kwargs.pop('item_id')  # if skill, then 1=speed, 2=magnet, 3=damage

            def _get_attr(self) -> dict:
                return {'item_name': (int, 'u_1'), 'action_type': (int, 'u_1'), 'item_id': (int, 'u_3')}

class EnemyUpdate:
    def __init__(self, entity_id: int, pos: (int, int)):
        self.entity_id = entity_id
        self.pos = pos

class TickUpdate:
    def __init__(self, player_update: NormalServer.Output.PlayerUpdate):
        self.player_update: NormalServer.Output.PlayerUpdate = player_update
        self.seq: int = NormalServer.Output.StateUpdate.seq_count

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

class DataToClient(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser=ser)
        if ser != b'':
            return

        self.pos_x = kwargs.pop('pos_x')
        self.pos_y = kwargs.pop('pos_y')

        self.health = kwargs.pop('health')  # 1 byte unsigned integer
        self.strength = kwargs.pop('strength')  # 1 byte unsigned integer
        self.resistance = kwargs.pop('resistance')  # 1 byte unsigned integer
        self.xp = kwargs.pop('xp')  # 2 bytes unsigned integer

        self.inventory = kwargs.pop('inventory')  # {item_name: (item_ids, item_count)}

    def _get_attr(self) -> dict:
        return {'pos_x': (int, 'u_2'),
                'pos_y': (int, 'u_2'),
                'health': (int, 'u_1'),
                'strength': (int, 'u_1'),
                'resistance': (int, 'u_1'),
                'xp': (int, 'u_2'),
                'inventory': (dict, (tuple, (str, 'str'), (tuple, (list, (int, 'u_4')), (int, 'u_1'))))}

class LoginResponseToClient(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser=ser)
        if ser != b'':
            return

        self.encrypted_client_id: bytes = kwargs['encrypted_id']
        self.server: ServerSer = kwargs['server']
        self.data_to_client = kwargs['data_to_client']

    def _get_attr(self) -> dict:
        return {'encrypted_client_id': (bytes, 'by'),
                'server': (ServerSer, 'o'), 'data_to_client': (DataToClient, 'o')}

class HelloMsg(Serializable):
    def __init__(self, encrypted_client_id: bytes, src_server_index: int):
        super().__init__(ser=b'')
        self.encrypted_client_id: bytes = encrypted_client_id
        self.src_server_index: int = src_server_index  # -1 for login

    def _get_attr(self) -> dict:
        return {'encrypted_client_id': (bytes, 'by'), 'src_server_index': (int, 's_1')}

class ChatMsgsLst(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser=ser)
        if ser != b'':
            return
        self.msg_lst: list[tuple[str]] = kwargs.get('msg_lst')

    def _get_attr(self) -> dict:
        return {'msg_lst': (list, (tuple, (str, 'str')))}