import random
from collections import deque
from typing import Dict, Sequence
from client_files.code.settings import *
from client_files.code.structures import Server
from client_files.code.support import *
from client_files.code.entity import Entity


class Player(Entity):
    def __init__(self, name, pos, groups, obstacle_sprites, height, create_attack, destroy_attack,
                 create_bullet, create_kettle, create_inventory, destroy_inventory, create_nametag,
                 nametag_update, get_inventory_box_pressed, create_dropped_item, spawn_enemy_from_egg,
                 entity_id, magnetic_players) -> None:
        super().__init__(groups, entity_id, True, name, create_nametag, nametag_update)

        # sprite group of magnetic players
        self.magnetic_players = magnetic_players

        # Load player sprite from files
        self.image: pygame.Surface = pygame.image.load('../graphics/player/down_idle/down.png').convert_alpha()

        # Position of player
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)

        # Height of the player on screen - 0 is background
        self.height: int = height

        # Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
        self.hitbox = self.rect.inflate(-20, -26)

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
        # attack sprites
        self.current_weapon = None

        # Animations
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.import_player_assets()
        self.status = 'down'

        # Server
        self.changes = {'pos': (self.rect.x, self.rect.y), 'attacking': self.attacking, 'weapon': self.weapon, 'status': self.status}  # Changes made in this tick
        self.attacks: deque = deque()

        # Stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'speed': 10}  # TODO - make energy actually do something
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.xp = 0
        self.speed = self.stats['speed']
        self.strength = self.stats['attack']
        self.resistance = 0  # TODO - make this stat actually matter and change the damage amount, MAKE ATTACKING THE PLAYER MAKE THIS GO DOWN SLIGHTLY

        # Nametag
        self.initialize_nametag()

        # Shooting cooldown
        self.can_shoot = True
        self.shoot_time = None
        self.shoot_cooldown = 400

        # Mouse press
        self.release_mouse = [False, False]

        # Magnet skill
        self.can_magnet = True
        self.is_magnet = False
        self.magnet_start = None
        self.magnet_time = 10000
        self.magnet_skill_cooldown = 50000

        # Speed skill
        self.can_speed = True
        self.is_fast = False
        self.speed_start = None
        self.speed_time = 1000
        self.speed_skill_cooldown = 8000
        self.speed_skill_factor = 2

        # Inventory
        self.create_inventory = create_inventory
        self.destroy_inventory = destroy_inventory
        self.inventory_active: bool = False
        self.can_change_inventory: bool = True
        self.inventory_time: int = 0
        self.inventory_cooldown: int = 100
        self.last_inventory: bool = True

        # Items
        self.item_sprites = None
        self.inventory_items = {}
        self.get_inventory_box_pressed = get_inventory_box_pressed
        self.create_dropped_item = create_dropped_item
        self.spawn_enemy_from_egg = spawn_enemy_from_egg
        self.pets = 0

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

        keys: Sequence[pygame.Key] = pygame.key.get_pressed()
        mouse: Sequence[bool] = pygame.mouse.get_pressed()

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

        # Check if using speed skill
        if self.can_speed and keys[pygame.K_1]:
            self.can_speed = False
            self.is_fast = True
            self.speed *= self.speed_skill_factor
            self.speed_start = pygame.time.get_ticks()

        # Check if using magnet skill
        if self.can_magnet and keys[pygame.K_2]:
            self.can_magnet = False
            self.add(self.magnetic_players)
            self.is_magnet = True
            print("here")
            self.magnet_start = pygame.time.get_ticks()

        # Move nametag right after moving
        self.nametag_update(self.nametag)

        if keys[pygame.K_e]:
            if self.can_change_inventory and not self.last_inventory:
                if not self.inventory_active:
                    self.create_inventory()
                else:
                    self.destroy_inventory()

                self.inventory_active = not self.inventory_active
                self.can_change_inventory = False
                self.inventory_time = pygame.time.get_ticks()
            self.last_inventory = True
        else:
            self.last_inventory = False

        if self.release_mouse[0] and not mouse[0]:
            self.release_mouse[0] = False
        if self.release_mouse[1] and not mouse[2]:
            self.release_mouse[1] = False

        if mouse[0] and not self.attacking and not self.release_mouse[0]:
            if not self.inventory_active or pygame.mouse.get_pos()[0] < SCREEN_WIDTH - INVENTORY_WIDTH:
                if self.weapon_index not in self.on_screen:
                    self.attacks.append(Server.Output.AttackUpdate(weapon_id=self.weapon_index, attack_type=1, direction=(0, 0)))
                    self.create_attack(self)
                    self.attacking = True
                    self.release_mouse[0] = True
                    self.attack_time = pygame.time.get_ticks()
                else:
                    if self.weapon_index == 1:
                        if self.can_shoot:
                            self.create_bullet(self)
                            self.can_shoot = False
                            self.shoot_time = pygame.time.get_ticks()
                    elif self.weapon_index == 2:
                        self.attacking = True
                        self.release_mouse[0] = True
                        self.attack_time = pygame.time.get_ticks()

                        self.create_kettle(self)
                        self.inventory_items['kettle'] -= 1
                        if self.inventory_items['kettle'] == 0:
                            del self.inventory_items['kettle']

                        if 'kettle' not in self.inventory_items:
                            self.switch_weapon()

        if self.inventory_active and pygame.mouse.get_pos()[0] > SCREEN_WIDTH - INVENTORY_WIDTH:
            mouse_pos = pygame.mouse.get_pos()
            box = self.get_inventory_box_pressed(mouse_pos)

            if box is not None and box < len(self.inventory_items):
                item = list(self.inventory_items.keys())[box]

                if mouse[0] and not self.release_mouse[0]:
                    self.release_mouse[0] = True
                    used = True

                    if item == "heal":
                        self.health += 20
                        if self.health > 100:
                            self.health = 100
                    elif item == "strength":
                        self.strength += 1
                    elif item == "kettle":
                        if self.can_switch_weapon and not self.attacking and self.weapon_index != 2:
                            self.switch_weapon(2)
                        used = False
                    elif item == "shield":
                        self.resistance += 1
                    elif item == "spawn_white":
                        self.spawn_enemy_from_egg(self, self.rect.topleft, "white_cow")
                    elif item == "spawn_green":
                        self.spawn_enemy_from_egg(self, self.rect.topleft, "green_cow")
                    elif item == "spawn_red":
                        self.spawn_enemy_from_egg(self, self.rect.topleft, "red_cow")
                    elif item == "spawn_pet":
                        if self.pets < MAX_PETS_PER_PLAYER:
                            self.spawn_enemy_from_egg(self, self.rect.topleft, "pet_cow", is_pet=True)
                            self.pets += 1
                        else:
                            used = False

                    if used:
                        self.inventory_items[item] -= 1

                        if self.inventory_items[item] == 0:
                            del self.inventory_items[item]

                elif mouse[2] and not self.release_mouse[1]:
                    self.release_mouse[1] = True

                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        for i in range(self.inventory_items[item]):
                            self.create_dropped_item(item, (self.rect.centerx, self.rect.centery))
                        self.inventory_items[item] = 0
                    else:
                        self.create_dropped_item(item, (self.rect.centerx, self.rect.centery))
                        self.inventory_items[item] -= 1

                    if self.inventory_items[item] == 0:
                        if item == "kettle" and self.weapon_index == 2:
                            self.switch_weapon()
                        del self.inventory_items[item]

        if keys[pygame.K_q] and self.can_switch_weapon and not self.attacking:
            self.switch_weapon()

    def switch_weapon(self, known_index=None) -> None:
        """
        switch current held weapon
        :return:
        """
        self.release_mouse[0] = True

        if self.weapon_index in self.on_screen:
            self.destroy_attack(self)

        self.can_switch_weapon = False
        self.weapon_switch_time = pygame.time.get_ticks()

        if known_index is None:
            if self.weapon_index < len(list(weapon_data.keys())) - 1:
                self.weapon_index += 1
            else:
                self.weapon_index = 0
        else:
            self.weapon_index = known_index
        self.weapon = list(weapon_data.keys())[self.weapon_index]

        self.attacking = False

        if self.weapon_index in self.on_screen:
            self.create_attack(self)

        self.attacks.append(Server.Output.AttackUpdate(weapon_id=self.weapon_index, attack_type=0, direction=(0, 0)))

        # if switched to kettle and have no kettle, reswitch
        if self.weapon_index == 2 and 'kettle' not in self.inventory_items:
            self.switch_weapon()

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

        # Speed skill timers
        if not self.can_speed:
            if current_time - self.speed_start >= self.speed_time and self.is_fast:
                self.speed /= self.speed_skill_factor
                self.is_fast = False
            if current_time - self.speed_start >= self.speed_skill_cooldown:
                self.can_speed = True

        # Magnet skill timers
        if not self.can_magnet:
            if current_time - self.magnet_start >= self.magnet_time and self.is_magnet:
                self.is_magnet = False
                self.remove(self.magnetic_players)
            if current_time - self.magnet_start >= self.magnet_skill_cooldown:
                self.can_magnet = True

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                if self.weapon_index not in self.on_screen:
                    self.destroy_attack(self)

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_shoot:
            if current_time - self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True

        if not self.can_change_inventory:
            if current_time - self.inventory_time >= self.inventory_cooldown:
                self.can_change_inventory = True

    def animate(self) -> None:
        """
        animate through images
        :return: None
        """
        animation: List[pygame.Surface] = self.animations[self.status]

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
        self.attacks: deque = deque()
        previous_state: dict = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.status}

        # Get keyboard inputs
        self.input()

        # Process cooldowns
        self.cooldowns()

        # Animation
        self.get_status()
        self.animate()

        # Apply keyboard inputs
        self.move(self.speed)

        # Pick up items
        self.item_collision()

        self.changes = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.status}
        if self.changes == previous_state:
            self.changes = None

        # Death
        if self.health <= 0:
            for item in list(self.inventory_items.keys()):
                for i in range(self.inventory_items[item]):
                    self.create_dropped_item(item, self.rect.center)
            self.inventory_items = {}

            for i in range(self.xp):
                self.create_dropped_item("xp", self.rect.center)
            self.xp = 0

            self.create_dropped_item("grave_player", self.rect.center)

            self.nametag.kill = True
            self.kill()  # TODO - add death screen

    def update_obstacles(self, obstacle_sprites: pygame.sprite.Group) -> None:
        """
        update the obstacle_sprite group
        :return: None
        """
        self.obstacle_sprites = obstacle_sprites

    def update_items(self, item_sprites: pygame.sprite.Group) -> None:
        self.item_sprites = item_sprites

    def get_pos(self) -> (int, int):
        """
        Returns the player's position
        """
        return self.rect.x, self.rect.y

    def item_collision(self):
        for item in self.item_sprites:
            if self.rect.colliderect(item.rect):
                if item.can_pick_up:
                    if item.name == "xp":
                        self.xp += 1
                        item.kill()
                    elif item.name == "grave_player" or item.name == "grave_pet":
                        if len(self.inventory_items) < INVENTORY_ITEMS:
                            self.inventory_items[item.name + f'({len(self.inventory_items)})'] = 1
                            item.kill()
                    else:
                        if item.name in list(self.inventory_items.keys()):
                            self.inventory_items[item.name] += 1
                            item.kill()
                        elif len(self.inventory_items) < INVENTORY_ITEMS:
                            self.inventory_items[item.name] = 1
                            item.kill()
