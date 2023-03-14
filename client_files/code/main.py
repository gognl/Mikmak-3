import socket  # Socket
import hashlib
import sys
import threading

import pygame  # Pygame
from threading import Thread  # Multi-threading
from queue import Queue, Empty  # Multi-threaded sorted queue
from collections import deque  # Normal queue
from struct import pack, unpack  # serialize
from sys import exit

from client_files.code.item import Item
from client_files.code.structures import *
from client_files.code.settings import *
from client_files.code.world import World
from client_files.code.title import Title

server_socket: socket.socket
def initialize_connection(server_addr: (str, int), encrypted_id: bytes) -> (Queue, int):
    global server_socket
    server_socket = socket.socket()
    server_socket.connect(server_addr)

    hello_msg: HelloMsg = HelloMsg(encrypted_id, -1)

    server_socket.send(hello_msg.serialize())
    data = server_socket.recv(6)
    client_id = int.from_bytes(data, 'little')

    # Start the packets-handler thread & initialize the queue
    updates_queue: Queue = Queue()
    pkts_handler: Thread = Thread(target=handle_server_pkts, args=(updates_queue,))
    pkts_handler.start()

    return updates_queue, client_id


get_server_pkt_AllowChanging = True
send_msg_to_server_AllowChanging = True
want_to_change_server = False
amount_server_changes = 0


def send_msg_to_server(msg: NormalServer.Output.StateUpdate):
    """Sends a message to the server (and encrypts it)"""
    while want_to_change_server:
        pass
    global send_msg_to_server_AllowChanging
    send_msg_to_server_AllowChanging = False
    msg.seq = NormalServer.Output.StateUpdate.seq_count
    data: bytes = msg.serialize()
    size: bytes = pack("<H", len(data))
    try:
        server_socket.send(size)
        server_socket.send(data)
        send_msg_to_server_AllowChanging = True
    except socket.error:
        if want_to_change_server:
            send_msg_to_server_AllowChanging = True
        else:
            pygame.quit()
            exit()


def get_server_pkt() -> bytes:
    """
    Gets a packet from the server (and decrypts them...)
    :return: The packet from the server.
    """
    while want_to_change_server:
        pass
    global get_server_pkt_AllowChanging
    get_server_pkt_AllowChanging = False
    try:
        size: int = unpack("<H", server_socket.recv(2))[0]
        data: bytes = server_socket.recv(size)
        get_server_pkt_AllowChanging = True
        return data
    except socket.error:
        if want_to_change_server:
            get_server_pkt_AllowChanging = True
        else:
            pygame.quit()
            exit()


def handle_server_pkts(updates_queue: Queue) -> None:
    """
    Handles the packets which are received from the server, and adds them to the updates priority queue.
    :return: None
    """
    while True:
        # Get a packet from the server; convert it to a NormalServerMessage object.
        data: bytes = get_server_pkt()
        if data == b'':
            print('got empty msg')
            continue

        prefix, ser = data[0], data[1:]
        if prefix == 0:
            msg: NormalServer.Input.StateUpdate = NormalServer.Input.StateUpdate(ser=ser)
            updates_queue.put(msg)
        elif prefix == 1:
            msg: NormalServer.Input.ChangeServerMsg = NormalServer.Input.ChangeServerMsg(ser=ser)
            global want_to_change_server, amount_server_changes
            want_to_change_server = True
            amount_server_changes += 1

            def change_server(amount_changes_now):
                while not (get_server_pkt_AllowChanging and send_msg_to_server_AllowChanging):
                    if amount_changes_now != amount_server_changes:
                        return
                if amount_changes_now == amount_server_changes:
                    global server_socket
                    server_socket.close()
                    server_socket = socket.socket()
                    print(msg.server.addr())
                    server_socket.connect(msg.server.addr())

                    print(msg.src_server_index)
                    hello_msg: HelloMsg = HelloMsg(msg.encrypted_client_id, msg.src_server_index)
                    server_socket.send(hello_msg.serialize())

                    NormalServer.Output.StateUpdate.seq_count = 0

                    global want_to_change_server
                    want_to_change_server = False

            threading.Thread(target=change_server, args=(amount_server_changes,)).start()



