from collections import deque
from typing import Union
from time import time_ns

from client_files.code.enemy import Enemy
from client_files.code.item import Item
from client_files.code.other_player import OtherPlayer
from client_files.code.settings import INTERPOLATION_PERIOD
from client_files.code.structures import Server

class Interpolator:
    def __init__(self, world):
        self.updates_queue: deque[Server.Input.StateUpdateNoAck] = deque()
        self.current_state: Union[Server.Input.StateUpdateNoAck, None] = None
        self.current_target: Union[Server.Input.StateUpdateNoAck, None] = None
        self.start_time: int = 0
        self.world = world

    def add_update(self, update: Server.Input.StateUpdateNoAck):
        self.updates_queue.append(update)

    def interpolate(self):

        # return if less than 2 updates, else continue and start interpolating
        if self.current_target is None:
            if len(self.updates_queue) >= 2:
                if self.current_state is None:
                    self.current_state = self.updates_queue.popleft()
                self.current_target = self.updates_queue.popleft()
                self.start_time = time_ns()
            else:
                return

        current_time = time_ns()
        time_part = (current_time-self.start_time)/INTERPOLATION_PERIOD
        if not 0 <= time_part <= 1:
            print(f'reset, {time_part}')
            self.current_state = self.current_target
            self.current_target = None
            return  # TODO tp to final pos

        print(f'no reset, {time_part}')

        interpolated_state: Server.Input.StateUpdateNoAck = self.create_interpolated_state(self.current_state, self.current_target, time_part)

        for player_update in interpolated_state.player_changes:
            if player_update.id == self.world.player.entity_id:
                continue
            entity_id: int = player_update.id
            entity_pos: (int, int) = player_update.pos
            if entity_id in self.world.other_players:
                self.world.other_players[entity_id].update_queue.append(player_update)

            else:
                self.world.other_players[entity_id] = OtherPlayer(entity_pos, (
                    self.world.visible_sprites, self.world.obstacle_sprites, self.world.all_obstacles), entity_id,
                                                             self.world.obstacle_sprites, self.world.create_attack,
                                                             self.world.destroy_attack, self.world.create_bullet,
                                                             self.world.create_kettle, self.world.create_dropped_item)
                self.world.all_players.append(self.world.other_players[entity_id])

        for enemy_update in interpolated_state.enemy_changes:
            entity_id: int = enemy_update.id
            entity_pos: (int, int) = enemy_update.pos
            enemy_name: str = enemy_update.type
            if entity_id in self.world.enemies:
                self.world.enemies[entity_id].update_queue.append(enemy_update)
            else:
                self.world.enemies[entity_id] = Enemy(enemy_name, entity_pos,
                                                 (self.world.visible_sprites, self.world.server_sprites, self.world.all_obstacles),
                                                 entity_id, self.world.all_obstacles, self.world.create_explosion,
                                                 self.world.create_bullet, self.world.kill_enemy)
                self.world.enemies[entity_id].update_queue.append(enemy_update)

        for item_update in interpolated_state.item_changes:
            # add it to the items dict if it's not already there
            if item_update.id not in self.world.items:
                print('creating item')
                self.world.items[item_update.id] = Item(item_update.id, item_update.name,
                                                   (self.world.visible_sprites, self.world.item_sprites), (0, 0), self.world.item_despawn,
                                                   self.world.item_pickup, self.world.item_drop, self.world.item_use)
            # add to its update queue
            self.world.items[item_update.id].update_queue.extend(item_update.actions)

    def create_interpolated_state(self,
                                  start: Server.Input.StateUpdateNoAck,
                                  end: Server.Input.StateUpdateNoAck,
                                  part: float) -> Server.Input.StateUpdateNoAck:
        """
        Calculates the state of each relevant entity in this time part.
        :param start: The state in the beginning
        :param end: The state in the end
        :param part: The time part
        :return: The new interpolated state
        """
        return start  # TODO change this so it works correctly




