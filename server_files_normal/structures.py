from server_files_normal.serializable import Serializable

class ClientInputMsg(Serializable):
    """ A class of messages from the client - inputs"""
    def __init__(self, **kwargs):
        super().__init__(ser=kwargs.pop('ser', b''))

class GameState(Serializable):
    """ A class that describes the current state of each entity in the game"""
    #For future references, this class will describe the changes in the game state
    def __init__(self, **kwargs):
        super().__init__(ser=kwargs.pop('ser', b''))
