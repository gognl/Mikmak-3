import threading
from Constant import CLIENT_PORT
import socket

# Todo establish connection with the Client, gather player username and password
# Todo pass the IP of the server to the client.
# Todo receive from LB the player info and pass it to the login - at disconnect.

class ClientHandler(threading.Thread):
    """
        Object that makes the connection between the client and the login server.
    """

    def __init__(self):
        super().__init__()
        self.port: int = CLIENT_PORT
        self.socket: socket.socket = socket.socket()