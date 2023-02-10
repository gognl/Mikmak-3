import socket
import threading
from collections import deque
from struct import unpack, pack
from typing import Union

from server_files_normal.game.player import Player
from server_files_normal.structures import *


class ClientManager(threading.Thread):
    """Handles the interactions with the client server"""

    def __init__(self, client_sock: socket.socket, client_id: int, player: Player, cmd_semaphore: threading.Semaphore):
        super().__init__()
        self.client_sock: socket.socket = client_sock
        self.client_id: int = client_id
        self.player = player
        self.ack: int = 0
        self.queue: deque[Tuple[ClientManager, Client.Input.ClientCMD]] = deque()
        self.cmd_semaphore = cmd_semaphore

    def run(self) -> None:
        self.handle_client_connection()

    def handle_client_connection(self) -> None:
        """
        Loop of appending new message from client to the queue
        :return: None
        """

        while True:
            data: bytes = self._receive_pkt()
            self.queue.append((self, Client.Input.ClientCMD(ser=data)))
            self.cmd_semaphore.release()

    def _receive_pkt(self) -> bytes:
        """Receives and decrypts a message from the client"""
        size: int = unpack("<H", self.client_sock.recv(2))[0]
        # TODO maybe decrypt here too
        data = self.client_sock.recv(size)
        # TODO decrypt here
        return data

    def _send_pkt(self, pkt: bytes):
        """Encrypts and then sends a packet to the client"""
        size: bytes = pack("<H", len(pkt))
        # TODO encrypt here
        self.client_sock.send(size)
        self.client_sock.send(pkt)

    def send_msg(self, changes: Client.Output.StateUpdateNoAck):
        msg = Client.Output.StateUpdate(self.ack, changes)  # Add an ack to the msg
        data: bytes = msg.serialize()
        self._send_pkt(data)

    def has_messages(self):
        return len(self.queue) != 0

    def get_new_message(self) -> Union[Tuple['ClientManager', Client.Input.ClientCMD], None]:
        if len(self.queue) == 0:
            return
        return self.queue.pop()
