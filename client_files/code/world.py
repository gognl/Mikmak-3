import random
from typing import Dict, Union, List

from client_files.code.interpolator import Interpolator
from client_files.code.other_player import OtherPlayer
from client_files.code.tile import Tile
from client_files.code.support import *
from client_files.code.weapon import Weapon
from client_files.code.enemy import Enemy
from client_files.code.projectile import Projectile
from client_files.code.ui import *
from client_files.code.structures import *
from client_files.code.explosion import *


class World:
    def __init__(self) -> None:
        # Pygame window
        self.display_surface: pygame.Surface = pygame.display.get_surface()

        # list of players using magnetic skill
        self.magnetic_players = pygame.sprite.Group()

        # Visible sprites: sprites that show on screen
        # Obstacle sprites: sprite the player can collide with
        # Server sprites: sprites whose updates have to be sent to the server
        self.visible_sprites: GroupYSort = GroupYSort()
        self.obstacle_sprites: pygame.sprite.Group = pygame.sprite.Group()  # players & walls
        self.all_obstacles: pygame.sprite.Group = pygame.sprite.Group()  # cows, players, and walls
        self.server_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.projectile_sprites: pygame.sprite.Group = pygame.sprite.Group()

        self.item_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.nametags: List[NameTag] = []

        # User interface
        self.ui = UI()

        # Calculate screen center
        self.half_width: int = self.display_surface.get_size()[0] // 2
        self.half_height: int = self.display_surface.get_size()[1] // 2
        self.screen_center: pygame.math.Vector2 = pygame.math.Vector2(self.half_width, self.half_height)

        # Camera position for drawing offset
        self.camera: pygame.math.Vector2 = pygame.math.Vector2()
        self.camera_distance_from_player: list[int, int] = list(CAMERA_DISTANCE_FROM_PLAYER)

        # Player before creation
        self.player: Player = None

        # enemies dict
        self.enemies: Dict[int, Enemy] = {}  # entity_id : Enemy
        # other players
        self.other_players: Dict[int, OtherPlayer] = {}  # entity_id : OtherPlayer
        # items
        self.items: Dict[int, Item] = {}

        # all players
        self.all_players: List[Union[Player, OtherPlayer]] = []

        # All layout csv files of the map
        self.layout: Dict[str, List[List[str]]] = {
            'floor': import_csv_layout('../graphics/map/map_Ground.csv'),
            'objects': import_csv_layout('../graphics/map/map_Objects.csv'),
            'boundary': import_csv_layout('../graphics/map/map_Barriers.csv'),
        }

        # All graphics groups
        self.graphics: dict[str: dict[int: pygame.Surface]] = {
            'floor': import_folder('../graphics/tiles'),
            'objects': import_folder('../graphics/objects')
        }

        # Load the map from settings.py
        self.create_map()

        # Zen
        self.zen_active = False

        self.interpolator: Interpolator = Interpolator(self)

        self.dt = 0

    def create_map(self) -> None:
        """
        Place movable tiles on the map
        :return: None
        """
        # Create player with starting position

        # Random player starting position generator
        while True:
            random_x = random.randint(0, 1280 * 40 // 64 - 1)
            random_y = random.randint(0, 720 * 40 // 64 - 1)
            if int(self.layout['floor'][random_y][random_x]) in SPAWNABLE_TILES and int(self.layout['objects'][random_y][random_x]) == -1:
                pos = (random_x * 64, random_y * 64)
                break
        pos = (25000, 800)
        self.player = Player("gognl", pos, (self.visible_sprites, self.obstacle_sprites, self.server_sprites, self.all_obstacles),
                             self.all_obstacles, 1, self.create_attack, self.destroy_attack, self.create_bullet,
                             self.create_kettle, self.create_inventory, self.destroy_inventory, self.create_chat, self.destroy_chat,
                             self.activate_zen, self.deactivate_zen, self.create_minimap, self.destroy_minimap, self.create_nametag,
                             self.nametag_update, self.get_inventory_box_pressed, self.create_dropped_item, self.spawn_enemy_from_egg,
                             0, self.magnetic_players, self.layout, self.create_lightning, self.create_magnet)  # TODO - make starting player position random (or a spawn)

        self.all_players.append(self.player)

        # Center camera
        self.camera.x = self.player.rect.centerx
        self.camera.y = self.player.rect.centery

    def create_attack(self, player: Union[Player, OtherPlayer]) -> None:
        player.current_weapon = Weapon(player, (self.visible_sprites,), self.obstacle_sprites, 3)

    def destroy_attack(self, player: Union[Player, OtherPlayer]):
        if player.current_weapon:
            player.current_weapon.kill()
        player.current_weapon = None

    def create_bullet(self, source: Union[Player, OtherPlayer, Enemy], pos, mouse=None):
        if isinstance(source, Player):
            mouse = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse[0], mouse[1]) - (source.rect.center - self.camera + self.screen_center)
            source.attacks.append(NormalServer.Output.AttackUpdate(weapon_id=source.weapon_index, attack_type=1, direction=tuple([int(i) for i in direction])))
        elif isinstance(source, Enemy):
            direction = pygame.math.Vector2(mouse[0] - source.rect.center[0], mouse[1] - source.rect.center[1])
        else:
            direction = pygame.math.Vector2(mouse)

        if not isinstance(source, Enemy):
            damage = int(weapon_data['nerf']['damage'] + (0.1 * source.strength))
        else:
            damage = source.damage

        Projectile(source, pos, direction, (self.visible_sprites, self.obstacle_sprites,
                                            self.projectile_sprites), self.all_obstacles, 4, 500, 5,
                   '../graphics/weapons/bullet.png', damage)

    def create_kettle(self, player: Union[Player, OtherPlayer], pos, mouse=None):
        if isinstance(player, Player):
            mouse = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse[0], mouse[1]) - (player.rect.center - self.camera + self.screen_center)
            player.attacks.append(NormalServer.Output.AttackUpdate(weapon_id=player.weapon_index, attack_type=1, direction=tuple([int(i) for i in direction])))
        else:
            direction = pygame.math.Vector2(mouse)
        Projectile(player, pos, direction, (self.visible_sprites, self.obstacle_sprites,
                    self.projectile_sprites), self.all_obstacles, 4, 75, 3,
                   '../graphics/weapons/kettle/full.png', int(weapon_data['kettle']['damage'] + (0.1 * player.strength)),
                   'explode', self.create_explosion, True)

    def create_inventory(self):
        self.ui.create_inventory()
        self.screen_center.x = self.half_width - int(INVENTORY_WIDTH / 2)
        self.camera_distance_from_player[0] = int(self.camera_distance_from_player[0] / 2)

    def destroy_inventory(self):
        self.ui.destroy_inventory()
        self.screen_center.x = self.half_width
        self.camera_distance_from_player = list(CAMERA_DISTANCE_FROM_PLAYER)

    def create_chat(self):
        self.ui.create_chat()

    def destroy_chat(self):
        self.ui.destroy_chat()

    def activate_zen(self):
        self.zen_active = True

    def deactivate_zen(self):
        self.zen_active = False

    def create_minimap(self):
        self.ui.create_minimap()

    def destroy_minimap(self):
        self.ui.destroy_minimap()

    def create_nametag(self, player, name):
        nametag = NameTag(player, name)
        self.nametags.append(nametag)

        return nametag

    def create_dropped_item(self, name, pos, item_id):
        self.items[item_id] = Item(item_id, name, (self.visible_sprites, self.item_sprites), pos, self.item_despawn, self.item_pickup, self.item_drop, self.item_use)

    def nametag_update(self, nametag):
        nametag.update(self.camera, self.screen_center)

    def get_inventory_box_pressed(self, mouse):
        return self.ui.get_inventory_box_pressed(mouse)

    def spawn_enemy_from_egg(self, pos, name):
        while True:
            random_x = pos[0] // 64 + (random.randint(2, 4) * random.randrange(-1, 2))
            random_y = pos[1] // 64 + (random.randint(2, 4) * random.randrange(-1, 2))

            if int(self.layout['floor'][random_y][random_x]) in SPAWNABLE_TILES and int(self.layout['objects'][random_y][random_x]) == -1:
                Enemy(name, (random_x * 64, random_y * 64), (self.visible_sprites, self.obstacle_sprites), 1,
                        self.obstacle_sprites, self.create_dropped_item, self.create_explosion, self.create_bullet)
                break

    def create_magnet(self):
        Explosion(self.player.rect.center, 0, (self.visible_sprites,), pygame.sprite.Group(), speed=1.05, radius=40, color='gray', player=self.player)

    def create_lightning(self):
        Explosion(self.player.rect.center, 0, (self.visible_sprites,), pygame.sprite.Group(), speed=1.26, radius=LIGHTNING_RADIUS, color='blue')

    def create_explosion(self, pos, damage):
        Explosion(pos, damage, (self.visible_sprites,), self.visible_sprites)

    def kill_enemy(self, enemy: Enemy):
        Explosion(enemy.rect.center, 0, (self.visible_sprites,), pygame.sprite.Group(), speed=1.26, radius=50)
        del self.enemies[enemy.entity_id]
        enemy.kill()

    def run(self) -> (TickUpdate, NormalServer.Output.StateUpdate):
        """
            Run one world frame
            :return: None
            """

        # Run the interpolation
        self.interpolator.interpolate()

        # Update the camera position
        self.update_camera()

        # Calculate played tile
        player_tile: pygame.math.Vector2 = pygame.math.Vector2(int(self.player.rect.x / TILESIZE),
                                                               int(self.player.rect.y / TILESIZE))

        # Create and display all visible sprites
        for style_index, (style, layout) in enumerate(self.layout.items()):
            for row_index in range(int(player_tile.y - ROW_LOAD_TILE_DISTANCE),
                                   int(player_tile.y + ROW_LOAD_TILE_DISTANCE)):
                if 0 <= row_index < ROW_TILES:
                    row = layout[row_index]
                    for col_index in range(int(player_tile.x - COL_LOAD_TILE_DISTANCE),
                                           int(player_tile.x + COL_LOAD_TILE_DISTANCE)):
                        if 0 <= col_index < COL_TILES:
                            col = row[col_index]
                            if col != '-1':  # -1 in csv means no tile, don't need to recreate the tile if it already exists
                                x: int = col_index * TILESIZE
                                y: int = row_index * TILESIZE

                                if style == 'floor':
                                    surface: pygame.Surface = self.graphics['floor'][col]
                                    Tile((x, y), (self.visible_sprites,), 'floor', col in SPAWNABLE_TILES, 0, surface)
                                elif style == 'objects':
                                    surface: pygame.Surface = self.graphics['objects'][col]
                                    Tile((x, y), (self.visible_sprites, self.obstacle_sprites, self.all_obstacles), 'object', False, 1,
                                         surface)
                                elif style == 'boundary':
                                    Tile((x, y), (self.obstacle_sprites, self.all_obstacles), 'barrier', False)

        # Display all visible sprites
        self.visible_sprites.custom_draw(self.camera, self.screen_center)

        # Update the obstacle sprites for the player
        self.player.update_items(self.item_sprites)

        self.player.dt = self.dt
        for proj in self.projectile_sprites.sprites():
            proj.dt = self.dt
        for player in self.other_players.values():
            player.dt = self.dt

        # UI
        for nametag in self.nametags:
            if nametag.kill:
                del nametag
            else:
                nametag.display()
        if not self.zen_active:
            self.ui.display(self.player)

        # Run update() function in all visible sprites' classes
        self.visible_sprites.update()

        # Delete all tiles
        for sprite in self.visible_sprites.sprites() + self.obstacle_sprites.sprites():
            if type(sprite) is Tile:
                sprite.kill()

        # Get info about changes made in this tick (used for server synchronization)
        if self.player.changes is None:
            return None, None  # no changes
        player_changes = NormalServer.Output.PlayerUpdate(id=self.player.entity_id, changes=self.player.changes)
        state_update: NormalServer.Output.StateUpdate = NormalServer.Output.StateUpdate(player_changes=player_changes)  # sent to server
        tick_update: TickUpdate = TickUpdate(player_changes)  # kept for synchronization

        messages = self.ui.new_messages.copy()
        self.ui.new_messages.clear()
        return tick_update, state_update, messages

    def update_camera(self) -> None:
        """
        update the camera position
        :return: None
        """
        # Figure out offset based on camera position

        # X axis
        if abs(self.player.rect.centerx - self.camera.x) > self.camera_distance_from_player[0]:  # If the camera is too far from the player
            if self.player.rect.centerx > self.camera.x:  # Move the camera from to the left of the bound if it's further left than the player
                self.camera.x = self.player.rect.centerx - self.camera_distance_from_player[0]
            else:  # Move the camera from to the right of the bound if it's further right than the player
                self.camera.x = self.player.rect.centerx + self.camera_distance_from_player[0]

        # Y axis
        if abs(self.player.rect.centery - self.camera.y) > self.camera_distance_from_player[1]:  # If the camera is too far from the player
            if self.player.rect.centery > self.camera.y:  # Move the camera from to the top of the bound if it's further up than the player
                self.camera.y = self.player.rect.centery - self.camera_distance_from_player[1]
            else:  # Move the camera from to the bottom of the bound if it's further down than the player
                self.camera.y = self.player.rect.centery + self.camera_distance_from_player[1]

    def spawn_enemies(self, amount: int) -> None:
        for enemy in range(amount):
            while True:
                random_x = random.randint(0, 1280 * 40 // 64 - 1)
                random_y = random.randint(0, 720 * 40 // 64 - 1)
                name = list(enemy_data.keys())[int(random.randint(1, 3))]  # Don't include other_player or pets

                if int(self.layout['floor'][random_y][random_x]) in SPAWNABLE_TILES and int(self.layout['objects'][random_y][random_x]) == -1:
                    Enemy(name, (random_x * 64, random_y * 64), (self.visible_sprites, self.obstacle_sprites), 1,
                          self.obstacle_sprites, self.create_dropped_item, self.create_explosion, self.create_bullet)
                    break

    def item_despawn(self, item: Item):
        """Remove the item from the game"""
        item.kill()

    def item_pickup(self, item: Item, player_id: int) -> None:
        """Add the item to the player's inventory and remove it from the floor"""

        # other players' inventories don't matter to this client
        if self.player.entity_id != player_id:
            del self.items[item.item_id]
            item.kill()
            return

        if item.name == "xp":
            self.player.xp += 1
            item.kill()
        elif item.name == "grave_player":
            self.player.inventory_items[item.name + f'({len(self.player.inventory_items)})'] = InventorySlot(item.item_id)
            del self.items[item.item_id]
            item.kill()
        else:
            if item.name in self.player.inventory_items:
                self.player.inventory_items[item.name].add_item(item.item_id)
                del self.items[item.item_id]
                item.kill()
            else:
                self.player.inventory_items[item.name] = InventorySlot(item.item_id)
                del self.items[item.item_id]
                item.kill()

    def item_drop(self, item: Item, player_id: int, pos: (int, int)) -> None:
        """Remove the item from the player's inventory and drop it on the floor"""
        if player_id == self.player.entity_id:
            return  # already dropped
        self.create_dropped_item(item.name, pos, item.item_id)

    def item_use(self, item: Item, player_id: int, pos: (int, int)) -> None:
        """Remove the item from the player's inventory and use it"""


class GroupYSort(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def custom_draw(self, camera: pygame.math.Vector2, screen_center: pygame.math.Vector2) -> None:
        """
        Draws the sprites on screen according to the screen height, and then according to the position of the camera
        :return: None
        """
        # For every visible sprite, from top to bottom
        for sprite in sorted(self.sprites(), key=lambda x: (x.height, x.rect.centery)):
            # Display the sprite on screen, moving it by the calculated offset
            self.display_surface.blit(sprite.image, sprite.rect.topleft - camera + screen_center)
