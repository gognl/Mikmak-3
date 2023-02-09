import pygame
from client_files.code.settings import *


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

	def show_exp(self, exp):
		text_surf = self.font.render(str(int(exp)), False, TEXT_COLOR)
		x = self.display_surface.get_size()[0] - 20
		y = self.display_surface.get_size()[1] - 20
		if self.inventory_active:
			x -= INVENTORY_WIDTH
		text_rect = text_surf.get_rect(bottomright=(x, y))

		pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(20, 20))
		self.display_surface.blit(text_surf, text_rect)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(20, 20), 3)

	def selection_box(self, left, top, has_switched):
		bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
		if has_switched:
			pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
		else:
			pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
		return bg_rect

	def weapon_overlay(self, weapon_index, has_switched):
		# Create weapon box
		bg_rect = self.selection_box(10, 630, has_switched)
		weapon_surf = self.weapon_graphics[weapon_index]
		weapon_rect = weapon_surf.get_rect(center=bg_rect.center)

		self.display_surface.blit(weapon_surf, weapon_rect)

	def show_inventory(self):
		x = self.display_surface.get_size()[0] - INVENTORY_WIDTH
		y = 0

		rect = pygame.Rect(x, y, INVENTORY_WIDTH, self.display_surface.get_size()[1])
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, rect)

	def display(self, player):
		# Creates the bars
		self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
		self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR)
		self.show_exp(player.exp)

		# Create weapon box
		self.weapon_overlay(player.weapon_index, not player.can_switch_weapon)

		# after we add magic
		# Create magic box
		# self.selection_box(93, 630)

		# Inventory
		if self.inventory_active:
			self.show_inventory()

	def create_inventory(self):
		self.inventory_active = True

	def destroy_inventory(self):
		self.inventory_active = False


class NameTag:
	def __init__(self, player):
		self.player = player
		self.name = self.player.name

		self.display_surface = pygame.display.get_surface()
		self.font = pygame.font.Font(UI_FONT, NAMETAG_FONT_SIZE)

		# Initial position
		self.text, self.rect = self.initialize_rect()

	def initialize_rect(self):
		text = self.font.render(self.name, False, TEXT_COLOR)
		x = self.player.rect.centerx - int(text.get_rect().width / 2)
		y = self.player.rect.top - NAMETAG_HEIGHT

		rect = text.get_rect(topleft=(x, y))

		print(text, rect)
		return text, rect

	def update(self, camera, screen_center):
		x = self.player.rect.centerx - int(self.text.get_rect().width / 2) - camera.x + screen_center.x
		y = self.player.rect.top - NAMETAG_HEIGHT - camera.y + screen_center.y

		self.rect = self.text.get_rect(topleft=(x, y))

	def display(self):
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.rect.inflate(20, 10))
		self.display_surface.blit(self.text, self.rect)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.rect.inflate(20, 10), 3)
