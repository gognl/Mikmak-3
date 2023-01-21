import pygame
from client_files.code.settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, height=0, surface=pygame.Surface((TILESIZE, TILESIZE))) -> None:
        super().__init__(groups)

        self.sprite_type = sprite_type

        # Load image from files
        self.image: pygame.Surface = surface

        # Position of the tile
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)

        # Height of tile on screen - 0 is background
        self.height: int = height

        # Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
        if self.sprite_type != "barrier":  # Barrier tiles don't get inflated collision boxes
            self.hitbox = self.rect.inflate(0, -10)
        else:
            self.hitbox = self.rect.inflate(0, 26)  # Undo player collision box inflation
