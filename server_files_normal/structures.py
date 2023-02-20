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

            def __init__(self, player_changes: Tuple['Client.Output.PlayerUpdate'], enemy_changes: Tuple['Client.Output.EnemyUpdate']):
                super().__init__(ser=b'')
                self.player_changes: Tuple[Client.Output.PlayerUpdate] = player_changes
                self.enemy_changes: Tuple[Client.Output.EnemyUpdate] = enemy_changes

            def _get_attr(self) -> dict:
                return {'player_changes': (tuple, (Client.Output.PlayerUpdate, 'o')),
                        'enemy_changes': (tuple, (Client.Output.EnemyUpdate, 'o'))}

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

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'attacks': (tuple, (Client.Output.AttackUpdate, 'o')), 'status': (str, 'str')}

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

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'type': (str, 'str'), 'direction': (tuple, (float, 'f_8'))}

        class ServerSwitch(Serializable):
            """A class of a message to the client which included data about switching to a different server (and region)"""

            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

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

                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'attacks': (tuple, (Client.Input.AttackUpdate, 'o')), 'status': (str, 'str')}

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
    def __init__(self, x: int, y : int):
        self.x: int = x
        self.y: int = y
