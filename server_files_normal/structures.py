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
                self.attacking = changes['attacking']
                self.weapon = changes['weapon']
                self.status = changes['status']

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8')), 'attacking': (bool, 'b'),
                        'weapon': (str, 'str'),
                        'status': (str, 'str')}

        class EnemyUpdate(Serializable):
            def __init__(self, **kwargs):
                s: bytes = kwargs.pop('ser', b'')
                super().__init__(ser=s)
                if s != b'':
                    return

                self.id = kwargs.pop('id')
                changes = kwargs.pop('changes')
                self.pos = changes['pos']

            def _get_attr(self) -> dict:
                return {'id': (int, 'u_2'), 'pos': (tuple, (int, 'u_8'))}

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
                changes = kwargs.pop('changes')
                self.player_changes: List[Client.Input.PlayerUpdate] = changes[0]

            def _get_attr(self) -> dict:
                return {'seq': (int, 'u_4'), 'player_changes': (list, (Client.Input.PlayerUpdate, 'o'))}

        class PlayerUpdate(Serializable):
            """
            A class of messages from the client - inputs
            corresponds to PlayerUpdate in the client

            Also used as a format for updating clients about other clients' updates
            """

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
                        'weapon': (str, 'str'),
                        'status': (str, 'str')}
