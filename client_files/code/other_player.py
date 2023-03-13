from collections import deque
from typing import Union

from client_files.code.entity import Entity
from client_files.code.explosion import Explosion
from client_files.code.settings import weapon_data, LIGHTNING_RADIUS
from client_files.code.structures import NormalServer
from client_files.code.support import *

class OtherPlayer(Entity):
    def __init__(self, pos, groups, entity_id, obstacle_sprites, create_attack, destroy_attack,
                 create_bullet, create_kettle, create_dropped_item, visible_sprites):
        super().__init__(groups, entity_id)

        self.status = None
        self.sprite_type = 'enemy'

        # graphics setup
        self.import_graphics()
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.height = 2

        # Tile hitbox - shrink the original hitbox in the vertical axis for tile overlap
        self.hitbox = self.rect.inflate(-20, -26)
        self.obstacle_sprites = obstacle_sprites

        self.enemy_name = 'other_player'

        # violence
        self.attacking: bool = False
        self.attack_cooldown: int = 0.5
        self.attack_time: int = 0

        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.create_bullet = create_bullet
        self.create_kettle = create_kettle
        self.weapon_index = 0
        self.on_screen = (1, 2)  # Indices of weapons that stay on screen
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.current_weapon = None

        # updates queue
        self.update_queue: deque = deque()

        # Stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'speed': 10}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.max_energy = self.stats['energy']
        self.xp = 0
        self.speed = self.stats['speed']
        self.strength = self.stats['attack']
        self.resistance = 0

        self.create_dropped_item = create_dropped_item

        self.visible_sprites = visible_sprites

        self.dt = 1

        self.is_magnet = False
        self.magnet_start = 0
        self.magnet_time = 10

        self.is_fast = False
        self.speed_start = 0
        self.speed_time = 3

    def import_graphics(self):
        path: str = '../graphics/player/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [],
                            'left_idle': [], 'right_idle': []}
        for animation in self.animations.keys():
            self.animations[animation] = list(import_folder(path + animation).values())

        speed_path: str = '../graphics/player_speed/'
        self.speed_animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [],
                                 'left_idle': [], 'right_idle': []}
        for speed_animation in self.speed_animations.keys():
            self.speed_animations[speed_animation] = list(import_folder(speed_path + speed_animation).values())

        self.status = 'down_idle'

    def animate(self) -> None:
        """
        animate through images
        :return: None
        """
        if self.is_fast:
            animation: List[pygame.Surface] = self.speed_animations[self.status]
        else:
            animation: List[pygame.Surface] = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def process_server_update(self, update: NormalServer.Input.PlayerUpdate) -> Union[str, None]:
        self.status = update.status

        if update.status == 'dead':
            self.xp = 0
            if self.current_weapon is not None:
                self.current_weapon.kill()
            Explosion(self.rect.center, 0, (self.visible_sprites,), pygame.sprite.Group(), speed=1.26, radius=50)
            self.kill()
            return 'dead'

        if not self.attacking:
            for attack in update.attacks:
                if attack.attack_type == 0:  # switch
                    if self.weapon_index in self.on_screen:
                        self.destroy_attack(self)
                    self.weapon_index = attack.weapon_id
                    self.weapon = list(weapon_data.keys())[self.weapon_index]
                    self.attacking = False
                    if self.weapon_index in self.on_screen:
                        self.create_attack(self)
                elif attack.attack_type == 1:  # attack
                    if self.weapon_index not in self.on_screen:
                        self.create_attack(self)
                        self.attacking = True
                    else:
                        if self.weapon_index == 1:
                            self.create_bullet(self, self.current_weapon.rect.center, attack.direction)
                        elif self.weapon_index == 2:
                            self.create_kettle(self, self.current_weapon.rect.center, attack.direction)

        for attack in update.attacks:
            if attack.attack_type == 2:
                Explosion(self.rect.center, 0, (self.visible_sprites,), pygame.sprite.Group(), speed=1.26,
                          radius=LIGHTNING_RADIUS, color='blue')
            elif attack.attack_type == 3:
                self.is_magnet = True
                self.magnet_start = 0
                Explosion(self.rect.center, 0, (self.visible_sprites,), pygame.sprite.Group(), speed=1.05, radius=40, color='gray', player=self)
            elif attack.attack_type == 4:
                self.is_fast = True
                self.speed_start = 0

        self.update_pos(update.pos)

    def update(self):

        # inputs
        while self.update_queue:
            if self.process_server_update(self.update_queue.popleft()) == 'dead':
                return

        self.cooldowns()
        self.animate()

    def cooldowns(self):
        if self.attacking:
            if self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.attack_time = 0
                if self.weapon_index not in self.on_screen:
                    self.destroy_attack(self)
            else:
                self.attack_time += self.dt

        # Magnet skill timers
        if self.is_magnet:
            if self.magnet_start >= self.magnet_time:
                self.is_magnet = False
            else:
                self.magnet_start += self.dt

        # Speed skill timers
        if self.is_fast:
            if self.speed_start >= self.speed_time:
                self.is_fast = False
            else:
                self.speed_start += self.dt
