from typing import Tuple

from server_files_normal.serializable import Serializable

class ClientUpdateMsg(Serializable):
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

        self.pos: (int, int) = kwargs.pop('pos')

    def _get_attr(self) -> dict:
        return {'pos': (tuple, (int, 'u_8'))}


class StateUpdateMsg(Serializable):
    """ A class that describes the message to the client, which contains the current state of relevant game changes"""
    #For future references, this class will describe the changes in the game state
    def __init__(self, new_changes: Tuple[Tuple[int, ClientUpdateMsg]]):
        super().__init__(ser=b'')
        self.changes: Tuple[(int, ClientUpdateMsg)] = new_changes  # id & update

    def _get_attr(self) -> dict:
        return {'changes': (tuple, (tuple, (int, 'u_2'), (ClientUpdateMsg, 'o')))}

class ServerSwitchMsg(Serializable):
    """A class of a message to the client which included data about switching to a different server (and region)"""
    def __init__(self, **kwargs):
        s: bytes = kwargs.pop('ser', b'')
        super().__init__(ser=s)
        if s != b'':
            return
