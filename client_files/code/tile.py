import pygame
from client_files.code.settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups) -> None:
        super().__init__(groups)

        # Load image from files
        self.image: pygame.Surface = pygame.image.load('../graphics/rock.png').convert_alpha()

        # Position of the tile
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
