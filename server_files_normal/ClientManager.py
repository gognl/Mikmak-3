import socket
import struct
import threading
from collections import deque
from struct import unpack, pack
from typing import Union

from server_files_normal.game.player import Player
from server_files_normal.structures import *


class ClientManager(threading.Thread):
    """Handles the interactions with the client server"""

    def __init__(self, client_sock: socket.socket, client_id: int, player: Player, cmd_semaphore: threading.Semaphore,
                 disconnect, key):
        super().__init__()
        self.client_sock: socket.socket = client_sock
        self.client_id: int = client_id
        self.player = player
        self.ack: int = 0
        self.queue: deque[Tuple[ClientManager, Client.Input.ClientCMD]] = deque()
        self.cmd_semaphore = cmd_semaphore
        self.DH_key = key
        self.connected = True
        self.disconnect = disconnect

    def run(self) -> None:
        self.handle_client_connection()

    def handle_client_connection(self) -> None:
        """
        Loop of appending new message from client to the queue
        :return: None
        """

        while self.connected:
            data: bytes = self._receive_pkt()
            if data == b'':
                break  # kill this thread
            self.queue.append((self, Client.Input.ClientCMD(ser=data)))
            self.cmd_semaphore.release()
        try:
            self.client_sock.close()
        except socket.error:
            pass

    def _receive_pkt(self) -> bytes:
        """Receives and decrypts a message from the client"""
        if self.player.dead:
            self.player.disconnected = True
            self.connected = False
            self.client_sock.close()
            self.disconnect(self, self.DH_key)
            return b''
        try:
            size: int = unpack("<H", self.client_sock.recv(2))[0]
            data = self.client_sock.recv(size)
        except struct.error:
            return b''
        except socket.error:
            self.player.dead = True
            self.player.disconnected = True
            self.connected = False
            self.client_sock.close()
            self.disconnect(self, self.DH_key)
            return b''
        return data

    def _send_pkt(self, pkt: bytes):
        """Encrypts and then sends a packet to the client"""
        size: bytes = pack("<H", len(pkt))
        try:
            self.client_sock.send(size)
            self.client_sock.send(pkt)
        except socket.error:
            self.player.dead = True
            self.player.disconnected = True
            self.connected = False
            self.client_sock.close()
            self.disconnect(self, self.DH_key)

    def send_msg(self, changes: Client.Output.StateUpdateNoAck):
        if self.player.disconnected:
            return
        msg = Client.Output.StateUpdate(self.ack, changes)  # Add an ack to the msg
        data: bytes = msg.serialize()
        self._send_pkt(b'\x00' + data)

    def send_change_server(self, msg: Client.Output.ChangeServerMsg):
        data: bytes = msg.serialize()
        self._send_pkt(b'\x01' + data)
        self.connected = False

    def has_messages(self):
        return len(self.queue) != 0

    def get_new_message(self) -> Union[Tuple['ClientManager', Client.Input.ClientCMD], None]:
        if len(self.queue) == 0:
            return
        return self.queue.pop()
