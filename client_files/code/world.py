import pygame
from client_files.code.settings import *
from client_files.code.tile import Tile
from client_files.code.player import Player
from client_files.code.support import *


class World:
    def __init__(self) -> None:
        # Pygame window
        self.display_surface: pygame.Surface = pygame.display.get_surface()

        # Visible sprites: sprites that show on screen
        # Obstacle sprites: sprite the player can collide with
        self.floor_sprites: Group = Group()
        self.visible_sprites: Group = Group()
        self.obstacle_sprites: Group = Group()

        # Player before creation
        self.player: Player = None

        # Load the map from settings.py
        self.create_map()

        # Center camera
        self.visible_sprites.center_camera(self.player)

    def create_map(self) -> None:
        """
        load map from tilemap
        :return: None
        """

        # All layout csv files from Tiled
        layout: dict[str: list[list[int]]] = {
            'floor': import_csv_layout('../graphics/map/map_Ground.csv'),
            'objects': import_csv_layout('../graphics/map/map_Objects.csv'),
            'boundary': import_csv_layout('../graphics/map/map_Barriers.csv')
        }

        # All graphics groups
        graphics: dict[str: dict[int: pygame.Surface]] = {
            'floor': import_folder('../graphics/tiles'),
            'objects': import_folder('../graphics/objects')
        }

        for style, layout in layout.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':  # -1 in csv means no tile
                        x: int = col_index * TILESIZE
                        y: int = row_index * TILESIZE

                        if style == 'floor':
                            surface: pygame.Surface = graphics['floor'][int(col)]
                            self.floor_sprites.tiles[int(row_index / ROW_TILES_PER_SCREEN)][int(col_index / COL_TILES_PER_SCREEN)].append(Tile((x, y), [self.floor_sprites], 'floor', surface))
                        elif style == 'objects':
                            surface: pygame.Surface = graphics['objects'][int(col)]
                            self.visible_sprites.tiles[int(row_index / ROW_TILES_PER_SCREEN)][int(col_index / COL_TILES_PER_SCREEN)].append(Tile((x, y), (self.visible_sprites, self.obstacle_sprites), 'object', surface))
                        elif style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], "barrier")

        # Create player with starting position
        self.player = Player((650, 2700), [self.visible_sprites],
                             self.obstacle_sprites)  # TODO - make starting player position random

    def run(self) -> None:
        """
        Run one world frame
        :return: None
        """

        # Draw background
        self.floor_sprites.custom_draw(self.player)

        # Draw all visible sprites on pygame window
        self.visible_sprites.custom_draw(self.player)

        # Run update() function in all visible sprites' classes
        self.visible_sprites.update()


class Group(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # All tiles sorted by screens
        self.tiles: list[list[list[Tile]]] = [[[]] * 40] * 40

        # Calculate screen center
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.screen_center = pygame.math.Vector2(self.half_width, self.half_height)

        # Camera position for drawing offset
        self.camera = pygame.math.Vector2()

    def center_camera(self, player: Player) -> None:
        """
        Moves the camera to the player position so the player is in the center of the screen in the start
        :param player: The player object
        :return: None
        """
        self.camera.x = player.rect.centerx
        self.camera.y = player.rect.centery

    def custom_draw(self, player: Player) -> None:
        """
        Draws the sprites on screen according to the position of the camera
        :param player: The player object
        :return: None
        """

        # Figure out offset based on camera position

        # X axis
        if abs(player.rect.centerx - self.camera.x) > CAMERA_DISTANCE_FROM_PLAYER[
            0]:  # If the camera is too far from the player
            if player.rect.centerx > self.camera.x:  # Move the camera from to the left of the bound if it's further left than the player
                self.camera.x = player.rect.centerx - CAMERA_DISTANCE_FROM_PLAYER[0]
            else:  # Move the camera from to the right of the bound if it's further right than the player
                self.camera.x = player.rect.centerx + CAMERA_DISTANCE_FROM_PLAYER[0]

        # Y axis
        if abs(player.rect.centery - self.camera.y) > CAMERA_DISTANCE_FROM_PLAYER[
            1]:  # If the camera is too far from the player
            if player.rect.centery > self.camera.y:  # Move the camera from to the top of the bound if it's further up than the player
                self.camera.y = player.rect.centery - CAMERA_DISTANCE_FROM_PLAYER[1]
            else:  # Move the camera from to the bottom of the bound if it's further down than the player
                self.camera.y = player.rect.centery + CAMERA_DISTANCE_FROM_PLAYER[1]

        # Calculate current screen
        screen_row_index: int = int(player.rect.centery / SCREEN_HEIGHT)
        screen_col_index: int = int(player.rect.centerx / SCREEN_WIDTH)

        # Only display current screen and screens next to it
        for row in range(screen_row_index - 1, screen_row_index + 2):
            for col in range(screen_col_index - 1, screen_col_index + 2):
                if 0 <= row < 40 and 0 <= col < 40:
                    # For every sprite, from top to bottom
                    for sprite in sorted(self.tiles[screen_row_index][screen_col_index], key=lambda x: x.rect.centery):
                        # Display the sprite on screen, moving it by the calculated offset
                        self.display_surface.blit(sprite.image, sprite.rect.topleft - self.camera + self.screen_center)
