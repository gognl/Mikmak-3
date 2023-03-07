"""
SERVER STRUCTURE:

Each manager "lives" in its own thread. ClientManager has multiple instances, depending on the number of clients.

- LoadBalancerManager - responsible for communication with the lb server. Updates some lists, which contain
                        information about movement of entities and clients to and from the server's region.

TODO:
- ClientManager - responsible for communication with the client. Updates a list (deque) that contains client inputs, and
                  sends the game state to the client if needed.
- GameManager - responsible for running the game, with the inputs it gets from the ClientManagers
- main - responsible for accepting new clients, managing the managers (shutting down client threads if their clients
         left the region x seconds ago).
"""

import socket
from collections import deque
from threading import Semaphore

from server_files_normal.LoadBalancerManager import LoadBalancerManager
from server_files_normal.ClientManager import ClientManager
from server_files_normal.GameManager import GameManager
from server_files_normal.game.player import Player
from server_files_normal.structures import Login


def accept_new_clients(server_sock, cmd_semaphore: Semaphore):
    client_id: int = 0
    while True:
        client_sock, client_addr = server_sock.accept()

        # TODO change this later, maybe to a ConnectionInitialization structure
        client_sock.send(f'id_{client_id}'.encode())

        player: Player = game_manager.add_player(client_id)  # Add the player to the game simulation
        new_client_manager: ClientManager = ClientManager(client_sock, client_id, player, cmd_semaphore, disconnect_client_manager)  # Create a new client manager
        client_managers.append(new_client_manager)
        new_client_manager.start()
        player.client_manager = new_client_manager  # Add the client manager to the player's attributes
        game_manager.send_initial_info(new_client_manager) # TODO: ugh?

        client_id += 1

def disconnect_client_manager(client_manager: ClientManager):
    player_data = Login.Output.PlayerData(**game_manager.get_player_data(client_manager.player))
    print(f'disconnected client. data:\n\t{player_data.__dict__}')
    # TODO send to login @bar
    client_managers.remove(client_manager)


client_managers: deque[ClientManager]
game_manager: GameManager
def main():
    server_sock: socket.socket = socket.socket()
    server_sock.bind(('0.0.0.0', 34861))
    server_sock.listen()

    cmd_semaphore: Semaphore = Semaphore(0)
    global client_managers
    client_managers = deque()
    global game_manager
    game_manager = GameManager(client_managers, cmd_semaphore, 1)
    game_manager.start()

    accept_new_clients(server_sock, cmd_semaphore)


if __name__ == '__main__':
    main()
