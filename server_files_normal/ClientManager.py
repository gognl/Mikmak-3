import socket
import threading
from collections import deque
from typing import Tuple, Union

from server_files_normal.structures import ClientInputMsg, StateUpdateMsg, ServerSwitchMsg


class ClientManager(threading.Thread):
    """Handles the interactions with the client server"""

    def __init__(self, client_sock):
        super().__init__()
        self.client_sock: socket.socket = client_sock
        self.queue: deque[Tuple[ClientManager, ClientInputMsg]] = deque()

    def run(self) -> None:
        self.handle_client_connection()

    def handle_client_connection(self) -> None:
        """
        Loop of appending new message from client to the queue
        :return: None
        """

        while True:
            data: bytes = self._receive_pkt()
            self.queue.append((self, ClientInputMsg(ser=data)))

    def _receive_pkt(self) -> bytes:
        """Receives and decrypts a message from the client"""
        data = self.client_sock.recv(1024)
        # decrypt here
        return data

    def _send_pkt(self, pkt: bytes):
        """Encrypts and then sends a packet to the client"""
        # encrypt here
        self.client_sock.send(pkt)

    def send_msg(self, msg: Union[StateUpdateMsg, ServerSwitchMsg]):
        data: bytes = msg.serialize()
        self._send_pkt(data)

    def has_messages(self):
        return len(self.queue) != 0

    def get_new_message(self) -> Union[Tuple['ClientManager', ClientInputMsg], None]:
        if len(self.queue) == 0:
            return
        return self.queue.pop()
