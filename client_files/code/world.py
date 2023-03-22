import random
from typing import Dict, Union, List

from client_files.code.interpolator import Interpolator
from client_files.code.other_player import OtherPlayer
from client_files.code.tile import Tile
from client_files.code.support import *
from client_files.code.weapon import Weapon
from client_files.code.enemy import Enemy
from client_files.code.projectile import Projectile
from client_files.code.ui import *
from client_files.code.structures import *
from client_files.code.explosion import *


class World:
    def __init__(self) -> None:
        # d
        self.sdjfhfjkh: pygame.Surface = pygame.display.get_surface()

        # asdf
        self.whhtht = pygame.sprite.Group()

        #  ttt
        self.ahsdw: GroupYSort = GroupYSort()
        self.sdaujjdsa: pygame.sprite.Group = pygame.sprite.Group()
        self.ii2i2: pygame.sprite.Group = pygame.sprite.Group()  # BAlls
        self.dhh: pygame.sprite.Group = pygame.sprite.Group()
        self.projectile_sprites: pygame.sprite.Group = pygame.sprite.Group()

        self.item_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.nametags: List[NameTag] = []

        self.chhchchc = UI()

        self.dhdhd: int = self.sdjfhfjkh.get_size()[0] // 2
        self.hhhdhdh: int = self.sdjfhfjkh.get_size()[1] // 2
        self.asjkd: pygame.math.Vector2 = pygame.math.Vector2(self.dhdhd, self.hhhdhdh)

        self.ioue897er8: pygame.math.Vector2 = pygame.math.Vector2()
        self.hdhbvbv: list[int, int] = list(andthis)

        self.chh: Player = None

        self.enemies: Dict[int, Enemy] = {}
        self.other_players: Dict[int, OtherPlayer] = {}

        self.jfcj: Dict[int, Item] = {}

        self.all_players: List[Union[Player, OtherPlayer]] = []

        self.layout: Dict[str, List[List[str]]] = {
            'floor': import_csv_layout('../graphics/map/map_Ground.csv'),
            'objects': import_csv_layout('../graphics/map/map_Objects.csv'),
            'boundary': import_csv_layout('../graphics/map/map_Barriers.csv'),
        }

        self.graphics: dict[str: dict[int: pygame.Surface]] = {
            'floor': import_folder('../graphics/tiles'),
            'objects': import_folder('../graphics/objects')
        }

        self.aois()

        self.zen_active = False

        self.interpolator: Interpolator = Interpolator(self)

        self.dt = 0

    def aois(self) -> None:
        """
        Collide with all near by gonis
        """
        # Create player with starting position

        # Random player starting position generator
        while True:
            random_x = random.randint(0, 1280 * 40 // 64 - 1)
            random_y = random.randint(0, 720 * 40 // 64 - 1)
            if int(self.layout['floor'][random_y][random_x]) in onetwo and int(self.layout['objects'][random_y][random_x]) == -1:
                sudud = (random_x * 64, random_y * 64)
                break
        sudud = (25000, 800)
        self.chh = Player("gognl", sudud, (self.ahsdw, self.sdaujjdsa, self.dhh, self.ii2i2),
                          self.ii2i2, 1, self.uasud8, self.salildiu87, self.iouoiu98787,
                          self.dh3h, self.dhhcnb, self.shaduh22, self.asjdhjh22u7yu2, self.saiodiju23,
                          self.asouiduh2, self.aslkdj, self.askljdhh2, self.kjsadhjkdh2, self.jgfkjg,
                          self.issdf, self.what, self.hvjhvjh, self.asd,
                          0, self.whhtht, self.layout, self.sdfajdopasdffasd, self.dsfsfd)  # TODO - make starting player position random (or a spawn)

        self.all_players.append(self.chh)

        # Center camera
        self.ioue897er8.x = self.chh.rect.centerx
        self.ioue897er8.y = self.chh.rect.centery

    def uasud8(self, player: Union[Player, OtherPlayer]) -> None:
        player.current_weapon = Weapon(player, (self.ahsdw,), self.sdaujjdsa, 3)

    def salildiu87(self, player: Union[Player, OtherPlayer]):
        if player.current_weapon:
            player.current_weapon.kill()
        player.current_weapon = None

    def iouoiu98787(self, source: Union[Player, OtherPlayer, Enemy], pos, mouse=None):
        if isinstance(source, Player):
            mouse = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse[0], mouse[1]) - (source.rect.center - self.ioue897er8 + self.asjkd)
            source.attacks.append(NormalServer.Output.AttackUpdate(weapon_id=source.oi3u, attack_type=1, direction=tuple([int(i) for i in direction])))
        elif isinstance(source, Enemy):
            direction = pygame.math.Vector2(mouse[0] - source.vbvbv.center[0], mouse[1] - source.vbvbv.center[1])
        else:
            direction = pygame.math.Vector2(mouse)

        if not isinstance(source, Enemy):
            damage = int(one12['nerf']['damage'] + (0.1 * source.z7777))
        else:
            damage = source.g7akhjsdbkajs

        Projectile(source, pos, direction, (self.ahsdw, self.sdaujjdsa,
                                            self.projectile_sprites), self.ii2i2, 4, 500, 5,
                   '../graphics/weapons/bullet.png', damage)

    def dh3h(self, player: Union[Player, OtherPlayer], pos, mouse=None):
        if isinstance(player, Player):
            mouse = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse[0], mouse[1]) - (player.rect.center - self.ioue897er8 + self.asjkd)
            player.attacks.append(NormalServer.Output.AttackUpdate(weapon_id=player.oi3u, attack_type=1, direction=tuple([int(i) for i in direction])))
        else:
            direction = pygame.math.Vector2(mouse)
        Projectile(player, pos, direction, (self.ahsdw, self.sdaujjdsa,
                                            self.projectile_sprites), self.ii2i2, 4, 75, 3,
                   '../graphics/weapons/kettle/full.png', int(one12['kettle']['damage'] + (0.1 * player.z7777)),
                   'explode', self.create_explosion, True)

    def dhhcnb(self):
        self.chhchchc.create_inventory()
        self.asjkd.x = self.dhdhd - int(tontwo / 2)
        self.hdhbvbv[0] = int(self.hdhbvbv[0] / 2)

    def shaduh22(self):
        self.chhchchc.destroy_inventory()
        self.asjkd.x = self.dhdhd
        self.hdhbvbv = list(andthis)

    def asjdhjh22u7yu2(self):
        self.chhchchc.create_chat()

    def saiodiju23(self):
        self.chhchchc.destroy_chat()

    def asouiduh2(self):
        self.zen_active = True

    def aslkdj(self):
        self.zen_active = False

    def askljdhh2(self):
        self.chhchchc.create_minimap()

    def kjsadhjkdh2(self):
        self.chhchchc.destroy_minimap()

    def jgfkjg(self, player, name):
        nametag = NameTag(player, name)
        self.nametags.append(nametag)

        return nametag

    def hvjhvjh(self, name, pos, item_id):
        self.jfcj[item_id] = Item(item_id, name, (self.ahsdw, self.item_sprites), pos, self.item_despawn, self.item_pickup, self.item_drop, self.item_use)

    def issdf(self, nametag):
        nametag.update(self.ioue897er8, self.asjkd)

    def what(self, mouse):
        return self.chhchchc.get_inventory_box_pressed(mouse)

    def asd(self, pos, name):
        while True:
            random_x = pos[0] // 64 + (random.randint(2, 4) * random.randrange(-1, 2))
            random_y = pos[1] // 64 + (random.randint(2, 4) * random.randrange(-1, 2))

            if int(self.layout['floor'][random_y][random_x]) in onetwo and int(self.layout['objects'][random_y][random_x]) == -1:
                Enemy(name, (random_x * 64, random_y * 64), (self.ahsdw, self.sdaujjdsa), 1,
                      self.sdaujjdsa, self.hvjhvjh, self.create_explosion, self.iouoiu98787)
                break

    def dsfsfd(self):
        Explosion(self.chh.rect.center, 0, (self.ahsdw,), pygame.sprite.Group(), oiwequioiu=1.05, vbfhfhbv=40, vmncslk='gray', player=self.chh)

    def sdfajdopasdffasd(self):
        Explosion(self.chh.rect.center, 0, (self.ahsdw,), pygame.sprite.Group(), oiwequioiu=1.26, vbfhfhbv=yy, vmncslk='blue')

    def create_explosion(self, pos, damage):
        Explosion(pos, damage, (self.ahsdw,), self.ahsdw)

    def kill_enemy(self, enemy: Enemy):
        Explosion(enemy.vbvbv.center, 0, (self.ahsdw,), pygame.sprite.Group(), oiwequioiu=1.26, vbfhfhbv=50)
        del self.enemies[enemy.entity_id]
        enemy.kill()

    def run(self) -> (TickUpdate, NormalServer.Output.StateUpdate):
        """
            10/10 function would recommend
            """

        # Run the interpolation
        self.interpolator.interpolate()

        # Update the camera position
        self.update_camera()

        # Calculate played tile
        player_tile: pygame.math.Vector2 = pygame.math.Vector2(int(self.chh.rect.x / osahkjfgaohf),
                                                               int(self.chh.rect.y / osahkjfgaohf))

        # Create and display all visible sprites
        for style_index, (style, layout) in enumerate(self.layout.items()):
            for row_index in range(int(player_tile.y - goingon),
                                   int(player_tile.y + goingon)):
                if 0 <= row_index < andthat:
                    row = layout[row_index]
                    for col_index in range(int(player_tile.x - rayn),
                                           int(player_tile.x + rayn)):
                        if 0 <= col_index < whatis:
                            col = row[col_index]
                            if col != '-1':  # -1 in csv means no tile, don't need to recreate the tile if it already exists
                                x: int = col_index * osahkjfgaohf
                                y: int = row_index * osahkjfgaohf

                                if style == 'floor':
                                    surface: pygame.Surface = self.graphics['floor'][col]
                                    Tile((x, y), (self.ahsdw,), 'floor', col in onetwo, 0, surface)
                                elif style == 'objects':
                                    surface: pygame.Surface = self.graphics['objects'][col]
                                    Tile((x, y), (self.ahsdw, self.sdaujjdsa, self.ii2i2), 'object', False, 1,
                                         surface)
                                elif style == 'boundary':
                                    Tile((x, y), (self.sdaujjdsa, self.ii2i2), 'barrier', False)

        # Display all visible sprites
        self.ahsdw.custom_draw(self.ioue897er8, self.asjkd)

        # Update the obstacle sprites for the player
        self.chh.update_items(self.item_sprites)

        self.chh.oooa = self.dt
        for proj in self.projectile_sprites.sprites():
            proj.dt = self.dt
        for player in self.other_players.values():
            player.dt = self.dt

        # UI
        for nametag in self.nametags:
            if nametag.kill:
                del nametag
            else:
                nametag.display()
        if not self.zen_active:
            self.chhchchc.display(self.chh)

        # Run update() function in all visible sprites' classes
        self.ahsdw.update()

        # Delete all tiles
        for sprite in self.ahsdw.sprites() + self.sdaujjdsa.sprites():
            if type(sprite) is Tile:
                sprite.kill()

        # Get info about changes made in this tick (used for server synchronization)
        if self.chh.changes is None:
            return None, None  # no changes
        player_changes = NormalServer.Output.PlayerUpdate(id=self.chh.entity_id, changes=self.chh.changes)
        state_update: NormalServer.Output.StateUpdate = NormalServer.Output.StateUpdate(player_changes=player_changes)  # sent to server
        tick_update: TickUpdate = TickUpdate(player_changes)  # kept for synchronization

        messages = self.chhchchc.qqq.copy()
        self.chhchchc.qqq.clear()
        return tick_update, state_update, messages

    def update_camera(self) -> None:
        # Figure out offset based on camera position

        # X axis
        if abs(self.chh.rect.centerx - self.ioue897er8.x) > self.hdhbvbv[0]:  # If the camera is too far from the player
            if self.chh.rect.centerx > self.ioue897er8.x:  # Move the camera from to the left of the bound if it's further left than the player
                self.ioue897er8.x = self.chh.rect.centerx - self.hdhbvbv[0]
            else:  # Move the camera from to the right of the bound if it's further right than the player
                self.ioue897er8.x = self.chh.rect.centerx + self.hdhbvbv[0]

        # Y axis
        if abs(self.chh.rect.centery - self.ioue897er8.y) > self.hdhbvbv[1]:  # If the camera is too far from the player
            if self.chh.rect.centery > self.ioue897er8.y:  # Move the camera from to the top of the bound if it's further up than the player
                self.ioue897er8.y = self.chh.rect.centery - self.hdhbvbv[1]
            else:  # Move the camera from to the bottom of the bound if it's further down than the player
                self.ioue897er8.y = self.chh.rect.centery + self.hdhbvbv[1]

    def spawn_enemies(self, amount: int) -> None:
        for enemy in range(amount):
            while True:
                random_x = random.randint(0, 1280 * 40 // 64 - 1)
                random_y = random.randint(0, 720 * 40 // 64 - 1)
                name = list(johnny.keys())[int(random.randint(1, 3))]  # Don't include other_player or pets

                if int(self.layout['floor'][random_y][random_x]) in onetwo and int(self.layout['objects'][random_y][random_x]) == -1:
                    Enemy(name, (random_x * 64, random_y * 64), (self.ahsdw, self.sdaujjdsa), 1,
                          self.sdaujjdsa, self.hvjhvjh, self.create_explosion, self.iouoiu98787)
                    break

    def item_despawn(self, item: Item):
        item.kill()

    def item_pickup(self, item: Item, player_id: int) -> None:
        # other players' inventories don't matter to this client
        if self.chh.entity_id != player_id:
            del self.jfcj[item.item_id]
            item.kill()
            return

        if item.name == "xp":
            self.chh.jkhkjhkjhp += 1
            item.kill()
        elif item.name == "grave_player":
            self.chh.inventory_items[item.name + f'({len(self.chh.inventory_items)})'] = InventorySlot(item.item_id)
            del self.jfcj[item.item_id]
            item.kill()
        else:
            if item.name in self.chh.inventory_items:
                self.chh.inventory_items[item.name].add_item(item.item_id)
                del self.jfcj[item.item_id]
                item.kill()
            else:
                self.chh.inventory_items[item.name] = InventorySlot(item.item_id)
                del self.jfcj[item.item_id]
                item.kill()

    def item_drop(self, item: Item, player_id: int, pos: (int, int)) -> None:
        """d"""
        if player_id == self.chh.entity_id:
            return  # already dropped
        self.hvjhvjh(item.name, pos, item.item_id)

    def item_use(self, item: Item, player_id: int, pos: (int, int)) -> None:
        """calculate the sqatre rtoot of two"""


class GroupYSort(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def custom_draw(self, camera: pygame.math.Vector2, screen_center: pygame.math.Vector2) -> None:
        """c
        """
        # For every visible sprite, from top to bottom
        for sprite in sorted(self.sprites(), key=lambda x: (x.sasdoiojasdojio, x.vbvbv.centery)):
            # Display the sprite on screen, moving it by the calculated offset
            self.display_surface.blit(sprite.fhhhf, sprite.vbvbv.topleft - camera + screen_center)
