from typing import Sequence
import pygame
from client_files.code.settings import *
from client_files.code.item import Item


class UI:
    def __init__(self):
        # General
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # Bar setup
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10, 35, ENERGY_BAR_WIDTH, BAR_HEIGHT)

        # Convert weapon dictionary
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            path = weapon['graphic']
            weapon = pygame.image.load(path).convert_alpha()
            self.weapon_graphics.append(weapon)

        # Inventory
        self.inventory_active: bool = False
        self.boxes: list[list[int]] = []
        self.box_size = 64
        self.box_starting_position = (self.display_surface.get_size()[0] - INVENTORY_WIDTH + 48, 190)
        self.boxes_distance = 10
        self.setup_inventory()

        # Inventory UI
        self.inventory_ui_starting_position = (self.display_surface.get_size()[0] - INVENTORY_WIDTH + 48, 48)

        # Chat
        self.chat_active: bool = False

        # Minimap
        self.minimap_active = False

        # Mouse
        self.release_mouse: bool = False

    def show_bar(self, current, max_amount, bg_rect, color):
        # Draw background
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # Converting stat to pixel
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # Drawing the bar
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_xp(self, xp):
        text_surf = self.font.render(str(int(xp)), False, TEXT_COLOR)
        x = self.display_surface.get_size()[0] - 20
        y = self.display_surface.get_size()[1] - 20
        if self.inventory_active:
            x -= INVENTORY_WIDTH
        text_rect = text_surf.get_rect(bottomright=(x, y))

        star = pygame.image.load('../graphics/items/xp.png').convert_alpha()
        star_rect = star.get_rect(center=text_rect.center)
        star_rect.x -= 45

        # bg, text, star, border
        j = pygame.Rect.union(text_rect.inflate(20, 20), star_rect.inflate(10, 0))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, j)
        self.display_surface.blit(text_surf, text_rect)
        self.display_surface.blit(star, star_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, j, 3)

    def selection_box(self, left, top, has_switched):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if has_switched:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def weapon_overlay(self, weapon_index, has_switched, inventory_items):
        # Create weapon box
        bg_rect = self.selection_box(10, 630, has_switched)
        weapon_surf = self.weapon_graphics[weapon_index]
        weapon_rect = weapon_surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(weapon_surf, weapon_rect)

        if weapon_index == 2:
            item_amount = inventory_items['kettle']
            if item_amount > 1:
                font = pygame.font.Font(UI_FONT, INVENTORY_FONT_SIZE)
                item_text = font.render(f'{item_amount}', False, TEXT_COLOR)
                item_text_rect = item_text.get_rect(bottomright=(bg_rect.bottomright[0] - 4, bg_rect.bottomright[1] - 4))
                self.display_surface.blit(item_text, item_text_rect)

    def setup_inventory(self):
        for y in range(INVENTORY_SIZE[1]):
            row = []
            for x in range(INVENTORY_SIZE[0]):
                row.append(pygame.Rect(self.box_starting_position[0] + (self.box_size + self.boxes_distance) * x,
                                       self.box_starting_position[1] + (self.box_size + self.boxes_distance) * y,
                                       self.box_size, self.box_size))
            self.boxes.append(row)

    def show_inventory(self, player, inventory_items):
        x = self.display_surface.get_size()[0] - INVENTORY_WIDTH
        y = 0

        # Background
        rect = pygame.Rect(x, y, INVENTORY_WIDTH, self.display_surface.get_size()[1])
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, rect)

        # UI
        text = [f'{player.name}',
                f'',
                f'Health     - {player.health}',
                f'Speed      - {player.speed}',
                f'Strength   - {player.strength}',
                f'Resistance - {player.resistance}']

        for i, entry in enumerate(text):
            inventory_ui_text = self.font.render(entry, False, TITLE_TEXT_COLOR)
            inventory_ui_text_rect = inventory_ui_text.get_rect(topleft=(self.inventory_ui_starting_position[0], self.inventory_ui_starting_position[1] + i * 20))

            self.display_surface.blit(inventory_ui_text, inventory_ui_text_rect)

        # Boxes
        for y, row in enumerate(self.boxes):
            for x in range(len(row)):
                rect = self.boxes[y][x]
                pygame.draw.rect(self.display_surface, UI_BG_COLOR, rect)
                pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, rect, 3)

                number = y * INVENTORY_SIZE[0] + x
                if len(inventory_items) > number:
                    item_name = list(inventory_items)[number]
                    item_amount = inventory_items[item_name].count

                    item = Item(-1, item_name, (), rect.center)
                    self.display_surface.blit(item.image, item.rect)

                    if item_amount > 1:
                        font = pygame.font.Font(UI_FONT, INVENTORY_FONT_SIZE)
                        item_text = font.render(f'{item_amount}', False, TEXT_COLOR)
                        item_text_rect = item_text.get_rect(bottomright=(rect.bottomright[0] - 2, rect.bottomright[1] - 2))
                        self.display_surface.blit(item_text, item_text_rect)

    def get_inventory_box_pressed(self, mouse):
        for y, row in enumerate(self.boxes):
            for x, box in enumerate(row):
                if box.collidepoint(mouse):
                    return y * INVENTORY_SIZE[0] + x

        return None

    def display(self, player):
        # Creates the bars
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR)
        self.show_xp(player.xp)

        # Create weapon box
        self.weapon_overlay(player.weapon_index, not player.can_switch_weapon, player.inventory_items)

        # Inventory
        if self.inventory_active:
            self.show_inventory(player, player.inventory_items)

        if self.chat_active:
            self.show_chat()

        if self.minimap_active:
            self.show_minimap(player)

    def create_inventory(self):
        self.inventory_active = True

    def destroy_inventory(self):
        self.inventory_active = False

    def create_chat(self):
        self.chat_active = True

    def destroy_chat(self):
        self.chat_active = False

    def create_minimap(self):
        self.minimap_active = True

    def destroy_minimap(self):
        self.minimap_active = False

    def show_chat(self):
        x = 10
        y = 95

        # Background
        transparent = pygame.Surface((CHAT_WIDTH, CHAT_HEIGHT))
        transparent.set_alpha(128)
        transparent.fill(UI_BG_COLOR)
        self.display_surface.blit(transparent, (x, y))

    def show_minimap(self, player):
        x = 128
        y = 72

        # Background
        rect = pygame.Rect(x, y, self.display_surface.get_size()[0] - (2 * x), self.display_surface.get_size()[1] - (2 * y))

        # Show image
        map_image = pygame.image.load('../graphics/minimap/map.png').convert_alpha()
        map_rect = map_image.get_rect(center=rect.center)
        self.display_surface.blit(map_image, map_rect)

        # Show player head
        head_image = pygame.image.load('../graphics/minimap/head.png').convert_alpha()
        head_rect = head_image.get_rect(center=rect.center)
        head_rect.x = x + player.rect.x/50 - head_rect.height/2
        head_rect.y = y + player.rect.y/50 - head_rect.width/2
        self.display_surface.blit(head_image, head_rect)


class NameTag:
    def __init__(self, player, name):
        self.player = player
        self.name = name

        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, NAMETAG_FONT_SIZE)

        # Initial position
        self.text, self.rect = self.initialize_rect()

        self.kill = False

    def initialize_rect(self):
        text = self.font.render(self.name, False, TEXT_COLOR)
        x = self.player.rect.centerx - int(text.get_rect().width / 2)
        y = self.player.rect.top - NAMETAG_HEIGHT

        rect = text.get_rect(topleft=(x, y))

        return text, rect

    def update(self, camera, screen_center):
        x = self.player.rect.centerx - int(self.text.get_rect().width / 2) - camera.x + screen_center.x
        y = self.player.rect.top - NAMETAG_HEIGHT - camera.y + screen_center.y

        self.rect = self.text.get_rect(topleft=(x, y))

    def display(self):
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.rect.inflate(20, 10))
        self.display_surface.blit(self.text, self.rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.rect.inflate(20, 10), 3)
