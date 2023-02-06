import pygame
from client_files.code.settings import *
from client_files.code.support import *
from client_files.code.entity import Entity


class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, height, create_attack, destroy_attack, create_bullet, create_kettle, entity_id) -> None:
        super().__init__(groups, entity_id)

        # Load player sprite from files
        self.image: pygame.Surface = pygame.image.load('../graphics/player/down_idle/down.png').convert_alpha()

        # Position of player
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)

        # Height of the player on screen - 0 is background
        self.height: int = height

        # Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
        self.hitbox = self.rect.inflate(-20, -26)

        # Speed of the player
        self.speed: int = 10

        # Obstacle sprites for the player to check collisions
        self.obstacle_sprites: pygame.Group = obstacle_sprites

        # Attacking
        self.attacking: bool = False
        self.attack_cooldown: int = 400
        self.attack_time: int = 0

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.create_bullet = create_bullet
        self.create_kettle = create_kettle
        self.weapon_index = 0
        self.on_screen = [1, 2]  # Indices of weapons that stay on screen
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 400

        # Animations
        self.animations: dict[str: list[pygame.Surface]] = {}
        self.import_player_assets()
        self.status = 'down'

        # Server
        self.changes = {'pos': (self.rect.x, self.rect.y), 'attacking': self.attacking, 'weapon': self.weapon, 'status': self.status}  # Changes made in this tick

        # Stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 10}
        self.health = self.stats['health'] * 0.5
        self.energy = self.stats['energy'] * 0.8
        self.exp = 123
        # Speed of the player
        self.speed = self.stats['speed']

        # Shooting cooldown
        self.can_shoot = True
        self.shoot_time = None
        self.shoot_cooldown = 200

        # Mouse press
        self.release_mouse = False

    def import_player_assets(self) -> None:
        """
        Import all player assets
        :return: None
        """
        path: str = '../graphics/player/'

        self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': []}
        for animation in self.animations.keys():
            self.animations[animation] = list(import_folder(path + animation).values())

    def input(self) -> None:
        """
        Get keyboard input and process it
        :return: None
        """
        keys: list[pygame.Key] = pygame.key.get_pressed()
        mouse: list[bool] = pygame.mouse.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'down'
        else:  # If no keys are pressed, the direction should reset to 0
            self.direction.y = 0

        if keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        else:  # If no keys are pressed, the direction should reset to 0
            self.direction.x = 0

        if self.release_mouse and not mouse[0]:
            self.release_mouse = False

        if mouse[0] and not self.attacking and not self.release_mouse:
            if self.weapon_index not in self.on_screen:
                self.create_attack()
                self.attacking = True
                self.release_mouse = True
                self.attack_time = pygame.time.get_ticks()
            else:
                if self.weapon_index == 1:
                    if self.can_shoot:
                        self.create_bullet()
                        self.can_shoot = False
                        self.shoot_time = pygame.time.get_ticks()
                elif self.weapon_index == 2:
                    self.create_kettle()
                    self.switch_weapon()

        if keys[pygame.K_q] and self.can_switch_weapon and not self.attacking:
            self.switch_weapon()

    def switch_weapon(self) -> None:
        """
        switch current held weapon
        :return:
        """
        self.release_mouse = True

        if self.weapon_index in self.on_screen:
            self.destroy_attack()

        self.can_switch_weapon = False
        self.weapon_switch_time = pygame.time.get_ticks()
        if self.weapon_index < len(list(weapon_data.keys())) - 1:
            self.weapon_index += 1
        else:
            self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]

        self.attacking = False

        if self.weapon_index in self.on_screen:
            self.create_attack()

    def get_status(self) -> None:
        """
        update player status
        :return: None
        """

        # idle
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status:
                self.status += '_idle'

    def cooldowns(self) -> None:
        """
        Manage cooldowns
        :return: None
        """
        current_time: int = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown and self.weapon_index not in self.on_screen:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_shoot:
            if current_time - self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True

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

    def update(self) -> None:
        """
        Update the player based on input
        :return: None
        """

        # Clear the changes dict
        previous_state: dict = {'pos': (self.rect.x, self.rect.y), 'attacking': self.attacking, 'weapon': self.weapon, 'status': self.status}

        # Get keyboard inputs
        self.input()

        # Process cooldowns
        self.cooldowns()

        # Animation
        self.get_status()
        self.animate()

        # Apply keyboard inputs

        self.move(self.speed)

        self.changes = {'pos': (self.rect.x, self.rect.y), 'attacking': self.attacking, 'weapon': self.weapon, 'status': self.status}
        if self.changes == previous_state:
            self.changes = None

    def update_obstacles(self, obstacle_sprites: pygame.sprite.Group) -> None:
        """
        update the obstacle_sprite group
        :return: None
        """
        self.obstacle_sprites = obstacle_sprites

    def get_pos(self) -> (int, int):
        """
        Returns the player's position
        """
        return self.rect.x, self.rect.y
