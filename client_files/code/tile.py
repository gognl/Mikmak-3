import pygame
from client_files.code.settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, spawnable, height=0, surface=pygame.Surface((TILESIZE, TILESIZE))) -> None:
        super().__init__(groups)

        self.sprite_type = sprite_type

        self.spawnable = spawnable

        # Load image from files
        self.image: pygame.Surface = surface

        # Position of the tile
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)

        # Height of tile on screen - 0 is background
        self.height: int = height

        # Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
        self.hitbox = self.rect.inflate(0, -10)
