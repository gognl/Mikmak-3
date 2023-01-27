import socket  # Socket
import pygame  # Pygame
from threading import Thread  # Multi-threading
from queue import Queue, Empty  # Multi-threaded sorted queue
from collections import deque  # Normal queue
from client_files.code.structures import StateUpdateMsg, ServerOutputMsg  # Some custom structures
from client_files.code.settings import *
from client_files.code.world import World

MULTIPLAYER = False

def initialize_connection(server_addr: (str, int)) -> (socket.socket, Queue, int):
    """
    Initializes the connection to the server, and starts the packets-handler thread.
    :param server_ip: The address of the server.
    :return: A tuple containing the server socket, updates queue and the id of the client.
    """

    # Create the socket - TODO
    server_socket: socket.socket = socket.socket()  # CHANGE LATER - TODO
    server_socket.connect(server_addr)

    # Establish some synchronization stuff - TODO
    client_id: int = int(server_socket.recv(5)[3:])  # id_<2 bytes>
    print(f'client {client_id} connected')

    # Start the packets-handler thread & initialize the queue
    updates_queue: Queue = Queue()
    pkts_handler: Thread = Thread(target=handle_server_pkts, args=(server_socket, updates_queue))
    pkts_handler.start()

    return server_socket, updates_queue, client_id

def send_msg_to_server(server_socket:socket.socket, msg: ServerOutputMsg):
    """Sends a message to the server (and encrypts it)"""
    data: bytes = msg.serialize()
    # TODO encrypt here
    server_socket.send(data)

def get_server_pkt(server_socket: socket.socket) -> bytes:  # TODO
    """
    Gets a packet from the server (and decrypts them...)
    :return: The packet from the server.
    """
    data: bytes = server_socket.recv(1024)
    # TODO decrypt here
    return data


def handle_server_pkts(server_socket: socket.socket, updates_queue: Queue) -> None:
    """
    Handles the packets which are received from the server, and adds them to the updates priority queue.
    :return: None
    """
    while True:
        # Get a packet from the server; convert it to a ServerMessage object.
        msg: StateUpdateMsg = StateUpdateMsg(ser=get_server_pkt(server_socket))
        updates_queue.put(msg)


def update_game(update_msg: StateUpdateMsg, changes: deque, client_id: int, world: World) -> None:
    """
    Updates the game according to the update from the server, and the changes made with the inputs received before the updated state.
    :param world: The pygame world.
    :param client_id: The id of this client.
    :param update_msg: The update message from the server.
    :param changes: A queue of the changes made to the game since the last call to this function.
    :return: None
    """

    # Update the game according to the update + changes since its ack (and remove them from the queue) - TODO
    for entity_update in update_msg.changes:
        entity_id: int = entity_update[0]
        entity_pos: (int, int) = entity_update[1]

        if entity_id == client_id:  # don't update self for now
            continue


def initialize_game() -> (pygame.Surface, pygame.time.Clock, World):
    """
    Initializes the game.
    :return: screen, clock
    """
    pygame.init()
    f = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(f)
    pygame.display.set_caption("Cows")
    clock = pygame.time.Clock()
    world = World()

    return screen, clock, world


def game_tick(screen: pygame.Surface, clock: pygame.time.Clock, world: World) -> (pygame.Surface, pygame.time.Clock, World):
    """
    Run game according to user inputs - prediction before getting update from server
    :return: updated screen, clock, and world
    """

    # Reset screen to black - delete last frame from screen
    screen.fill('black')

    # Update the world state and then the screen
    world.run()
    pygame.display.update()

    # Wait for one tick
    clock.tick(FPS)

    return screen, clock, world


def run_game(*args) -> None:  # TODO
    """
    Runs the game.
    :return: None
    """

    # Check for invalid number of arguments; Should be okay to delete this in the final version - TODO
    if len(args) != 6:
        print('you did smth wrong smh')
        return

    # Unpack the arguments
    server_socket: socket.socket = args[0]
    screen: pygame.Surface = args[1]
    clock: pygame.time.Clock = args[2]
    world: World = args[3]
    update_queue: Queue = args[4]
    client_id: int = args[5]

    # Create custom events
    update_required_event = pygame.USEREVENT + 1

    # The changes queue; Push to it data about the changes after every cmd sent to the server
    changes_queue: deque = deque()

    # The main game loop
    running: bool = True
    while running:
        for event in pygame.event.get():
            if event.type == update_required_event:
                update_game(event.msg, changes_queue, client_id, world)
            elif event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False

        previous_player_pos: (int, int) = world.player.get_pos()

        # Run game according to user inputs - prediction before getting update from server
        screen, clock, world = game_tick(screen, clock, world)

        # update the server
        new_player_pos: (int, int) = world.player.get_pos()
        if new_player_pos != previous_player_pos:
            send_msg_to_server(server_socket, ServerOutputMsg(new_pos=new_player_pos))

        # Check if an update is needed
        if not update_queue.empty():

            # Get the message from the queue
            try:
                update_msg: StateUpdateMsg = update_queue.get_nowait()
            except Empty:
                continue

            # Post the event
            pygame.event.post(pygame.event.Event(update_required_event, {"msg": update_msg}))

    pygame.quit()

    return None


def close_game(server_socket: socket.socket) -> None:
    """Closes the game"""
    server_socket.close()


def main():
    server_addr: (str, int) = ('127.0.0.1', 34863)  # TEMPORARY

    # Initialize the game
    screen, clock, world = initialize_game()

    # Initialize the connection with the server
    server_socket: socket.socket
    updates_queue: Queue
    client_id: int
    server_socket, updates_queue, client_id = initialize_connection(server_addr)

    # Run the main game
    run_game(server_socket, screen, clock, world, updates_queue, client_id)

    # Close the game
    close_game(server_socket)


if __name__ == '__main__':
    main()
