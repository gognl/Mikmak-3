import pygame
from client_files.code.settings import *


class Title:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(TITLE_FONT, TITLE_FONT_SIZE)

        self.username = ""
        self.password = ""
        self.running = True

        # Box background
        self.box_width = 400
        self.box_height = 350
        self.boxx = int(SCREEN_WIDTH / 2) - int(self.box_width / 2)
        self.boxy = int(SCREEN_HEIGHT / 2) - int(self.box_height / 2)
        self.box = pygame.Rect(self.boxx, self.boxy, self.box_width, self.box_height)

        # Input boxes
        self.username_text = self.font.render("Username", False, TITLE_TEXT_COLOR)
        self.username_text_rect = self.username_text.get_rect(topleft=(self.boxx + 50, self.boxy + 50))
        self.username_rect = pygame.Rect(self.boxx + 50, self.boxy + 80, 300, 50)
        self.password_text = self.font.render("Password", False, TITLE_TEXT_COLOR)
        self.password_text_rect = self.password_text.get_rect(topleft=(self.boxx + 50, self.boxy + 150))
        self.password_rect = pygame.Rect(self.boxx + 50, self.boxy + 180, 300, 50)

        # Go button
        self.button_rect = pygame.Rect(self.boxx + 140, self.boxy + 270, 100, 50)
        self.button_text = self.font.render("Join", False, BUTTON_TEXT_COLOR)
        self.button_text_rect = self.button_text.get_rect(topleft=(self.boxx + 150, self.boxy + 280))

    def display(self):
        # Background
        self.display_surface.fill(TITLE_BG_COLOR)

        # Box
        pygame.draw.rect(self.display_surface, BOX_BG_COLOR, self.box)

        # Username
        self.display_surface.blit(self.username_text, self.username_text_rect)
        pygame.draw.rect(self.display_surface, INPUT_BG_COLOR, self.username_rect)

        # Password
        self.display_surface.blit(self.password_text, self.password_text_rect)
        pygame.draw.rect(self.display_surface, INPUT_BG_COLOR, self.password_rect)

        # Button
        pygame.draw.rect(self.display_surface, BUTTON_BG_COLOR, self.button_rect)
        self.display_surface.blit(self.button_text, self.button_text_rect)

    def run(self):
        self.display()

        return self.running, self.username, self.password
