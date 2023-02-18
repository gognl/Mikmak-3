FPS: int = 5
CLIENT_FPS: int = 120
TILESIZE = 64
ROW_TILES: int = 450
COL_TILES: int = 800

weapon_data = {
	'sword': {'cooldown': 100, 'damage': 15, 'graphic': '../graphics/weapons/sword/full.png'},
	'nerf': {'cooldown': 100, 'damage': 35, 'graphic': '../graphics/weapons/nerf/full.png'},
	'kettle': {'cooldown': 100, 'damage': 25, 'graphic': '../graphics/weapons/kettle/full.png'}
}

enemy_data = {
	'other_player': {'health': 100, 'xp': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300},
	'red_cow': {'health': 100, 'xp': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300},
	'green_cow': {'health': 100, 'xp': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300},
	'white_cow': {'health': 100, 'xp': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300}
}
