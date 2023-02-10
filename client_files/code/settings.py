SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
FPS: int = 120
TILESIZE: int = 64
CAMERA_DISTANCE_FROM_PLAYER: tuple[int, int] = (300, 100)
ROW_TILES: int = 450
COL_TILES: int = 800
ROW_LOAD_TILE_DISTANCE: int = 20
COL_LOAD_TILE_DISTANCE: int = 30
ROW_UNLOAD_TILE_DISTANCE: int = 30
COL_UNLOAD_TILE_DISTANCE: int = 40
SPAWNABLE_TILES: list[int] = [9, 10, 11, 17, 18, 19, 21, 22, 23, 24]

weapon_data = {
	'sword': {'cooldown': 100, 'damage': 15, 'graphic': '../graphics/weapons/sword/full.png'},
	'nerf': {'cooldown': 100, 'damage': 35, 'graphic': '../graphics/weapons/nerf/full.png'},
	'kettle': {'cooldown': 100, 'damage': 25, 'graphic': '../graphics/weapons/kettle/full.png'}
}

# UI
UI_FONT = '../graphics/font/joystix.ttf'
UI_FONT_SIZE = 18
NAMETAG_FONT_SIZE = 12
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
INVENTORY_WIDTH = 300
NAMETAG_HEIGHT = 32

# general colors
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# UI colors
HEALTH_COLOR = 'red'
ENERGY_COLOR = 'blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

# Openning screen
TITLE_BG_COLOR = '#71ddee'
TITLE_FONT = UI_FONT  # TODO - change
TITLE_FONT_SIZE = 24
TITLE_TEXT_COLOR = '#EEEEEE'
BOX_BG_COLOR = '#444444'
INPUT_BG_COLOR = '#cc99ff'
BUTTON_BG_COLOR = '#66ff66'
BUTTON_TEXT_COLOR = '#222222'

# TODO: make the red cow explode
enemy_data = {
	'other_player': {'health': 100, 'exp': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300},
	'red_cow': {'health': 100, 'exp': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300},
	'green_cow': {'health': 100, 'exp': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300},
	'white_cow': {'health': 100, 'exp': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300}
}


