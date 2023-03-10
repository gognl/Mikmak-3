from typing import Tuple, List

from server_files_normal.game.item import Item
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
                        'src_server_index': (int, 'u_1')}

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
                self.pos = changes['pos']
                self.attacks = changes['attacks']
                self.status = changes['status']
                self.health = changes['health']

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_6'), 'pos': (tuple, (int, 'u_8')),
                        'attacks': (tuple, (Client.Output.AttackUpdate, 'o')), 'status': (str, 'str'),
                        'health': (int, 'u_1')}

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

        class EnemyUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.id = kwargs.pop('id')
                self.type = kwargs.pop('type')
                changes = kwargs.pop('changes')
                self.pos = changes['pos']
                self.direction = changes['direction']
                self.status = changes['status']
                self.attacks = changes['attacks']

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_6'), 'pos': (tuple, (int, 'u_8')), 'type': (str, 'str'),
                        'direction': (tuple, (float, 'f_8')), 'status': (str, 'str'),
                        'attacks': (tuple, (Client.Output.EnemyAttackUpdate, 'o'))}

        class EnemyAttackUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.direction = kwargs.pop('direction')  # if it's (0, 0) then it's an exploding red cow

            def _get_attr(self) -> dict:
                return {'direction': (tuple, (float, 'f_8'))}

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
                        'actions': (tuple, (Client.Output.ItemActionUpdate, 'o'))}

        class ItemActionUpdate(Serializable):

            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.player_id = kwargs.pop('player_id', 0)  # id of player
                self.action_type = kwargs.pop('action_type',
                                              'spawn')  # 'spawn' or 'despawn' or 'pickup' or 'drop' or 'move' or 'use'
                self.pos = kwargs.pop('pos', (0, 0))  # tuple of item position

            def _get_attr(self) -> dict:
                return {'player_id': (int, 'u_6'), 'action_type': (str, 'str'), 'pos': (tuple, (int, 'u_8'))}

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
                    return

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_6'),
                        'pos': (tuple, (int, 'u_8')),
                        'attacks': (tuple, (Client.Input.AttackUpdate, 'o')),
                        'status': (str, 'str'),
                        'item_actions': (tuple, (Client.Input.ItemActionUpdate, 'o'))}

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

        class ItemActionUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.item_name: str = None
                self.action_type: str = None  # 'drop' or 'use'
                self.item_id: int = None

            def _get_attr(self) -> dict:
                return {'item_name': (str, 'str'), 'action_type': (str, 'str'), 'item_id': (int, 'u_3')}


class NormalServer:
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
