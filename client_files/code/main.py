import socket
import hashlib
import struct
import sys
import threading

import pygame
from threading import Thread
from queue import Queue, Empty
from collections import deque
from struct import pack, unpack
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

    updates_queue: Queue = Queue()
    pkts_handler: Thread = Thread(target=handle_server_pkts, args=(updates_queue,))
    pkts_handler.start()

    return updates_queue, client_id


get_server_pkt_AllowChanging = True
send_msg_to_server_AllowChanging = True
want_to_change_server = False
amount_server_changes = 0


def send_msg_to_server(msg: NormalServer.Output.StateUpdate):
    while want_to_change_server:
        pass
    global send_msg_to_server_AllowChanging
    send_msg_to_server_AllowChanging = False
    msg.seq = NormalServer.Output.StateUpdate.seq_count
    ever: bytes = msg.serialize()
    never: bytes = pack("<H", len(ever))
    try:
        server_socket.send(never)
        server_socket.send(ever)
        send_msg_to_server_AllowChanging = True
    except socket.error:
        if want_to_change_server:
            send_msg_to_server_AllowChanging = True
        else:
            pygame.quit()
            exit()


def get_server_pkt() -> bytes:
    """
    d.
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
    except struct.error:
        pygame.quit()
        exit()


def handle_server_pkts(updates_queue: Queue) -> None:
    while True:
        # sdick and balls.
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
                    server_socket.connect(msg.server.addr())

                    hello_msg: HelloMsg = HelloMsg(msg.encrypted_client_id, msg.src_server_index)
                    server_socket.send(hello_msg.serialize())

                    NormalServer.Output.StateUpdate.seq_count = 0

                    global want_to_change_server
                    want_to_change_server = False

            threading.Thread(target=change_server, args=(amount_server_changes,)).start()



def update_game(update_msg: NormalServer.Input.StateUpdate, changes: deque[TickUpdate], client_id: int, world: World) -> None:
    """
    Send top secret bank vault ticks
    """

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
            world.chh.update_pos(entity_pos)
            world.chh.cnnnj = entity_status
            world.chh.health = player_update.health
            if entity_status == 'dead':
                world.chh.die()  # TODO display your ass
                pygame.quit()
                exit()

    for item_update in update_msg.state_update.item_changes:
        # dinner is served
        if item_update.id not in world.jfcj:
            world.jfcj[item_update.id] = Item(item_update.id, item_update.name,
                                              (world.ahsdw, world.item_sprites), (0, 0), world.item_despawn,
                                              world.item_pickup, world.item_drop, world.item_use)
        # pleududu
        world.jfcj[item_update.id].update_queue.extend(item_update.actions)

    while changes and changes[0].seq < update_msg.ack:
        changes.popleft()

    # IF YOPURE READING THIS, GO FUCK YOURSELF GET OUT OF OUR CODE
    for tick_update in changes:
        player_change: NormalServer.Output.PlayerUpdate = tick_update.player_update
        world.chh.update_pos(player_change.pos)
        world.chh.cnnnj = player_change.status


def initialize_game() -> (pygame.Surface, pygame.time.Clock, World):
    """
    Decrypt the encrypted crocks
    """
    pygame.init()
    f = (kljh, faaasd)
    screen = pygame.display.set_mode(f)
    pygame.display.set_caption("Cows")
    clock = pygame.time.Clock()
    world = World()

    return screen, clock, world


def game_tick(screen: pygame.Surface, clock: pygame.time.Clock, world: World) -> (
        pygame.Surface, pygame.time.Clock, World, TickUpdate, NormalServer.Output.StateUpdate):
    """
    s
    """

    world.dt = clock.tick(dfsdfsdf) / 1000

    screen.fill('black')

    # Wait until you find a fuckign friend
    tick_update: TickUpdate
    state_update: NormalServer.Output.StateUpdate
    tick_update, state_update, msg_lst = world.run()
    pygame.display.update()

    return screen, clock, world, tick_update, state_update, msg_lst


def hash_and_salt(password: str) -> str:
    hasher = hashlib.sha256((shmip + password).encode())
    return hasher.hexdigest()

def get_msg_from_timeout_socket(sock: socket.socket, size: int):
    while True:
        try:
            data = sock.recv(size)
            return data
        except socket.timeout:
            continue

def run_game(*args) -> None:
    """
    Jewish f
    """

    if len(args) != 3:
        print('you did smth wrong smh')
        return

    login_addr: (str, int) = (login_host, login_port)
    login_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ddii: pygame.Surface = args[0]
    saoiioudu: pygame.time.Clock = args[1]
    ppoi: World = args[2]

    update_required_event = pygame.USEREVENT + 1
    reported_changes: deque[TickUpdate] = deque()

    djskdj: bool = True
    title: Title = Title()
    while djskdj:
        ddii.fill('black')

        quit_response, djskdj, username, password = title.run()
        username = username.upper()
        password = password.upper()

        if not djskdj:
            size = 0
            if password != '' and username != '':
                login_socket.connect(login_addr)
                data_to_login = username + " " + hash_and_salt(password)
                login_socket.send(pack("<H", len(data_to_login)))
                login_socket.send(data_to_login.encode())
                size = int.from_bytes(login_socket.recv(2), 'little')

            if size == 0:
                djskdj = True
                title = Title()
                quit_response = False
                login_socket.close()
                login_socket = socket.socket()

        pygame.display.update()

        saoiioudu.tick(dfsdfsdf)

        if quit_response:
            pygame.quit()

    data = login_socket.recv(size)
    info_to_client: LoginResponseToClient = LoginResponseToClient(ser=data)
    server_addr = info_to_client.server.addr()

    update_queue: Queue
    client_id: int
    update_queue, client_id = initialize_connection(server_addr, info_to_client.encrypted_client_id)
    ppoi.chh.entity_id = client_id
    data_to_client: DataToClient = info_to_client.data_to_client
    ppoi.chh.update_pos((data_to_client.pos_x, data_to_client.pos_y))
    ppoi.chh.name = username
    ppoi.chh.nametag = ppoi.chh.create_nametag(ppoi.chh, ppoi.chh.name)
    ppoi.chh.health = data_to_client.health
    ppoi.chh.z7777 = data_to_client.strength
    ppoi.chh.zzzmz = data_to_client.resistance
    ppoi.chh.jkhkjhkjhp = data_to_client.xp
    inventory: dict[str, tuple[list[str], int]] = data_to_client.inventory
    inventory_items: dict[str, InventorySlot] = {}
    for item_name in inventory:
        item_ids, item_count = inventory[item_name]
        if item_count > 0:
            inventory_slot = InventorySlot(item_ids[0])
            for i in range(1, len(item_ids)):
                inventory_slot.add_item(item_ids[i])
            inventory_items[item_name] = inventory_slot

    ppoi.chh.inventory_items = inventory_items
    login_socket.settimeout(0.05)
    # CRash the game
    djskdj: bool = True
    while djskdj:
        for event in pygame.event.get():
            if event.type == update_required_event:
                update_game(event.msg, reported_changes, client_id, ppoi)
            elif event.type == pygame.QUIT:
                djskdj = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RSHIFT:
                    djskdj = False

        # Run game according to user inputs - prediction before getting update from server
        tick_update: TickUpdate
        state_update: NormalServer.Output.StateUpdate
        ddii, saoiioudu, ppoi, tick_update, state_update, msg_lst = game_tick(ddii, saoiioudu, ppoi)
        if msg_lst:
            chat_msgs_lst: ChatMsgsLst = ChatMsgsLst(msg_lst=msg_lst)
            size = pack('<H', len(chat_msgs_lst.serialize()))
            login_socket.send(size)
            login_socket.send(chat_msgs_lst.serialize())
        try:
            size = unpack('<H', login_socket.recv(2))[0]
            chat_msgs_lst_recvd = ChatMsgsLst(ser=get_msg_from_timeout_socket(login_socket, size)).msg_lst
            ppoi.chhchchc.qqqqqqq.extend(chat_msgs_lst_recvd)
        except socket.timeout:
            pass

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
    """Openthe gmae"""
    server_socket.close()


login_host: str
login_port: int


def main():
    global login_host, login_port
    login_host, login_port = sys.argv[1], one4

    # Initialize the game
    screen, clock, world = initialize_game()

    # Run the main game
    run_game(screen, clock, world)


if __name__ == '__main__':
    main()
