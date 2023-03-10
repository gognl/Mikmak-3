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
                self.player_changes: Tuple[NormalServer.Input.PlayerUpdate] = None
                self.enemy_changes: Tuple[NormalServer.Input.EnemyUpdate] = None
                self.item_changes: Tuple[NormalServer.Input.ItemUpdate] = None

            def _get_attr(self) -> dict:
                return {'player_changes': (tuple, (NormalServer.Input.PlayerUpdate, 'o')),
                        'enemy_changes': (tuple, (NormalServer.Input.EnemyUpdate, 'o')),
                        'item_changes': (tuple, (NormalServer.Input.ItemUpdate, 'o'))}

        class PlayerUpdate(Serializable):
            """
            A class of messages from the server - input
            """

            def __init__(self, **kwargs):
                self.id: int = None
                self.pos: Tuple[int, int] = None
                self.attacks: Tuple[NormalServer.Input.AttackUpdate] = None
                self.status: str = None
                self.health: int = None

                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')),
                        'attacks': (tuple, (NormalServer.Output.AttackUpdate, 'o')),
                        'status': (str, 'str'), 'health': (int, 'u_1')}

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
                self.status: str = None
                self.attacks: Tuple[NormalServer.Input.EnemyAttackUpdate] = None
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'type': (str, 'str'),
                        'direction': (tuple, (float, 'f_8')), 'status': (str, 'str'),
                        'attacks': (tuple, (NormalServer.Input.EnemyAttackUpdate, 'o'))}

        class EnemyAttackUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.direction = None  # if it's (0, 0) then it's an exploding red cow

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
                        'actions': (tuple, (NormalServer.Input.ItemActionUpdate, 'o'))}

        class ItemActionUpdate(Serializable):

            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.player_id = kwargs.pop('player_id')  # id of player
                self.action_type = kwargs.pop(
                    'action_type')  # 'spawn' or 'despawn' or 'pickup' or 'drop' or 'move' or 'use'
                self.pos = kwargs.pop('pos')  # tuple of item position

            def _get_attr(self) -> dict:
                return {'player_id': (int, 'u_2'), 'action_type': (str, 'str'), 'pos': (tuple, (int, 'u_8'))}

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
                self.attacks = changes['attacks']
                self.status = changes['status']
                self.item_actions = changes['item_actions']

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'),
                        'pos': (tuple, (int, 'u_8')),
                        'attacks': (tuple, (NormalServer.Input.AttackUpdate, 'o')),
                        'status': (str, 'str'),
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

            def _get_attr(self) -> dict:
                return {'weapon_id': (int, 'u_1'), 'attack_type': (int, 'u_1'), 'direction': (tuple, (float, 'f_8'))}

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
    def __init__(self, player_update: NormalServer.Output.PlayerUpdate, enemies_update: List[EnemyUpdate]):
        self.player_update: NormalServer.Output.PlayerUpdate = player_update
        self.enemies_update: List[EnemyUpdate] = enemies_update
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

class LoginResponseToClient(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser)
        if ser != b'':
            return

        self.encrypted_client_id: bytes = kwargs['encrypted_id']
        self.server: ServerSer = kwargs['server']

class HelloMsg(Serializable):
    def __init__(self, encrypted_client_id: bytes, src_server_index: int):
        super().__init__(ser=b'')
        self.encrypted_client_id: bytes = encrypted_client_id
        self.src_server_index: int = src_server_index  # -1 for login

class HelloMsg2(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser=ser)
        if ser != b'':
            return

        self.encrypted_client_id: bytes = kwargs['encrypted_id']
        self.src_server_index: int = kwargs['src_server_index']


