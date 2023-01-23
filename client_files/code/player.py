import pygame
from client_files.code.settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, height, create_attack, destroy_attack) -> None:
        super().__init__(groups)

        # Load player sprite from files
        self.image: pygame.Surface = pygame.image.load('../graphics/player/down_idle/down.png').convert_alpha()

        # Position of player
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)

        # Height of the player on screen - 0 is background
        self.height: int = height

        # Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
        self.hitbox = self.rect.inflate(0, -26)

        # Movement
        # Direction of the player
        self.direction: pygame.Vector2 = pygame.math.Vector2()

        # Speed of the player
        self.speed: int = 10

        # Starting conditions for attacking
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        # Obstacle sprites for the player to check collisions
        self.obstacle_sprites: pygame.Group = obstacle_sprites

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

    def import_player_assets(self) -> None:
        character_path = '../graphics/player/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []}

    def input(self) -> None:
        """
        Get keyboard input and apply it to player direction
        :return: None
        """
        keys: list[pygame.Key] = pygame.key.get_pressed()

        # Movement input

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:  # If no keys are pressed, the direction should reset to 0
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:  # If no keys are pressed, the direction should reset to 0
            self.direction.x = 0

        # attack input
        if keys[pygame.K_SPACE] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            self.create_attack()

        # magic input
        if keys[pygame.K_LCTRL] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            print('magic')

        # change weapon
        if keys[pygame.K_q] and self.can_switch_weapon:
            self.can_switch_weapon = False
            self.weapon_switch_time = pygame.time.get_ticks()
            if self.weapon_index < len(list(weapon_data.keys())) - 1:
                self.weapon_index += 1
            else:
                self.weapon_index = 0
            self.weapon = list(weapon_data.keys())[self.weapon_index]

    def move(self, speed: int) -> None:
        """
        Move the player towards the direction it is going, and apply collision
        :param speed: maximum pixels per direction per frame (may vary if both directions are active)
        :return: None
        """
        # Normalize direction
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')  # Check collisions in the horizontal axis
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')  # Check collisions in the vertical axis
        self.rect.center = self.hitbox.center

    def collision(self, direction: str) -> None:
        """
        Apply collisions to the player, each axis separately
        :param direction: A string representing the direction the player is going
        :return: None
        """
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # Player going right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # Player going left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # Player going down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # Player going up
                        self.hitbox.top = sprite.hitbox.bottom

    def cooldowns(self) -> None:
        """
        Update the timers based on time
        :return: None
        """
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

    def update(self) -> None:
        """
        Update the player based on input
        :return: None
        """
        # Get keyboard inputs
        self.input()
        # Update timers
        self.cooldowns()
        # Apply keyboard inputs
        self.move(self.speed)

    def update_obstacles(self, obstacle_sprites: pygame.sprite.Group) -> None:
        """
        update the obstacle_sprite group
        :return: None
        """
        self.obstacle_sprites = obstacle_sprites