def update_game(update_msg: NormalServer.Input.StateUpdate, changes: deque[TickUpdate], client_id: int, world: World) -> None:
    """
    Updates the game according to the update from the server, and the changes made with the inputs received before the updated state.
    :param world: The pygame world.
    :param client_id: The id of this client.
    :param update_msg: The update message fruom the server.
    :param changes: A queue of the changes made to the game since the last call to this function.
    :return: None
    """

    # Reset to the server state
    if None in (update_msg.state_update.player_changes, update_msg.state_update.enemy_changes):
        print(
            f'Returning from update_game():\n\tplayer_changes: {update_msg.state_update.player_changes}\n\tenemy_changes: {update_msg.state_update.enemy_changes}')
        return

    world.interpolator.add_update(update_msg.state_update)

    for player_update in update_msg.state_update.player_changes:
        entity_id: int = player_update.id
        entity_pos: (int, int) = player_update.pos
        entity_status: str = player_update.status

        if entity_id == client_id:
            world.player.update_pos(entity_pos)
            world.player.status = entity_status
            world.player.health = player_update.health
            if entity_status == 'dead':
                world.player.die()  # TODO display death screen
                pygame.quit()
                exit()

    for item_update in update_msg.state_update.item_changes:
        # add it to the items dict if it's not already there
        if item_update.id not in world.items:
            world.items[item_update.id] = Item(item_update.id, item_update.name,
                                               (world.visible_sprites, world.item_sprites), (0, 0), world.item_despawn,
                                               world.item_pickup, world.item_drop, world.item_use)
        # add to its update queue
        world.items[item_update.id].update_queue.extend(item_update.actions)

    # Clear the changes deque; Leave only the changes made after the acknowledged CMD
    while changes and changes[0].seq < update_msg.ack:
        changes.popleft()

    # Apply the changes
    for tick_update in changes:
        player_change: NormalServer.Output.PlayerUpdate = tick_update.player_update
        world.player.update_pos(player_change.pos)
        world.player.status = player_change.status


def initialize_game() -> (pygame.Surface, pygame.time.Clock, World):
    """
    Initializes the game.
    :return: screen, clock, world
    """
    pygame.init()
    f = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(f)
    pygame.display.set_caption("Cows")
    clock = pygame.time.Clock()
    world = World()

    return screen, clock, world


def game_tick(screen: pygame.Surface, clock: pygame.time.Clock, world: World) -> (
        pygame.Surface, pygame.time.Clock, World, TickUpdate, NormalServer.Output.StateUpdate):
    """
    Run game according to user inputs - prediction before getting update from server
    :return: updated screen, clock, and world
    """

    # Wait for one tick
    world.dt = clock.tick(FPS) / 1000

    # Reset screen to black - delete last frame from screen
    screen.fill('black')

    # Update the world state and then the screen
    tick_update: TickUpdate
    state_update: NormalServer.Output.StateUpdate
    tick_update, state_update, msg_lst = world.run()
    pygame.display.update()

    return screen, clock, world, tick_update, state_update, msg_lst


def hash_and_salt(password: str) -> str:
    hasher = hashlib.sha256((SALT + password).encode())
    return hasher.hexdigest()


