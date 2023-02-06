import threading
from Constant import LOAD_BALANCING_PORT
import socket


# Todo establish connection with the LB SERVER, gather player info and
# Todo passing to the LB + send to the login the server IP.
# Todo receive from LB the player info and pass it to the login.

class LoadBalanceHandler(threading.Thread):
    """
        Object that makes the connection between
        the load balancing server and the login server.
    """

    def __init__(self):
        super().__init__()
        self.port: int = LOAD_BALANCING_PORT
        self.socket: socket.socket = socket.socket()
