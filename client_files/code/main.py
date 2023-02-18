import socket  # Socket

import pygame  # Pygame
from threading import Thread  # Multi-threading
from queue import Queue, Empty  # Multi-threaded sorted queue
from collections import deque  # Normal queue
from struct import pack, unpack  # serialize

from client_files.code.structures import *
from client_files.code.settings import *
from client_files.code.world import World
from client_files.code.enemy import Enemy
from client_files.code.title import Title
from client_files.code.other_player import OtherPlayer
from client_files.code.circle import Circle

def initialize_connection(server_addr: (str, int)) -> (socket.socket, Queue, int):
	"""
	Initializes the connection to the server, and starts the packets-handler thread.
	:param server_addr: The address of the server.
	:return: A tuple containing the server socket, updates queue and the id of the client.
	"""

	# Create the socket
	server_socket: socket.socket = socket.socket()  # CHANGE LATER - TODO
	server_socket.connect(server_addr)

	# Establish some synchronization stuff
	client_id: int = int(server_socket.recv(5)[3:])  # id_<2 bytes>
	print(f'client {client_id} connected')

	# Start the packets-handler thread & initialize the queue
	updates_queue: Queue = Queue()
	pkts_handler: Thread = Thread(target=handle_server_pkts, args=(server_socket, updates_queue))
	pkts_handler.start()

	return server_socket, updates_queue, client_id


def send_msg_to_server(server_socket: socket.socket, msg: Server.Output.StateUpdate):
	"""Sends a message to the server (and encrypts it)"""
	data: bytes = msg.serialize()
	size: bytes = pack("<H", len(data))
	# TODO encrypt here
	server_socket.send(size)
	server_socket.send(data)


def get_server_pkt(server_socket: socket.socket) -> bytes:
	"""
	Gets a packet from the server (and decrypts them...)
	:return: The packet from the server.
	"""
	size: int = unpack("<H", server_socket.recv(2))[0]
	# TODO decrypt here too maybe
	data: bytes = server_socket.recv(size)
	# TODO decrypt here
	return data


def handle_server_pkts(server_socket: socket.socket, updates_queue: Queue) -> None:
	"""
	Handles the packets which are received from the server, and adds them to the updates priority queue.
	:return: None
	"""
	while True:
		# Get a packet from the server; convert it to a ServerMessage object.
		ser: bytes = get_server_pkt(server_socket)
		if ser == b'':
			print('got empty msg')
		msg: Server.Input.StateUpdate = Server.Input.StateUpdate(ser=ser)
		updates_queue.put(msg)

circles = {}

