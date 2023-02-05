import pygame
from client_files.code.settings import *
from client_files.code.entity import Entity
from client_files.code.support import *


class Enemy(Entity):
    def __init__(self, world, enemy_name, pos, groups, entity_id):

        # general setup
        super().__init__(world, groups, entity_id)
        self.sprite_type = 'enemy'

        # graphics setup
        self.import_graphics(enemy_name)
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.height = 1

        # Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
        self.hitbox = self.rect.inflate(-20, -26)

    def import_graphics(self, name):

        if name == 'other_player':
            path: str = '../graphics/player/'
            self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [],
                               'left_idle': [], 'right_idle': []}
            for animation in self.animations.keys():
                self.animations[animation] = list(import_folder(path + animation).values())

            self.status = 'down_idle'

        else:
            self.animations = {'move': []}
            path = f'../graphics/monsters/{name}/move/'
            self.animations['move'] = list(import_folder(path).values())
            self.status = 'move'

    def animate(self) -> None:
        """
        animate through images
        :return: None
        """
        animation: list[pygame.Surface] = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update_pos(self, pos: (int, int)) -> None:
        self.rect.x = pos[0]
        self.rect.y = pos[1]
