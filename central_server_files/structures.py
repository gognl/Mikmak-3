from central_server_files.serializable import Serializable

ID = int

class Point:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def add(self, other):
        assert isinstance(other, Point)
        self.x += other.x
        self.y += other.y

    def div(self, num):
        assert isinstance(num, int) and num != 0
        self.x //= num
        self.y //= num

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def dist2(self, other):
        assert isinstance(other, Point)
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

class PlayerCentral(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser)
        if ser != b'':
            return

        self.pos: Point = kwargs['pos']
        self.id: ID = kwargs['player_id']

class PlayerCentralList(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser)
        if ser != b'':
            return

        self.players: list[PlayerCentral] = kwargs['players']

class Server:
    def __init__(self, ip, port):
        self.ip: str = ip
        self.port: int = port

    def addr(self):
        return self.ip, self.port

    def __eq__(self, other):
        assert isinstance(other, Server)
        return self.ip == other.ip and self.port == other.port

class ServerSer(Serializable, Server):
    def __init__(self, **kwargs):
        ser = kwargs.get("ser", b'')
        Serializable.__init__(self, ser)
        if ser != b'':
            return
        Server.__init__(self, kwargs['ip'], kwargs['port'])

class LB_to_login_msg:
    def __init__(self, client_id: ID, server: Server):
        self.client_id: ID = client_id
        self.server: Server = server

class LoginResponseToClient(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser)
        if ser != b'':
            return

        self.encrypted_client_id: bytes = kwargs['encrypted_id']
        self.server: ServerSer = kwargs['server']

class InfoData(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser)
        if ser != b'':
            return

        self.info: tuple = kwargs['info']

class InfoMsgToNormal(Serializable):
    def __init__(self, **kwargs):
        ser = kwargs.get('ser', b'')
        super().__init__(ser)
        if ser != b'':
            return

        self.client_id: bytes = kwargs['client_id']
        self.info_list: bytes = kwargs['info']

class Rect:
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1: int = x1
        self.y1: int = y1
        self.x2: int = x2
        self.y2: int = y2

    def __contains__(self, item):
        assert isinstance(item, Point)
        return self.x1 <= item.x <= self.x2 and self.y1 <= item.y <= self.y2

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

    # max item count: 255

    def _get_attr(self) -> dict:
        return {'entity_id': (int, 'u_2'),
                'pos': (tuple, 'u_2'),
                'health': (int, 'u_1'),
                'strength': (int, 'u_1'),
                'resistance': (int, 'u_1'),
                'xp': (int, 'u_2'),
                'inventory': (dict, (tuple, (str, 'str'), (int, 'u_1')))}

    def get_pos(self):
        return self.pos[0], self.pos[1]
