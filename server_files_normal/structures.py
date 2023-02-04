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

            def __init__(self, new_changes: Tuple['Client.Output.EntityUpdate']):
                super().__init__(ser=b'')
                self.changes: Tuple[Client.Output.EntityUpdate] = new_changes

            def _get_attr(self) -> dict:
                return {'changes': (tuple, (Client.Output.EntityUpdate, 'o'))}

        class EntityUpdate(Serializable):
            """
            A class of messages from the client - inputs
            corresponds to ServerOutputMsg in the client

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
                self.player_changes: List[Client.Input.EntityUpdate] = changes[0]
                self.enemies_changes = changes[1]
                self.items_changes = changes[2]

            def _get_attr(self) -> dict:
                return {'seq': (int, 'u_4'), 'player_changes': (list, (Client.Input.EntityUpdate, 'o'))}

        class EntityUpdate(Serializable):
            """
            A class of messages from the client - inputs
            corresponds to ServerOutputMsg in the client

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
