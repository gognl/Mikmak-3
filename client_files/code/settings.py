from typing import List

SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
FPS: int = 120
TILESIZE: int = 64
CAMERA_DISTANCE_FROM_PLAYER: (int, int) = (300, 100)
ROW_TILES: int = 450
COL_TILES: int = 800
ROW_LOAD_TILE_DISTANCE: int = 20
COL_LOAD_TILE_DISTANCE: int = 30
ROW_UNLOAD_TILE_DISTANCE: int = 30
COL_UNLOAD_TILE_DISTANCE: int = 40
SPAWNABLE_TILES: List[int] = [9, 10, 11, 17, 18, 19, 21, 22, 23, 24, 33, 36, 66, 67, 68, 69, 70]
MAX_DIVERGENCE_SQUARED: int = 80 ** 2
MAX_PETS_PER_PLAYER: int = 5
ENEMY_ATTACK_COOLDOWN: int = 100

weapon_data = {
    'sword': {'damage': 100, 'graphic': '../graphics/weapons/sword/full.png'},
    'nerf': {'damage': 20, 'graphic': '../graphics/weapons/nerf/full.png'},
    'kettle': {'damage': 40, 'graphic': '../graphics/weapons/kettle/full.png'}
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
CHAT_WIDTH, CHAT_HEIGHT = (300, 500)
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

# Opening screen
TITLE_BG_COLOR = '#71ddee'
TITLE_FONT = UI_FONT
TITLE_FONT_SIZE = 24
TITLE_TEXT_COLOR = '#EEEEEE'
BOX_BG_COLOR = '#444444'
INPUT_BG_COLOR = '#cc99ff'
BUTTON_BG_COLOR = '#66ff66'
BUTTON_TEXT_COLOR = '#222222'
TITLE_MOUSE_RADIUS = 100
TITLE_RANDOM_COW = ['green_cow', 'red_cow', 'pet_cow']

# Inventory
INVENTORY_SIZE = (3, 5)
INVENTORY_ITEMS = INVENTORY_SIZE[0] * INVENTORY_SIZE[1]
INVENTORY_FONT_SIZE = 10
ITEM_PICK_UP_COOLDOWN = 60
ITEM_DESPAWN_TIME = 36000

# Chat
CHAT_TEXT_LENGTH = 36
CHAT_TEXT_TOTAL_LENGTH = 3 * CHAT_TEXT_LENGTH

# Explosion
EXPLOSION_SPEED = 1.3
EXPLOSION_RADIUS = 150

enemy_data = {
    'other_player': {'health': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 0, 'notice_radius': 400,
                     'stop_radius': 100, 'move_cooldown': 0, 'death_items': ['grave_player'], 'xp': 0},
    'red_cow': {'health': 100, 'damage': 1, 'speed': 10, 'resistance': 0, 'attack_radius': 100, 'notice_radius': 500,
                'move_cooldown': 0, 'death_items': ['heal', 'strength', 'kettle', 'shield', 'spawn_red', 'spawn_pet'], 'xp': 40},
    'green_cow': {'health': 100, 'damage': 1, 'speed': 10, 'resistance': 50, 'attack_radius': 55, 'notice_radius': 400,
                  'move_cooldown': 0, 'death_items': ['heal', 'strength', 'kettle', 'shield', 'spawn_green', 'spawn_pet'], 'xp': 20},
    'white_cow': {'health': 100, 'damage': 1, 'speed': 10, 'resistance': 10, 'attack_radius': 55, 'notice_radius': 400,
                  'move_cooldown': 0, 'death_items': ['heal', 'strength', 'kettle', 'shield', 'spawn_white', 'spawn_pet'], 'xp': 15},
    'yellow_cow': {'health': 100, 'damage': 1, 'speed': 10, 'resistance': 20, 'attack_radius': 350, 'notice_radius': 600,
                   'move_cooldown': 24, 'death_items': ['heal', 'strength', 'kettle', 'shield', 'spawn_yellow', 'spawn_pet'], 'xp': 30},
    'pet_cow': {'health': 100, 'damage': 0, 'speed': 10, 'resistance': 50, 'attack_radius': 0, 'notice_radius': 400,
                'stop_radius': 100, 'move_cooldown': 0, 'death_items': ['grave_pet'], 'xp': 5}
}

item_names = ['heal', 'strength', 'kettle', 'shield', 'spawn_white', 'spawn_green',
              'spawn_red', 'spawn_yellow', 'spawn_pet', 'xp']  # TODO - keep only items that need to be naturally spawned

RANDOM_NAMETAG = ['goni', 'omri', 'bar', 'alon', 'liron', 'gabriel', 'god', 'dog', 'not a cow', 'friend',
                  'epstein', 'shmulik', 'holy cow', 'cat', 'milk factory', '123456', 'password', 'user',
                  'not a bot', 'pet', 'SOS', 'obama', 'allah', 'not a cow', 'meow', 'woof', 'moo', 'BLOOD', 'VIOLENCE',
                  'DEATH', 'MASSACRE', 'GENOCIDE', 'what', 'server', 'alt+f4', 'die', 'mom', 'dad',
                  'joe', 'this game was encrypted using-']  # TODO - add more

INTERPOLATION_PERIOD = 100_000_000  # ns
INTERPOLATION_ACTIVE = False
