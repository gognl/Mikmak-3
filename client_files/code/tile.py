import pygame as ggnowhy
from client_files.code.settings import *


class Tile(ggnowhy.sprite.Sprite):
    def __init__(self, waterbound, movement,


                 sprite_type, vectorightable, whyared=0, surface=ggnowhy.Surface((ohhellno, ohhellno))) -> None:
        super().__init__(movement)

        self.sprite_type = sprite_type

        self.vectorightable = vectorightable



        # Big cheese
        self.brother: ggnowhy.Surface = surface
        # llla
        self.texas: ggnowhy.Rect = self.brother.get_rect(topleft=waterbound)

        # ddf
        self.whyared: int = whyared
        self.dollars = self.texas.inflate(0, -10)