def run_game(*args) -> None:
    """
    Runs the game.
    :return: None
    """

    # Check for invalid number of arguments; Should be okay to delete this in the final version - TODO
    if len(args) != 3:
        print('you did smth wrong smh')
        return

    # Connection with login
    login_addr: (str, int) = (login_host, login_port)
    login_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Unpack the arguments
    screen: pygame.Surface = args[0]
    clock: pygame.time.Clock = args[1]
    world: World = args[2]

    # Create custom events
    update_required_event = pygame.USEREVENT + 1

    # The changes queue; Push to it data about the changes after every cmd sent to the server
    reported_changes: deque[TickUpdate] = deque()

    # Opening screen loop
    running: bool = True
    title: Title = Title()
    while running:
        # Reset screen to black - delete last frame from screen
        screen.fill('black')

        quit_response, running, username, password = title.run()  # TODO - add ip and port (if needed - @goni?)
        username = username.upper()
        password = password.upper()

        if not running:
            size = 0
            if password != '' and username != '':
                login_socket.connect(login_addr)
                data_to_login = username + " " + hash_and_salt(password)
                login_socket.send(pack("<H", len(data_to_login)))
                login_socket.send(data_to_login.encode())
                size = int.from_bytes(login_socket.recv(2), 'little')

            if size == 0:
                running = True
                title = Title()
                quit_response = False
                login_socket.close()
                login_socket = socket.socket()

        pygame.display.update()

        # Wait for one tick
        clock.tick(FPS)

        if quit_response:
            pygame.quit()

    data = login_socket.recv(size)
    info_to_client: LoginResponseToClient = LoginResponseToClient(ser=data)
    server_addr = info_to_client.server.addr()


    # Initialize the connection with the server
    update_queue: Queue
    client_id: int
    update_queue, client_id = initialize_connection(server_addr, info_to_client.encrypted_client_id)
    world.player.entity_id = client_id
    data_to_client: DataToClient = info_to_client.data_to_client
    world.player.update_pos((data_to_client.pos_x, data_to_client.pos_y))
    world.player.name = username
    world.player.nametag = world.player.create_nametag(world.player, world.player.name)
    world.player.health = data_to_client.health
    world.player.strength = data_to_client.strength
    world.player.resistance = data_to_client.resistance
    world.player.xp = data_to_client.xp
    inventory: dict[str, tuple[list[str], int]] = data_to_client.inventory
    inventory_items: dict[str, InventorySlot] = {}
    for item_name in inventory:
        item_ids, item_count = inventory[item_name]
        if item_count > 0:
            inventory_slot = InventorySlot(item_ids[0])
            for i in range(1, len(item_ids)):
                inventory_slot.add_item(item_ids[0][i])
            inventory_items[item_name] = inventory_slot

    world.player.inventory_items = inventory_items

    # The main game loop
    running: bool = True
    while running:
        for event in pygame.event.get():
            if event.type == update_required_event:
                update_game(event.msg, reported_changes, client_id, world)
            elif event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RSHIFT:
                    running = False

        # Run game according to user inputs - prediction before getting update from server
        tick_update: TickUpdate
        state_update: NormalServer.Output.StateUpdate
        screen, clock, world, tick_update, state_update, msg_lst = game_tick(screen, clock, world)
        if msg_lst:
            chat_msgs_lst: ChatMsgsLst = ChatMsgsLst(msg_lst=msg_lst)
            size = pack('<H', len(chat_msgs_lst.serialize()))
            login_socket.send(size)
            login_socket.send(chat_msgs_lst.serialize())

        size = unpack('<H', login_socket.recv(2))[0]
        chat_msgs_lst_recved = ChatMsgsLst(ser=login_socket.recv(size))
        world.ui.msgs_recv.extend(chat_msgs_lst_recved.msg_lst)

        if state_update is not None:
            send_msg_to_server(state_update)
            NormalServer.Output.StateUpdate.seq_count += 1
        reported_changes.append(tick_update)

        # Check if an update is needed
        if not update_queue.empty():

            # Get the message from the queue
            try:
                update_msg: NormalServer.Input.StateUpdate = update_queue.get_nowait()
            except Empty:
                pass
            else:
                # Post the event

                pygame.event.post(pygame.event.Event(update_required_event, {"msg": update_msg}))

    pygame.quit()

    # Close the game
    close_game(server_socket)


def close_game(server_socket: socket.socket) -> None:
    """Closes the game"""
    server_socket.close()


login_host: str
login_port: int


def main():
    global login_host, login_port
    # login_host, login_port = sys.argv[1], sys.argv[2]
    login_host, login_port = '127.0.0.1', LOGIN_PORT_TO_CLIENT

    # Initialize the game
    screen, clock, world = initialize_game()

    # Run the main game
    run_game(screen, clock, world)


if __name__ == '__main__':
    main()
