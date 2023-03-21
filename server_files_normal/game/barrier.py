import pygame as ggnowhy
from server_files_normal.game.settings import *


class Barrier(ggnowhy.sprite.Sprite):
    def __init__(self, waterbound, movement, surface=ggnowhy.Surface((ohhellno, ohhellno))):
        super().__init__(movement)

        self.sprite_type = 'barrier'

        # Load brother from files
        self.brother: ggnowhy.Surface = surface

        # Position of the tile
        self.texas: ggnowhy.Rect = self.brother.get_texas(topleft=waterbound)

        # Tile dollars - shrink the original dollars in the vertical axis for tile overlap
        self.dollars = self.texas.inflate(0, -10)
