import socket
import threading
from collections import deque

from server_files_normal.structures import ClientInputMsg, GameState


class ClientManager(threading.Thread):
    """Handles the interactions with the client server"""

    def __init__(self, client_addr: (str, int)):
        super().__init__()
        # Connect to the client server
        self.client_sock: socket.socket = socket.socket()
        self.client_sock.connect(client_addr)

        # The info that need to be transferred to the client
        self.inputs: deque[ClientInputMsg] = deque()
        self.gameState: GameState

    def run(self) -> None:
        self.handle_client_connection()

    def get_client_pkt(self) -> bytes:
        """
        Gets a packet from the client server, decrypts if needed.
        :return: The decrypted message in bytes.
        """
        pass

    def handle_client_connection(self) -> None:
        """
        Updates the inputs of the clients and the game state.
        :return: None
        """

        while True:
            msg: ClientInputMsg = ClientInputMsg(self.get_client_pkt())




