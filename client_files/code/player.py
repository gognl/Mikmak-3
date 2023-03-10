import random
from collections import deque
from typing import Dict, Sequence, Tuple
from client_files.code.settings import *
from client_files.code.structures import Server, InventorySlot
from client_files.code.support import *
from client_files.code.entity import Entity


class Player(Entity):
    def __init__(self, name, pos, groups, obstacle_sprites, height, create_attack, destroy_attack,
                 create_bullet, create_kettle, create_inventory, destroy_inventory, create_chat,
                 destroy_chat, activate_zen, deactivate_zen, create_minimap, destroy_minimap, create_nametag,
                 nametag_update, get_inventory_box_pressed, create_dropped_item, spawn_enemy_from_egg, entity_id,
                 magnetic_players) -> None:
        super().__init__(groups, entity_id, True, name, create_nametag, nametag_update)

        # Player name TODO: might be temporary
        self.name = name

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
        self.weapon_switch_time = 0
        self.switch_duration_cooldown = 1.5
        # attack sprites
        self.current_weapon = None

        # Animations
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.import_player_assets()
        self.status = 'down'

        # Server
        self.attacks: deque = deque()
        self.item_actions: deque = deque()  # also used as skills update
        self.changes = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.status, 'item_actions': tuple(self.item_actions)}  # Changes made in this tick

        # Stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 0, 'speed': 400}  # TODO - make energy actually do something
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.xp = 0
        self.speed = self.stats['speed']
        self.strength = self.stats['attack']
        self.resistance = 0

        # Nametag
        self.initialize_nametag()

        # Shooting cooldown
        self.can_shoot = True
        self.shoot_time = 0
        self.shoot_cooldown = 1

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
        self.inventory_cooldown: int = 6
        self.last_inventory: bool = True

        # Chat
        self.create_chat = create_chat
        self.destroy_chat = destroy_chat
        self.last_chat = True
        self.chat_time = 0
        self.chat_cooldown = 100
        self.chat_active = False
        self.can_change_chat = True

        # Zen
        self.activate_zen = activate_zen
        self.deactivate_zen = deactivate_zen
        self.last_zen = True
        self.zen_time = 0
        self.zen_cooldown = 100
        self.zen_active = False
        self.can_change_zen = True

        # Minimap
        self.create_minimap = create_minimap
        self.destroy_minimap = destroy_minimap
        self.last_minimap = True
        self.minimap_time = 0
        self.minimap_cooldown = 100
        self.minimap_active = False
        self.can_change_minimap = True

        # Items
        self.item_sprites = None
        self.inventory_items: Dict[str, InventorySlot] = {}
        self.get_inventory_box_pressed = get_inventory_box_pressed
        self.create_dropped_item = create_dropped_item
        self.spawn_enemy_from_egg = spawn_enemy_from_egg

        self.dt = 1

        self.inputs_disabled: bool = False

    def import_player_assets(self) -> None:
        """
        Import all player assets
        :return: None
        """
        path: str = '../graphics/player/'

        self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [],
                           'left_idle': [], 'right_idle': []}
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
            self.item_actions.append(Server.Output.ItemActionUpdate(action_type='skill', item_id=1, item_name=''))

        # Check if using magnet skill
        if self.can_magnet and keys[pygame.K_2]:
            self.can_magnet = False
            self.add(self.magnetic_players)
            self.is_magnet = True
            self.magnet_start = pygame.time.get_ticks()
            self.item_actions.append(Server.Output.ItemActionUpdate(action_type='skill', item_id=2, item_name=''))

        # Move nametag right after moving
        self.nametag_update(self.nametag)

        if keys[pygame.K_e] and not self.zen_active:
            if self.can_change_inventory and not self.last_inventory:
                if not self.inventory_active:
                    self.create_inventory()
                else:
                    self.destroy_inventory()

                self.inventory_active = not self.inventory_active
                self.can_change_inventory = False
            self.last_inventory = True
        else:
            self.last_inventory = False

        if keys[pygame.K_t]:
            if self.can_change_chat and not self.last_chat:
                if not self.chat_active:
                    self.create_chat()
                else:
                    self.destroy_chat()

                self.chat_active = not self.chat_active
                self.can_change_chat = False
                self.chat_time = pygame.time.get_ticks()
            self.last_chat = True
        else:
            self.last_chat = False

        if keys[pygame.K_m]:
            if self.can_change_minimap and not self.last_minimap:
                if not self.minimap_active:
                    self.create_minimap()
                else:
                    self.destroy_minimap()

                self.minimap_active = not self.minimap_active
                self.can_change_minimap = False
                self.minimap_time = pygame.time.get_ticks()
            self.last_minimap = True
        else:
            self.last_minimap = False

        if keys[pygame.K_z]:
            if self.can_change_zen and not self.last_zen:
                if not self.zen_active:
                    self.activate_zen()
                else:
                    self.deactivate_zen()

                self.zen_active = not self.zen_active
                self.can_change_zen = False
                self.zen_time = pygame.time.get_ticks()
            self.last_zen = True
        else:
            self.last_zen = False

        if self.release_mouse[0] and not mouse[0]:
            self.release_mouse[0] = False
        if self.release_mouse[1] and not mouse[2]:
            self.release_mouse[1] = False

        if mouse[0] and not self.attacking and not self.release_mouse[0]:
            if not self.inventory_active or pygame.mouse.get_pos()[0] < SCREEN_WIDTH - INVENTORY_WIDTH:
                if self.weapon_index not in self.on_screen:
                    self.attacks.append(
                        Server.Output.AttackUpdate(weapon_id=self.weapon_index, attack_type=1, direction=(0, 0)))
                    self.create_attack(self)
                    self.attacking = True
                    self.release_mouse[0] = True
                    self.attack_time = pygame.time.get_ticks()
                else:
                    if self.weapon_index == 1:
                        if self.can_shoot:
                            self.create_bullet(self, self.current_weapon.rect.center)
                            self.can_shoot = False
                    elif self.weapon_index == 2:
                        self.attacking = True
                        self.release_mouse[0] = True
                        self.attack_time = pygame.time.get_ticks()

                        self.create_kettle(self, self.current_weapon.rect.center)
                        self.inventory_items['kettle'].count -= 1
                        if self.inventory_items['kettle'].count == 0:
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
                        if self.health > self.stats['health']:
                            self.health = self.stats['health']
                    elif item == "strength":
                        self.strength += 1
                    elif item == "kettle":
                        if self.can_switch_weapon and not self.attacking and self.weapon_index != 2:
                            self.switch_weapon(2)
                        used = False
                    elif item == "shield":
                        self.resistance += 1
                    elif item == "spawn_white":
                        pass  # self.spawn_enemy_from_egg(self, self.rect.topleft, "white_cow")
                    elif item == "spawn_green":
                        pass  # self.spawn_enemy_from_egg(self, self.rect.topleft, "green_cow")
                    elif item == "spawn_red":
                        pass  # self.spawn_enemy_from_egg(self, self.rect.topleft, "red_cow")
                    elif item == "spawn_yellow":
                        pass  # self.spawn_enemy_from_egg(self, self.rect.topleft, "yellow_cow")

                    if used:
                        item_id = self.inventory_items[item].remove_item()
                        self.item_actions.append(Server.Output.ItemActionUpdate(item_name=item, action_type='use', item_id=item_id))

                        if self.inventory_items[item].count == 0:
                            del self.inventory_items[item]

                elif mouse[2] and not self.release_mouse[1]:
                    self.release_mouse[1] = True

                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        for i in range(self.inventory_items[item].count):
                            item_id = self.inventory_items[item].remove_item()
                            self.create_dropped_item(item, (self.rect.centerx, self.rect.centery), item_id)
                            self.item_actions.append(Server.Output.ItemActionUpdate(item_name=item, action_type='drop', item_id=item_id))
                    else:
                        item_id = self.inventory_items[item].remove_item()
                        self.create_dropped_item(item, (self.rect.centerx, self.rect.centery), item_id)
                        self.item_actions.append(Server.Output.ItemActionUpdate(item_name=item, action_type='drop', item_id=item_id))

                    if self.inventory_items[item].count == 0:
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
                self.speed = int(self.speed / self.speed_skill_factor)
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

        if self.attacking:  # TODO - make this based on ticks not time
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                if self.weapon_index not in self.on_screen:
                    self.destroy_attack(self)

        if not self.can_switch_weapon:
            if self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True
                self.weapon_switch_time = 0
            else:
                self.weapon_switch_time += self.dt

        if not self.can_shoot:
            if self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True
                self.shoot_time = 0
            else:
                self.shoot_time += self.dt

        if not self.can_change_inventory:
            if self.inventory_time >= self.inventory_cooldown:
                self.can_change_inventory = True
                self.inventory_time = 0
            else:
                self.inventory_time += 1

        if not self.can_change_chat:
            if current_time - self.chat_time >= self.chat_cooldown:
                self.can_change_chat = True

        if not self.can_change_zen:
            if current_time - self.zen_time >= self.zen_cooldown:
                self.can_change_zen = True

        if not self.can_change_minimap:
            if current_time - self.minimap_time >= self.minimap_cooldown:
                self.can_change_minimap = True

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
        self.item_actions: deque = deque()
        previous_state: dict = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.status,
                                'item_actions': self.item_actions}

        # Get keyboard inputs
        if not self.inputs_disabled:
            self.input()

        # Process cooldowns
        self.cooldowns()

        # Animation
        self.get_status()
        self.animate()

        # Apply keyboard inputs
        self.move(self.speed*self.dt)

        self.changes = {'pos': (self.rect.x, self.rect.y), 'attacks': tuple(self.attacks), 'status': self.status,
                        'item_actions': tuple(self.item_actions)}
        if self.changes == previous_state:
            self.changes = None

    def die(self):

        self.nametag.kill = True
        if self.current_weapon is not None:
            self.current_weapon.kill()
        self.kill()  # TODO - add death screen

    def update_items(self, item_sprites: pygame.sprite.Group) -> None:
        self.item_sprites = item_sprites

    def get_pos(self) -> (int, int):
        """
        Returns the player's position
        """
        return self.rect.x, self.rect.y
