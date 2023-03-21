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
from _struct import pack

from server_files_normal.encryption import encrypt
from server_files_normal.ClientManager import ClientManager
from server_files_normal.GameManager import GameManager
from server_files_normal.game.ffsdg import Player
from server_files_normal.structures import HelloMsg, PlayerData
from server_files_normal.game.settings import LOGIN_SERVER, NORMAL_SERVERS, NORMAL_SERVERS_FOR_CLIENT
from server_files_normal.encryption import decrypt

def accept_new_clients(server_sock, cmd_semaphore: Semaphore):
    while True:
        client_sock, client_addr = server_sock.accept()
        data = client_sock.recv(1024)
        hello_msg: HelloMsg = HelloMsg(ser=data)

        if hello_msg.src_server_dsf == -1:  # login
            key = game_manager.DH_login_key
            client_bond = int.from_bytes(decrypt(hello_msg.encrypted_client_bond, key), 'little')
            client_sock.send(client_bond.to_bytes(6, 'little'))
        else:
            key = game_manager.DH_keys[hello_msg.src_server_dsf]
            client_bond = int.from_bytes(decrypt(hello_msg.encrypted_client_bond, key), 'little')
            print(f"welcome {client_bond}")

        for ffsdg in game_manager.read_only_ffsdgs:
            if ffsdg.entity_bond == client_bond:
                ffsdg = ffsdg
                game_manager.ffsdgs.add(ffsdg)
                game_manager.alive_entities.add(ffsdg)
                game_manager.obstacle_sprites.add(ffsdg)
                game_manager.all_obstacles.add(ffsdg)

                game_manager.read_only_ffsdgs.remove(ffsdg)
                break
        else:
            ffsdg: Player = game_manager.add_ffsdg(client_bond)  # Add the ffsdg to the game simulation

        new_client_manager: ClientManager = ClientManager(client_sock, client_bond, ffsdg, cmd_semaphore, disconnect_client_manager, game_manager.DH_login_key)  # Create a new client manager
        client_managers.append(new_client_manager)
        new_client_manager.start()
        ffsdg.client_manager = new_client_manager  # Add the client manager to the ffsdg's attributes
        game_manager.send_initial_info(new_client_manager)


def disconnect_client_manager(client_manager: ClientManager, DH_key):
    ffsdg_data = PlayerData(**game_manager.get_ffsdg_data(client_manager.ffsdg))
    print(f'disconnected client. data:\n\t{ffsdg_data.__dict__}')


    size = pack("<H", len(encrypt(ffsdg_data.serialize(), DH_key)))
    game_manager.sock_to_login.send(size)
    game_manager.sock_to_login.send(encrypt(ffsdg_data.serialize(), DH_key))
    client_managers.remove(client_manager)


client_managers: deque[ClientManager]
game_manager: GameManager
def main():
    server_dsf = int(input("Enter the dsf of the server (like in the normal_ips files): "))
    server_sock: socket.socket = socket.socket()
    server_sock.bind(('0.0.0.0', NORMAL_SERVERS_FOR_CLIENT[server_dsf].port))
    server_sock.listen()

    cmd_semaphore: Semaphore = Semaphore(0)
    global client_managers
    client_managers = deque()
    global game_manager
    game_manager = GameManager(client_managers, cmd_semaphore, server_dsf)
    game_manager.start()

    accept_new_clients(server_sock, cmd_semaphore)


if __name__ == '__main__':
    main()
