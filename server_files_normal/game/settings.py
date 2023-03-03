from typing import List

FPS: int = 60
CLIENT_FPS: int = 120
UPDATE_FREQUENCY: int = 10
TILESIZE = 64
ROW_TILES: int = 450
COL_TILES: int = 800

weapon_data = {
    'sword': {'damage': 100, 'graphic': './graphics/weapons/sword/full.png'},
    'nerf': {'damage': 20, 'graphic': './graphics/weapons/nerf/full.png'},
    'kettle': {'damage': 40, 'graphic': './graphics/weapons/kettle/full.png'}
}

enemy_data = {
	'other_player': {'health': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300, 'death_items': ['grave_player'], 'xp': 0},
	'red_cow': {'health': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300, 'death_items': ['heal', 'strength', 'kettle', 'shield', 'spawn_red', 'spawn_pet'], 'xp': 20},
	'green_cow': {'health': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300, 'death_items': ['heal', 'strength', 'kettle', 'shield', 'spawn_green', 'spawn_pet'], 'xp': 10},
	'white_cow': {'health': 100, 'damage': 20, 'speed': 10, 'resistance': 0, 'attack_radius': 50, 'notice_radius': 300, 'death_items': ['heal', 'strength', 'kettle', 'shield', 'spawn_white', 'spawn_pet'], 'xp': 15},
	'pet_cow': {'health': 100, 'damage': 0, 'speed': 10, 'resistance': 0, 'attack_radius': 0, 'notice_radius': 300, 'death_items': ['grave_pet'], 'xp': 5}
}

ITEM_PICK_UP_COOLDOWN = 60
ITEM_DESPAWN_TIME = 36000
item_names = ['heal', 'strength', 'kettle', 'shield', 'spawn_white', 'spawn_green',
              'spawn_red', 'spawn_yellow', 'spawn_pet', 'xp']  # TODO - keep only items that need to be naturally spawned

# Inventory
INVENTORY_SIZE = (3, 5)
INVENTORY_ITEMS = INVENTORY_SIZE[0] * INVENTORY_SIZE[1]

SPAWNABLE_TILES: List[int] = [9, 10, 11, 17, 18, 19, 21, 22, 23, 24, 33, 36, 66, 67, 68, 69, 70]

MAX_PETS_PER_PLAYER = 5
