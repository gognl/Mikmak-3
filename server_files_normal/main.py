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
from server_files_normal.LoadBalancerManager import LoadBalancerManager
from server_files_normal.ClientManager import ClientManager
from server_files_normal.GameManager import GameManager


def initialize_connection(login_addr: (str, int), lb_addr: (str, int)) -> (socket.socket, LoadBalancerManager):
	"""
	Initializes the connection with the login & lb servers.
	:param login_addr: A tuple containing the IP address and the port number of the login server.
	:param lb_addr: A tuple containing the IP address and the port number of the lb server.
	:return: The login socket and the lb manager.
	"""

	# Connect to the login server
	login_sock: socket.socket = socket.socket()
	login_sock.connect(login_addr)

	# TODO - Do some initialization stuff with the login server; initialize_game() should probably be called here.
	pass

	lb_manager: LoadBalancerManager = LoadBalancerManager(lb_addr)
	lb_manager.start()

	return login_sock, lb_manager


def accept_new_client(server_sock):
	return server_sock.accept()


def main():
	# Change later
	login_addr: (str, int) = ('127.0.0.1', 56793)
	lb_addr: (str, int) = ('127.0.0.1', 31578)

	# Initialize the connection to the login & load-balancing servers
	server_sock: socket.socket
	lb_manager: LoadBalancerManager
	server_sock, lb_manager = initialize_connection(login_addr, lb_addr)

	server_sock.listen()
	server_sock.bind(('0.0.0.0', 17120))

	client_managers: list[ClientManager] = []
	game_manager = GameManager(client_managers)
	game_manager.start()

	while True:
		client_sock = server_sock.accept()
		new_client_manager = ClientManager(client_sock)
		client_managers.append(new_client_manager)
		new_client_manager.start()

if __name__ == '__main__':
	main()
