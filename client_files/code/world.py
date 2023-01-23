import pygame
from client_files.code.settings import *
from client_files.code.tile import Tile
from client_files.code.player import Player
from client_files.code.support import *
from client_files.code.weapon import Weapon


class World:
    def __init__(self) -> None:
        # Pygame window
        self.display_surface: pygame.Surface = pygame.display.get_surface()

        # Visible sprites: sprites that show on screen
        # Obstacle sprites: sprite the player can collide with
        self.visible_sprites: Group_YSort = Group_YSort()
        self.obstacle_sprites: pygame.sprite.Group = pygame.sprite.Group()

        # Calculate screen center
        self.half_width: int = self.display_surface.get_size()[0] // 2
        self.half_height: int = self.display_surface.get_size()[1] // 2
        self.screen_center: pygame.math.Vector2 = pygame.math.Vector2(self.half_width, self.half_height)

        # Camera position for drawing offset
        self.camera: pygame.math.Vector2 = pygame.math.Vector2()

        # Player before creation
        self.player: Player = None

        # attack sprites
        self.current_attack = None

        # Load the map from settings.py
        self.create_map()

        # All layout csv files of the map
        self.layout: dict[str: list[list[int]]] = {
            'floor': import_csv_layout('../graphics/map/map_Ground.csv'),
            'objects': import_csv_layout('../graphics/map/map_Objects.csv'),
            'boundary': import_csv_layout('../graphics/map/map_Barriers.csv')
        }

        # All graphics groups
        self.graphics: dict[str: dict[int: pygame.Surface]] = {
            'floor': import_folder('../graphics/tiles'),
            'objects': import_folder('../graphics/objects')
        }

    def create_map(self) -> None:
        """
        Place moveable tiles on the map
        :return: None
        """

        # Create player with starting position
        self.player = Player((650, 2700), [self.visible_sprites], 1, self.obstacle_sprites, self.create_attack, self.destroy_attack)

        # Center camera
        self.camera.x = self.player.rect.centerx
        self.camera.y = self.player.rect.centery

    def create_attack(self) -> None:
        self.current_attack = Weapon(self.player, [self.visible_sprites])

    def destroy_attack(self) -> None:
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def run(self) -> None:
        """
        Run one world frame
        :return: None
        """

        # Update the camera position
        self.update_camera()

        # Calculate played tile
        player_tile: pygame.math.Vector2 = pygame.math.Vector2(int(self.player.rect.x / TILESIZE), int(self.player.rect.y / TILESIZE))

        # Create and display all visible sprites
        for style_index, (style, layout) in enumerate(self.layout.items()):
            for row_index in range(int(player_tile.y - ROW_LOAD_TILE_DISTANCE), int(player_tile.y + ROW_LOAD_TILE_DISTANCE)):
                if 0 <= row_index < ROW_TILES:
                    row = layout[row_index]
                    for col_index in range(int(player_tile.x - COL_LOAD_TILE_DISTANCE), int(player_tile.x + COL_LOAD_TILE_DISTANCE)):
                        if 0 <= col_index < COL_TILES:
                            col = row[col_index]
                            if col != '-1':  # -1 in csv means no tile, don't need to recreate the tile if it already exists
                                x: int = col_index * TILESIZE
                                y: int = row_index * TILESIZE

                                if style == 'floor':
                                    surface: pygame.Surface = self.graphics['floor'][int(col)]
                                    Tile((x, y), [self.visible_sprites], 'floor', 0, surface)
                                elif style == 'objects':
                                    surface: pygame.Surface = self.graphics['objects'][int(col)]
                                    Tile((x, y), (self.visible_sprites, self.obstacle_sprites), 'object', 1, surface)
                                elif style == 'boundary':
                                    Tile((x, y), [self.obstacle_sprites], 'barrier')

        # Display all visible sprites
        self.visible_sprites.custom_draw(self.camera, self.screen_center)

        # Update the obstacle sprites for the player
        self.player.update_obstacles(self.obstacle_sprites)

        # Run update() function in all visible sprites' classes
        self.visible_sprites.update(self.camera)

        # Delete all tiles
        for sprite in self.visible_sprites.sprites() + self.obstacle_sprites.sprites():
            if sprite != self.player:
                sprite.kill()

    def update_camera(self) -> None:
        """
        update the camera position
        :return: None
        """
        # Figure out offset based on camera position

        # X axis
        if abs(self.player.rect.centerx - self.camera.x) > CAMERA_DISTANCE_FROM_PLAYER[
            0]:  # If the camera is too far from the player
            if self.player.rect.centerx > self.camera.x:  # Move the camera from to the left of the bound if it's further left than the player
                self.camera.x = self.player.rect.centerx - CAMERA_DISTANCE_FROM_PLAYER[0]
            else:  # Move the camera from to the right of the bound if it's further right than the player
                self.camera.x = self.player.rect.centerx + CAMERA_DISTANCE_FROM_PLAYER[0]

        # Y axis
        if abs(self.player.rect.centery - self.camera.y) > CAMERA_DISTANCE_FROM_PLAYER[
            1]:  # If the camera is too far from the player
            if self.player.rect.centery > self.camera.y:  # Move the camera from to the top of the bound if it's further up than the player
                self.camera.y = self.player.rect.centery - CAMERA_DISTANCE_FROM_PLAYER[1]
            else:  # Move the camera from to the bottom of the bound if it's further down than the player
                self.camera.y = self.player.rect.centery + CAMERA_DISTANCE_FROM_PLAYER[1]


class Group_YSort(pygame.sprite.Group):
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
