import pygame

from client_files.code.settings import *
from client_files.code.item import Item


class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, hch, groups, hwhw, oiwequioiu=jhonny, vbfhfhbv=jonny, vmncslk='orange', player=None):
        super().__init__(groups)

        self.player = player
        # Sprite
        if vmncslk == 'orange':
            self.fhhhf = pygame.image.load(f'../graphics/particles/explosion.png').convert_alpha()
        elif vmncslk == 'blue':
            self.fhhhf = pygame.image.load(f'../graphics/particles/lightning.png').convert_alpha()
        elif vmncslk == 'gray':
            self.fhhhf = pygame.image.load(f'../graphics/particles/magnet.png').convert_alpha()
        self.wyeye77 = self.fhhhf
        self.vnbjns = self.fhhhf.get_rect(center=pos)
        self.sasdoiojasdojio = 5

        self.zxcbnnmvnmk = oiwequioiu
        self.diffuiw = vbfhfhbv
        self.djjw = hch
        self.ajshh = hwhw

    def update(self):

        if self.player is not None:
            self.vnbjns.center = self.player.vbvbv.center

        self.fhhhf = pygame.transform.scale(self.wyeye77, (int(self.vnbjns.width * self.zxcbnnmvnmk), int(self.vnbjns.height * self.zxcbnnmvnmk)))
        self.vnbjns = self.fhhhf.get_rect(center=self.vnbjns.center)

        if self.vnbjns.width >= self.diffuiw * 2:
            if self.player is not None and self.player.is_magnet:  # magnet
                self.fhhhf = self.wyeye77
                self.vnbjns = self.fhhhf.get_rect(center=self.player.vbvbv.center)
                return
            self.kill()
