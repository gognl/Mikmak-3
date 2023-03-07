FPS: int = 60
CLIENT_FPS: int = 120
UPDATE_FREQUENCY: int = 10
OVERLAPPED_UPDATE_FREQUENCY: int = 15
SEND_TO_LB_FREQUENCY: int = 1
TILESIZE = 64
ROW_TILES: int = 450
COL_TILES: int = 800
MAP_WIDTH = TILESIZE * COL_TILES
MAP_HEIGHT = TILESIZE * ROW_TILES
OVERLAPPING_AREA_T = 100000000000
DH_p = 129580882928432529101537842147269734269461392429415268045151341409571915390240545252786047823626355003667141296663918972102908481139133511887035351545132033655663683090166304802438003459450977581889646160951156933194756978255460848171968985564238788467016810538221614304187340780075305032745815204247560364281
DH_g = 119475692254216920066132241696136552167987712858139173729861721592048057547464063002529177743099212305134089294733874076960807769722388944847002937915383340517574084979135586810183464775095834581566522721036079400681459953414957269562943460288437613755140572753576980521074966372619062067471488360595813421462

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

# TODO: get this list in the starting of the server
NORMAL_SERVERS = [Server('192.168.174.189', 14760), Server('192.168.172.117', 14760), Server('192.168.172.117', 14769), Server('192.168.172.117', 14769)]
LOGIN_SERVER = Server('192.168.171.117', 12304)
LB_SERVER = Server('192.168.171.117', 12328)

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
