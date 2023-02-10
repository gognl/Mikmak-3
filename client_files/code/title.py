import pygame
from client_files.code.settings import *


class Title:
    def __init__(self):
        # General
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(TITLE_FONT, TITLE_FONT_SIZE)
        self.max_length = 14

        # Field values
        self.username = ""
        self.password = ""
        self.running = True
        self.quit = False

        # Mouse
        self.release_mouse = False

        # Box background
        self.box_width = 400
        self.box_height = 350
        self.boxx = int(SCREEN_WIDTH / 2) - int(self.box_width / 2)
        self.boxy = int(SCREEN_HEIGHT / 2) - int(self.box_height / 2)
        self.box = pygame.Rect(self.boxx, self.boxy, self.box_width, self.box_height)

        # Input boxes
        # Username
        self.username_title_text = self.font.render("Username", False, TITLE_TEXT_COLOR)
        self.username_title_text_rect = self.username_title_text.get_rect(topleft=(self.boxx + 50, self.boxy + 50))
        self.username_rect = pygame.Rect(self.boxx + 50, self.boxy + 80, 300, 50)
        self.username_text = None
        self.username_text_rect = None
        # Password
        self.password_title_text = self.font.render("Password", False, TITLE_TEXT_COLOR)
        self.password_title_text_rect = self.password_title_text.get_rect(topleft=(self.boxx + 50, self.boxy + 150))
        self.password_rect = pygame.Rect(self.boxx + 50, self.boxy + 180, 300, 50)
        self.password_text = None
        self.password_text_rect = None

        # Go button
        self.button_rect = pygame.Rect(self.boxx + 145, self.boxy + 270, 100, 50)
        self.button_text = self.font.render("Join", False, BUTTON_TEXT_COLOR)
        self.button_text_rect = self.button_text.get_rect(topleft=(self.boxx + 152, self.boxy + 280))

        # Fields selection
        self.username_selected = False
        self.password_selected = False

    def background(self):
        # Background
        self.display_surface.fill(TITLE_BG_COLOR)  # TODO - add cows and grass

    def display(self):
        self.background()

        # Box
        pygame.draw.rect(self.display_surface, BOX_BG_COLOR, self.box)

        # Username
        self.display_surface.blit(self.username_title_text, self.username_title_text_rect)
        pygame.draw.rect(self.display_surface, INPUT_BG_COLOR, self.username_rect)
        if self.username_selected:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, self.username_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.username_rect, 3)
        self.display_surface.blit(self.username_text, self.username_text_rect)

        # Password
        self.display_surface.blit(self.password_title_text, self.password_title_text_rect)
        pygame.draw.rect(self.display_surface, INPUT_BG_COLOR, self.password_rect)
        if self.password_selected:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, self.password_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.password_rect, 3)
        self.display_surface.blit(self.password_text, self.password_text_rect)

        # Button
        pygame.draw.rect(self.display_surface, BUTTON_BG_COLOR, self.button_rect)
        self.display_surface.blit(self.button_text, self.button_text_rect)

    def mouse(self):
        mouse = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if self.release_mouse and not mouse_click[0]:
            self.release_mouse = False

        if mouse_click[0]:
            if self.username_rect.collidepoint(mouse[0], mouse[1]):
                self.username_selected = True
            else:
                self.username_selected = False

            if self.password_rect.collidepoint(mouse[0], mouse[1]):
                self.password_selected = True
            else:
                self.password_selected = False

            if self.button_rect.collidepoint(mouse[0], mouse[1]):
                self.running = False

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.KEYDOWN:
                if self.username_selected:
                    if event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif len(self.username) < self.max_length:
                        self.username += str(event.unicode)

                if self.password_selected:
                    if event.key == pygame.K_BACKSPACE:
                        self.password = self.password[:-1]
                    elif len(self.password) < self.max_length:
                        self.password += str(event.unicode)

        # Update text on screen
        # Username
        self.username_text = self.font.render(self.username, False, TITLE_TEXT_COLOR)
        self.username_text_rect = self.username_text.get_rect(topleft=(self.boxx + 60, self.boxy + 90))
        # Password
        self.password_text = self.font.render(self.password, False, TITLE_TEXT_COLOR)
        self.password_text_rect = self.password_text.get_rect(topleft=(self.boxx + 60, self.boxy + 190))

    def run(self):
        self.mouse()
        self.input()
        self.display()

        return self.quit, self.running, self.username, self.password
