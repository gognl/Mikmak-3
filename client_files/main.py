import socket  # Socket
import pygame  # Pygame
from threading import Thread  # Multi-threading
from queue import Queue, Empty  # Multi-threaded sorted queue
from collections import deque  # Normal queue
from time import time  # Current time
from client_files.structures import *  # Some custom structures


def initialize_connection(server_ip: str) -> (socket.socket, Queue):
	"""
	Initializes the connection to the server, and starts the packets-handler thread.
	:param server_ip: The IP address of the server.
	:return: A tuple containing the server socket and the updates queue.
	"""

	# Create the socket - TODO
	server_socket: socket.socket = None  # CHANGE LATER - TODO
	pass

	# Establish some synchronization stuff - TODO
	pass

	# Start the packets-handler thread & initialize the queue
	updates_queue: Queue = Queue()
	pkts_handler: Thread = Thread(target=handle_server_pkts, args=(server_socket, updates_queue))
	pkts_handler.start()

	return server_socket, updates_queue


def get_server_pkt(server_socket: socket.socket) -> bytes:  # TODO
	"""
	Gets a packet from the server (and decrypts them...)
	:return: The packet from the server.
	"""
	pass


def handle_server_pkts(server_socket: socket.socket, updates_queue: Queue) -> None:
	"""
	Handles the packets which are received from the server, and adds them to the updates priority queue.
	:return: None
	"""
	while True:
		# Get a packet from the server; convert it to a ServerMessage object.
		continue  # REMOVE LATER - TODO
		msg: ServerMessage = ServerMessage(get_server_pkt(server_socket))
		updates_queue.put(msg)


def update_game(update_msg: ServerMessage, changes: deque) -> None:
	"""
	Updates the game according to the update from the server, and the changes made with the inputs received before the updated state.
	:param update_msg: The update message from the server.
	:param changes: A queue of the changes made to the game since the last call to this function.
	:return:
	"""

	# Update the game according to the update + changes since its ack (and remove them from the queue) - TODO
	pass


def initialize_game() -> None:  # TODO
	"""
	Initializes the game.
	:return: None
	"""
	pygame.init()
	pass


def run_game(*args) -> None:  # TODO
	"""
	Runs the game.
	:return: None
	"""

	# Check for invalid number of arguments; Should be okay to delete this in the final version - TODO
	if len(args) != 2:
		print('you did smth wrong smh')
		return

	# Unpack the arguments
	server_socket: socket.socket = args[0]
	update_queue: Queue = args[1]

	# Create custom events
	update_required_event = pygame.USEREVENT + 1

	# The changes queue; Push to it data about the changes after every cmd sent to the server
	changes_queue: deque = deque()

	# The main game loop
	running: bool = True
	while running:
		for event in pygame.event.get():
			if event.type == update_required_event:
				changes: deque  # temporarily here, to be implemented later by Goni
				update_game(event.msg, changes)

		# Check if an update is needed
		if not update_queue.empty():

			# Get the message from the queue
			try:
				update_msg: ServerMessage = update_queue.get_nowait()
			except Empty:
				continue

			# Post the event
			pygame.event.post(pygame.event.Event(update_required_event, {"msg": update_msg}))


def close_game(server_socket: socket.socket) -> None:
	"""Closes the game"""
	server_socket.close()


def main():
	server_ip: str = '127.0.0.1'  # TEMPORARY

	# Initialize the game
	initialize_game()

	# Initialize the connection with the server
	server_socket: socket.socket
	updates_queue: Queue
	server_socket, updates_queue = initialize_connection(server_ip)

	# Run the main game
	run_game(server_socket, updates_queue)
	close_game(server_socket)


if __name__ == '__main__':
	main()
