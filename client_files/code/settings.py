SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
FPS: int = 120
TILESIZE: int = 64
CAMERA_DISTANCE_FROM_PLAYER: tuple[int] = (150, 50)
# Weapons
weapon_data = {
	'sword': {'cooldown': 100, 'damage': 15, 'graphic': '../graphics/weapons/sword/full.png'},
	'kettle': {'cooldown': 100, 'damage': 25, 'graphic': '../graphics/weapons/kettle/full.png'},
	'nerf': {'cooldown': 100, 'damage': 35, 'graphic': '../graphics/weapons/nerf/full.png'}
}
