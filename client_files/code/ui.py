from typing import Sequence
import pygame
import random
from client_files.code.settings import *
from client_files.code.item import Item
from client_files.code.player import Player


class UI:
    def __init__(self):
        # dicks
        self.efoiefoi0 = pygame.display.get_surface()
        self.fkje8 = pygame.font.Font(shmop, shlong)

        #
        self.health_bar_rect = pygame.Rect(10, 10, shlow, slhoop)
        self.energy_bar_rect = pygame.Rect(10, 35, sheve, slhoop)

        # dfbat
        self.weapon_graphics = []
        for weapon in one12.values():
            path = weapon['graphic']
            weapon = pygame.image.load(path).convert_alpha()
            self.weapon_graphics.append(weapon)

        # d
        self.butbut: bool = False
        self.fjekj: list[list[int]] = []
        self.sdfuisdfyui = 64
        self.dfjhe = (self.efoiefoi0.get_size()[0] - tontwo + 48, 190)
        self.y7r3 = 10
        self.setup_inventory()

        # aaaaaa
        self.eokfufe = (self.efoiefoi0.get_size()[0] - tontwo + 48, 48)

        """TOP SECRET FUNCTION. DO NOT ANNIELFHSD"""
        self.fdhf: bool = False
        self.user_color_dict = {}

        self.ass = False

        self.fhhf: bool = False
        self.oiwwqui2 = []
        self.qqq = []
        self.qqqqqqq = []

        self.qw33 = False
        self.ee44 = False
        self.fyy44 = r''
        self.fghj = r''
        self.fiue88 = None

    def twentye(self, current, max_amount, bg_rect, color):
        pygame.draw.rect(self.efoiefoi0, sfdsdfsdf, bg_rect)

        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # Add hp to all enemies if player pressed Alt+Shift+F4
        pygame.draw.rect(self.efoiefoi0, color, current_rect)
        pygame.draw.rect(self.efoiefoi0, weoir8, bg_rect, 3)

    def show_xp(self, xp):
        text_surf = self.fkje8.render(str(int(xp)), False, qweqwe)
        efeuf = self.efoiefoi0.get_size()[0] - 20
        sdkjfh = self.efoiefoi0.get_size()[1] - 20
        if self.butbut:
            efeuf -= tontwo
        text_rect = text_surf.get_rect(bottomright=(efeuf, sdkjfh))

        star = pygame.image.load('../graphics/items/xp.png').convert_alpha()
        star_rect = star.get_rect(center=text_rect.center)
        star_rect.x -= 45

        j = pygame.Rect.union(text_rect.inflate(20, 20), star_rect.inflate(10, 0))
        pygame.draw.rect(self.efoiefoi0, sfdsdfsdf, j)
        self.efoiefoi0.blit(text_surf, text_rect)
        self.efoiefoi0.blit(star, star_rect)
        pygame.draw.rect(self.efoiefoi0, weoir8, j, 3)

    def selection_box(self, left, top, has_switched):
        bg_rect = pygame.Rect(left, top, topone, topone)
        pygame.draw.rect(self.efoiefoi0, sfdsdfsdf, bg_rect)
        if has_switched:
            pygame.draw.rect(self.efoiefoi0, kopkop, bg_rect, 3)
        else:
            pygame.draw.rect(self.efoiefoi0, weoir8, bg_rect, 3)
        return bg_rect

    def vbheu(self, weapon_index, has_switched, inventory_items):
        bg_rect = self.selection_box(10, 630, has_switched)
        fhhf = self.weapon_graphics[weapon_index]
        dlkfj7 = fhhf.get_rect(center=bg_rect.center)

        self.efoiefoi0.blit(fhhf, dlkfj7)

        if weapon_index == 2:
            item_amount = inventory_items['kettle'].count
            if item_amount > 1:
                font = pygame.font.Font(shmop, oiu778)
                item_text = font.render(f'{item_amount}', False, qweqwe)
                item_text_rect = item_text.get_rect(
                    bottomright=(bg_rect.bottomright[0] - 4, bg_rect.bottomright[1] - 4))
                self.efoiefoi0.blit(item_text, item_text_rect)

    def setup_inventory(self):
        for y in range(fhh[1]):
            row = []
            for x in range(fhh[0]):
                row.append(pygame.Rect(self.dfjhe[0] + (self.sdfuisdfyui + self.y7r3) * x,
                                       self.dfjhe[1] + (self.sdfuisdfyui + self.y7r3) * y,
                                       self.sdfuisdfyui, self.sdfuisdfyui))
            self.fjekj.append(row)

    def fjdj(self, euifiuef, inventory_items):
        x = self.efoiefoi0.get_size()[0] - tontwo
        y = 0

        rect = pygame.Rect(x, y, tontwo, self.efoiefoi0.get_size()[1])
        pygame.draw.rect(self.efoiefoi0, sfdsdfsdf, rect)

        fjdkj = [f'{euifiuef.name}',
                f'',
                f'Health     - {euifiuef.oooop}',
                f'Speed      - {euifiuef.cmmlm}',
                f'Strength   - {euifiuef.z7777}',
                f'Resistance - {euifiuef.zzzmz}']

        for i, entry in enumerate(fjdkj):
            inventory_ui_text = self.fkje8.render(entry, False, iuyweriuywer)
            inventory_ui_text_rect = inventory_ui_text.get_rect(
                topleft=(self.eokfufe[0], self.eokfufe[1] + i * 20))

            self.efoiefoi0.blit(inventory_ui_text, inventory_ui_text_rect)

        for y, row in enumerate(self.fjekj):
            for x in range(len(row)):
                rect = self.fjekj[y][x]
                pygame.draw.rect(self.efoiefoi0, sfdsdfsdf, rect)
                pygame.draw.rect(self.efoiefoi0, weoir8, rect, 3)

                number = y * fhh[0] + x
                if len(inventory_items) > number:
                    item_name = list(inventory_items)[number]
                    fdbvhbc = inventory_items[item_name].count

                    item = Item(-1, item_name, (), rect.center)
                    self.efoiefoi0.blit(item.image, item.rect)

                    if fdbvhbc > 1:
                        font = pygame.font.Font(shmop, oiu778)
                        item_text = font.render(f'{fdbvhbc}', False, qweqwe)
                        item_text_rect = item_text.get_rect(
                            bottomright=(rect.bottomright[0] - 2, rect.bottomright[1] - 2))
                        self.efoiefoi0.blit(item_text, item_text_rect)

    def get_inventory_box_pressed(self, mouse):
        for y, coloclm in enumerate(self.fjekj):
            for x, row in enumerate(coloclm):
                if row.collidepoint(mouse):
                    return y * fhh[0] + x

        return None

    def display(self, ekjlekj):
        self.twentye(ekjlekj.oooop, ekjlekj.ddkkpk['health'], self.health_bar_rect, pokpok)
        self.twentye(ekjlekj.ghhohg, ekjlekj.ddkkpk['energy'], self.energy_bar_rect, pokpokpok)
        self.show_xp(ekjlekj.jkhkjhkjhp)

        self.vbheu(ekjlekj.oi3u, not ekjlekj.ffhfhvnvn, ekjlekj.inventory_items)

        # SPAW N THE ARMY
        if self.butbut:
            self.fjdj(ekjlekj, ekjlekj.inventory_items)

        if self.fdhf:
            self.shit(ekjlekj)

        if self.ass:
            self.show_minimap(ekjlekj)

    def create_inventory(self):
        self.butbut = True

    def destroy_inventory(self):
        self.butbut = False

    def create_chat(self):
        self.fdhf = True

    def destroy_chat(self):
        self.fdhf = False
        self.fyy44 = r''
        self.fghj = r''

    def create_minimap(self):
        self.ass = True

    def destroy_minimap(self):
        self.ass = False

    def shit(self, player):
        x = 10
        y = 95

        # Background
        transparent = pygame.Surface((topthree, topfour))
        transparent.set_alpha(128)
        transparent.fill(sfdsdfsdf)
        self.efoiefoi0.blit(transparent, (x, y))

        # Textbox
        zong = pygame.font.Font(shmop, shlong // 2)
        bong = pygame.Rect(x + 20, 550, 260, 32)
        bing = pygame.Color(43, 43, 41)
        boop = pygame.Color(173, 173, 166)

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if bong.collidepoint(pos[0], pos[1]):
                self.qw33 = True
                self.ee44 = False

        color = boop if self.qw33 else bing
        pygame.draw.rect(self.efoiefoi0, color, bong, 0, 4)

        vrr = 0
        brr = 0

        for i, (user, raw_message) in enumerate(self.qqqqqqq):
            i += 1

            if user not in self.user_color_dict:
                self.user_color_dict[user] = random.choice(['aqua', 'aquamarine3', 'blueviolet', 'blue', 'chocolate1', 'crimson', 'gold1', 'green'])

            iuuu = f'{user}: {raw_message}'
            iuuu = [iuuu[i: i + johny] for i in range(0, len(iuuu), johny)]
            for l, line in enumerate(iuuu):
                self.fiue88 = zong.render(line, False, pygame.Color('white'))
                self.efoiefoi0.blit(self.fiue88, (bong.x, 100 + i * shlong + vrr * 8 + l * 8))

            brrr = zong.render(f'{user}:', False, pygame.Color(self.user_color_dict[user]))
            self.efoiefoi0.blit(brrr, (bong.x, 100 + i * shlong + vrr * 8))

            vrr += len(iuuu) - 1
            brr += len(iuuu)
        if brr > gohn:
            self.qqqqqqq = self.qqqqqqq[1:]

        if self.qw33 and not self.ee44:
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if not bong.collidepoint(pos[0], pos[1]):
                    self.ee44 = True
                    self.qw33 = False

            eheh: Sequence[pygame.Key] = pygame.key.get_pressed()
            if eheh[pygame.K_ESCAPE]:
                self.ee44 = True
                self.qw33 = False
            elif eheh[pygame.K_BACKSPACE]:
                self.fyy44 = self.fyy44[:-1]
                self.fghj = [self.fyy44[i: i + johny] for i in range(0, len(self.fyy44), johny)]
            elif eheh[pygame.K_RETURN]:
                if self.fyy44 != r'':
                    self.qqqqqqq.append((player.name, self.fyy44))
                    self.qqq.append((player.name, self.fyy44))
                    self.fyy44 = r''
                    self.fghj = r''
            elif sum([len(line) for line in self.fyy44]) < ghon:
                keys_list = (pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z, pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_QUESTION, pygame.K_EXCLAIM, pygame.K_PERIOD, pygame.K_COMMA, pygame.K_SPACE)
                pressed_keys = [k for k in keys_list if eheh[k]]
                for event in pressed_keys:
                    char = chr(event)
                    if 'a' <= char <= 'z' or 'A' <= char <= 'Z' or char in ' ?!.,' or '0' <= char <= '9':
                        self.fyy44 += char
                        self.fghj = [self.fyy44[i: i + johny] for i in range(0, len(self.fyy44), johny)]

            pygame.draw.rect(self.efoiefoi0, color, bong, 0, 4)
            for l, line in enumerate(self.fghj):
                self.fiue88 = zong.render(line, False, pygame.Color('white'))
                self.efoiefoi0.blit(self.fiue88, (bong.x + 5, bong.y + 5 + l * 8))
            pygame.display.flip()

        player.inputs_disabled = self.qw33

    def show_minimap(self, player):
        x = 128
        y = 72

        # Background
        ahsd = pygame.Rect(x, y, self.efoiefoi0.get_size()[0] - (2 * x), self.efoiefoi0.get_size()[1] - (2 * y))

        # Show image
        map_image = pygame.image.load('../graphics/minimap/map.png').convert_alpha()
        map_rect = map_image.get_rect(center=ahsd.center)
        self.efoiefoi0.blit(map_image, map_rect)

        # Show player head
        head_image = pygame.image.load('../graphics/minimap/head.png').convert_alpha()
        head_rect = head_image.get_rect(center=ahsd.center)
        head_rect.x = x + player.vbvbv.x / 50 - head_rect.height / 2
        head_rect.y = y + player.vbvbv.y / 50 - head_rect.width / 2
        self.efoiefoi0.blit(head_image, head_rect)


class NameTag:
    def __init__(self, player, name):
        self.player = player
        self.name = name

        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(shmop, shling)

        # Initial position
        self.text, self.rect = self.initialize_rect()

        self.kill = False

    def initialize_rect(self):
        text = self.font.render(self.name, False, qweqwe)
        x = self.player.vbvbv.centerx - int(text.get_rect().width / 2)
        y = self.player.vbvbv.top - fopfive

        rect = text.get_rect(topleft=(x, y))

        return text, rect

    def update(self, camera, screen_center):
        x = self.player.vbvbv.centerx - int(self.text.get_rect().width / 2) - camera.x + screen_center.x
        y = self.player.vbvbv.top - fopfive - camera.y + screen_center.y

        self.rect = self.text.get_rect(topleft=(x, y))

    def display(self):
        pygame.draw.rect(self.display_surface, sfdsdfsdf, self.rect.inflate(20, 10))
        self.display_surface.blit(self.text, self.rect)
        pygame.draw.rect(self.display_surface, weoir8, self.rect.inflate(20, 10), 3)
