import pygame
from settings import *
from tile import Tile
from player import Player


class World:
    def __init__(self) -> None:
        # Pygame window
        self.display_surface: pygame.Surface = pygame.display.get_surface()

        # Visible sprites: sprites that show on screen
        # Obstacle sprites: sprite the player can collide with
        self.visible_sprites: pygame.Group = pygame.sprite.Group()
        self.obstacle_sprites: pygame.Group = pygame.sprite.Group()

        # Player before creation
        self.player: Player = None

        # Load the map from settings.py
        self.create_map()

    def create_map(self) -> None:
        """
        Load every tile from settings.py and add it to relevant groups
        :return: None
        """
        # For every tile in the world map from settings.py:
        for r, row in enumerate(WORLD_MAP):
            for c, col in enumerate(row):
                # Get x and y coordinates of the tile
                x: int = c * TILESIZE
                y: int = r * TILESIZE

                # Figure out what tile it is
                if col == 'x':  # Rock
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
                if col == 'p':  # Player
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)

    def run(self) -> None:
        """
        Run one world frame
        :return: None
        """
        # Draw all visible sprites on pygame window
        self.visible_sprites.draw(self.display_surface)

        # Run update() function in all visible sprites' classes
        self.visible_sprites.update()