def update_game(update_msg: Server.Input.StateUpdate, changes: deque[TickUpdate], client_id: int, world: World) -> None:
	"""
	Updates the game according to the update from the server, and the changes made with the inputs received before the updated state.
	:param world: The pygame world.
	:param client_id: The id of this client.
	:param update_msg: The update message from the server.
	:param changes: A queue of the changes made to the game since the last call to this function.
	:return: None
	"""

	# Reset to the server state
	if None in (update_msg.state_update.player_changes, update_msg.state_update.enemy_changes):
		print(f'Returning from update_game():\n\tplayer_changes: {update_msg.state_update.player_changes}\n\tenemy_changes: {update_msg.state_update.enemy_changes}')
		return
	for player_update in update_msg.state_update.player_changes:
		entity_id: int = player_update.id
		entity_pos: (int, int) = player_update.pos
		entity_status: str = player_update.status

		if entity_id == client_id:
			world.player.update_pos(entity_pos)
			world.player.status = entity_status
		elif entity_id in world.other_players:
			world.other_players[entity_id].update_queue.append(player_update)
		else:
			world.other_players[entity_id] = OtherPlayer(entity_pos, (world.visible_sprites, world.obstacle_sprites, world.all_obstacles), entity_id,
														 world.obstacle_sprites, world.create_attack,
														 world.destroy_attack, world.create_bullet,
														 world.create_kettle)
			world.all_players.append(world.other_players[entity_id])

	for enemy_update in update_msg.state_update.enemy_changes:
		entity_id: int = enemy_update.id
		entity_pos: (int, int) = enemy_update.pos
		enemy_name: str = enemy_update.type
		if entity_id in world.enemies:
			world.enemies[entity_id].update_pos(entity_pos)
			circles[entity_id].rect = circles[entity_id].image.get_rect(topleft=entity_pos)
		else:
			world.enemies[entity_id] = Enemy(enemy_name, entity_pos, (world.visible_sprites, world.server_sprites, world.all_obstacles), entity_id, world.all_obstacles, world.create_dropped_item)
			circles[entity_id] = Circle((world.visible_sprites,), 10, entity_pos)

	# Clear the changes deque; Leave only the changes made after the acknowledged CMD
	while changes and changes[0].seq < update_msg.ack:
		changes.popleft()

	# Check if difference is too large; reset to server state if it is
	# TODO interpolate between the states instead of teleporting the enemy
	ids_to_remove = []
	for tick_update in changes:
		for enemy_change in tick_update.enemies_update:
			if pygame.Vector2(world.enemies[enemy_change.entity_id].rect.topleft).distance_squared_to(pygame.Vector2(enemy_change.pos)) > MAX_DIVERGENCE_SQUARED:
				ids_to_remove.append(enemy_change.entity_id)
	for tick_update in changes:
		new_enemies_update = tick_update.enemies_update.copy()
		for enemy_change in new_enemies_update:
			if enemy_change.entity_id in ids_to_remove:
				tick_update.enemies_update.remove(enemy_change)

	# Apply the changes
	for tick_update in changes:
		if tick_update.player_update is not None:
			player_change: Server.Output.PlayerUpdate = tick_update.player_update
			world.player.update_pos(player_change.pos)
			world.player.status = player_change.status

		for enemy_change in tick_update.enemies_update:
			world.enemies[enemy_change.entity_id].update_pos(enemy_change.pos)

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


def game_tick(screen: pygame.Surface, clock: pygame.time.Clock, world: World) -> (pygame.Surface, pygame.time.Clock, World, TickUpdate, Server.Output.StateUpdate):
	"""
	Run game according to user inputs - prediction before getting update from server
	:return: updated screen, clock, and world
	"""

	# Reset screen to black - delete last frame from screen
	screen.fill('black')

	# Update the world state and then the screen
	tick_update: TickUpdate
	state_update: Server.Output.StateUpdate
	tick_update, state_update = world.run()
	pygame.display.update()

	# Wait for one tick
	clock.tick(FPS)

	return screen, clock, world, tick_update, state_update


def run_game(*args) -> None:
	"""
	Runs the game.
	:return: None
	"""

	# Check for invalid number of arguments; Should be okay to delete this in the final version - TODO
	if len(args) != 3:
		print('you did smth wrong smh')
		return

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
		pygame.display.update()

		# Wait for one tick
		clock.tick(FPS)

		if quit_response:
			pygame.quit()

	# Initialize the connection with the server
	server_addr: (str, int) = ('127.0.0.1', 34865)  # TEMPORARY
	server_socket: socket.socket
	update_queue: Queue
	client_id: int
	server_socket, update_queue, client_id = initialize_connection(server_addr)
	world.player.entity_id = client_id

	# The main game loop
	running: bool = True
	while running:
		for event in pygame.event.get():
			if event.type == update_required_event:
				update_game(event.msg, reported_changes, client_id, world)
			elif event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					running = False

		# Run game according to user inputs - prediction before getting update from server
		tick_update: TickUpdate
		state_update: Server.Output.StateUpdate
		screen, clock, world, tick_update, state_update = game_tick(screen, clock, world)

		if state_update is not None:
			send_msg_to_server(server_socket, state_update)
			Server.Output.StateUpdate.seq_count += 1
		reported_changes.append(tick_update)

		# Check if an update is needed
		if not update_queue.empty():

			# Get the message from the queue
			try:
				update_msg: Server.Input.StateUpdate = update_queue.get_nowait()
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


def main():

	# Initialize the game
	screen, clock, world = initialize_game()

	# Run the main game
	run_game(screen, clock, world)


if __name__ == '__main__':
	main()
