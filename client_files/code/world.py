from collections import deque
import random

import pygame
from typing import Dict
from client_files.code.settings import *
from client_files.code.tile import Tile
from client_files.code.player import Player
from client_files.code.support import *
from client_files.code.weapon import Weapon
from client_files.code.enemy import Enemy
from client_files.code.projectile import Projectile
from client_files.code.structures import *


class World:
    def __init__(self) -> None:
        # Pygame window
        self.display_surface: pygame.Surface = pygame.display.get_surface()

        # Visible sprites: sprites that show on screen
        # Obstacle sprites: sprite the player can collide with
        # Server sprites: sprites whose updates have to be sent to the server
        self.visible_sprites: GroupYSort = GroupYSort()
        self.obstacle_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.server_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.projectile_sprites: pygame.sprite.Group = pygame.sprite.Group()

        # attack sprites
        self.current_weapon = None

        # Calculate screen center
        self.half_width: int = self.display_surface.get_size()[0] // 2
        self.half_height: int = self.display_surface.get_size()[1] // 2
        self.screen_center: pygame.math.Vector2 = pygame.math.Vector2(self.half_width, self.half_height)

        # Camera position for drawing offset
        self.camera: pygame.math.Vector2 = pygame.math.Vector2()

        # Player before creation
        self.player: Player = None

        # enemies dict
        self.enemies: Dict[int, Enemy] = {}  # entity_id : Enemy

        # All layout csv files of the map
        self.layout: dict[str: list[list[int]]] = {
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

    def create_map(self) -> None:
        """
        Place movable tiles on the map
        :return: None
        """
        # Create player with starting position
        self.player = Player((1024, 1024), [self.visible_sprites, self.server_sprites],
                             self.obstacle_sprites, 1, self.create_attack, self.destroy_attack, self.create_bullet,
                             self.create_kettle, 0)  # TODO - make starting player position random (or a spawn)

        # Center camera
        self.camera.x = self.player.rect.centerx
        self.camera.y = self.player.rect.centery

        # Spawn enemies
        self.spawn_enemies(100000)  # TODO: enemy count, spawn more if under 100

    def create_attack(self) -> None:
        self.current_weapon = Weapon(self.player, [self.visible_sprites], 2)

    def destroy_attack(self):
        if self.current_weapon:
            self.current_weapon.kill()
        self.current_weapon = None

    def create_bullet(self):
        Projectile(self.player, self.camera, self.screen_center, self.current_weapon,
                   pygame.mouse.get_pos(), (self.visible_sprites, self.obstacle_sprites,
                                            self.projectile_sprites), self.obstacle_sprites, 3, 15, 2000,
                   '../graphics/weapons/bullet.png')

    def create_kettle(self):
        Projectile(self.player, self.camera, self.screen_center, self.current_weapon,
                   pygame.mouse.get_pos(), (self.visible_sprites, self.obstacle_sprites,
                                            self.projectile_sprites), self.obstacle_sprites, 3, 5, 750,
                   '../graphics/weapons/kettle/full.png', 'explode', True)

    def run(self, changes: deque) -> None:
        """
        Run one world frame
        :return: None
        """

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
                                    Tile((x, y), [self.visible_sprites], 'floor', col in SPAWNABLE_TILES, 0, surface)
                                elif style == 'objects':
                                    surface: pygame.Surface = self.graphics['objects'][col]
                                    Tile((x, y), (self.visible_sprites, self.obstacle_sprites), 'object', False, 1,
                                         surface)
                                elif style == 'boundary':
                                    Tile((x, y), [self.obstacle_sprites], 'barrier', False)

        # Display all visible sprites
        self.visible_sprites.custom_draw(self.camera, self.screen_center)

        # Update the obstacle sprites for the player
        self.player.update_obstacles(self.obstacle_sprites)
        for projectile in self.projectile_sprites:
            projectile.update_obstacles(self.obstacle_sprites)

        # Run update() function in all visible sprites' classes
        self.visible_sprites.update()

        local_changes = [[], [], []]  # A list of changes made in this tick. 0 - player, 1 - enemies, 2 - items.
        for sprite in self.server_sprites.sprites():
            if sprite.changes is None:  # If no new changes were made
                continue
            if type(sprite) is Player:
                local_changes[0].append(Server.Output.PlayerUpdate(id=sprite.entity_id, changes=sprite.changes))
            elif type(sprite) is Enemy:
                pass  # append EnemyUpdate to local_changes[1]

        changes.append(Server.Output.StateUpdate(changes=local_changes))

        # Delete all tiles
        for sprite in self.visible_sprites.sprites() + self.obstacle_sprites.sprites():
            if type(sprite) is Tile:
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

    def spawn_enemies(self,
                      amount: int) -> None:  # TODO: should be random, dont spawn on water/player, collidable block

        for enemy in range(amount):
            random_x = random.randint(0, 1280 * 40 // 64 - 1)
            random_y = random.randint(0, 720 * 40 // 64 - 1)
            name = list(enemy_data.keys())[int(random.randint(0, 3))]

            if int(self.layout['floor'][random_y][random_x]) in SPAWNABLE_TILES:
                Enemy(enemy_name=name, pos=(random_x * 64, random_y * 64),
                      groups=[self.visible_sprites, self.obstacle_sprites],
                      entity_id=None)  # TODO: @gognl whats # entity id?


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
