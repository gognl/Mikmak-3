import pygame
from server_files_normal.game.settings import *


class Barrier(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surface=pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)

        self.sprite_type = 'barrier'

        # Load image from files
        self.image: pygame.Surface = surface

        # Position of the tile
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)

        # Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
        self.hitbox = self.rect.inflate(0, -10)
