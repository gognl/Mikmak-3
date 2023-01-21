from server_files_normal.serializable import Serializable

class ClientInputMsg(Serializable):
    """ A class of messages from the client - inputs"""
    def __init__(self, **kwargs):
        super().__init__(ser=kwargs.pop('ser', b''))

class StateUpdateMsg(Serializable):
    """ A class that describes the message to the client, which contains the current state of relevant game changes"""
    #For future references, this class will describe the changes in the game state
    def __init__(self, **kwargs):
        super().__init__(ser=kwargs.pop('ser', b''))


class ServerSwitchMsg(Serializable):
    """A class of a message to the client which included data about switching to a different server (and region)"""
    def __init__(self, **kwargs):
        super().__init__(ser=kwargs.pop('ser', b''))
