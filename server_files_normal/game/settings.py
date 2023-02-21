FPS: int = 60
CLIENT_FPS: int = 120
UPDATE_FREQUENCY: int = 10
TILESIZE = 64
ROW_TILES: int = 450
COL_TILES: int = 800
MAP_WIDTH = TILESIZE * COL_TILES
MAP_HEIGHT = TILESIZE * ROW_TILES
OVERLAPPING_AREA_T = 100000000000

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
        return Server(self.ip, self.port+other)

# TODO: get this list in the starting of the server
NORMAL_SERVERS = [Server('192.168.172.117', 14760), Server('192.168.174.189', 14760), Server('127.0.0.1', 14769), Server('127.0.0.1', 14769)]

weapon_data = {
	'sword': {'cooldown': 100, 'damage': 15, 'graphic': '../graphics/weapons/sword/full.png'},
	'nerf': {'cooldown': 100, 'damage': 35, 'graphic': '../graphics/weapons/nerf/full.png'},
	'kettle': {'cooldown': 100, 'damage': 25, 'graphic': '../graphics/weapons/kettle/full.png'}
}

enemy_data = {
	'other_player': {'health': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300, 'death_items': ['grave_player'], 'xp': 0},
	'red_cow': {'health': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300, 'death_items': ['heal', 'strength', 'kettle', 'shield', 'spawn_red', 'spawn_pet'], 'xp': 20},
	'green_cow': {'health': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300, 'death_items': ['heal', 'strength', 'kettle', 'shield', 'spawn_green', 'spawn_pet'], 'xp': 10},
	'white_cow': {'health': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300, 'death_items': ['heal', 'strength', 'kettle', 'shield', 'spawn_white', 'spawn_pet'], 'xp': 15},
	'pet_cow': {'health': 100, 'damage': 0, 'speed': 10, 'resistance': 0, 'attack_radius': 0, 'notice_radius': 300, 'death_items': ['grave_pet'], 'xp': 5}
}
