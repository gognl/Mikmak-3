import pygame
from client_files.code.settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups,


                 sprite_type, spawnable, height=0, surface=pygame.Surface((TILESIZE, TILESIZE))) -> None:
        super().__init__(groups)

        self.sprite_type = sprite_type

        self.spawnable = spawnable



        # Big cheese
        self.image: pygame.Surface = surface
        # llla
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)

        # ddf
        self.height: int = height
        self.hitbox = self.rect.inflate(0, -10)
