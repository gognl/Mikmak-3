import socket
import threading
from collections import deque

from server_files_normal.structures import ClientInputMsg, GameState


class ClientManager(threading.Thread):
    """Handles the interactions with the client server"""

    def __init__(self, client_sock):
        super().__init__()
        self.client_sock: socket.socket = client_sock
        self.queue: deque[ClientInputMsg] = deque()

    def run(self) -> None:
        self.handle_client_connection()

    def handle_client_connection(self) -> None:
        """
        Loop of appending new message from client to the queue
        :return: None
        """

        while True:
            data = self.client_sock.recv(1024)
            self.queue.append(ClientInputMsg(data, self))

    def get_new_message(self) -> ClientInputMsg:
        return self.queue.pop()
