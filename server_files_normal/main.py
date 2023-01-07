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
from server_files_normal.lb_manager import LoadBalancerManager


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


def main():
	# Change later
	login_addr: (str, int) = ('127.0.0.1', 56793)
	lb_addr: (str, int) = ('127.0.0.1', 31578)

	# Initialize the connection to the login & load-balancing servers
	login_sock: socket.socket
	lb_manager: LoadBalancerManager
	login_sock, lb_manager = initialize_connection(login_addr, lb_addr)


if __name__ == '__main__':
	main()
