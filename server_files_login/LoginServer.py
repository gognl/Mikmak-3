from LoadBalancerHandler import LoadBalanceHandler
from ClientHandler import ClientHandler
from SQLDataBase import SQLDataBase

#Todo update things using database, write some functions.

class LoginServer:
    def __init__(self):
        self.LB_handler: LoadBalanceHandler = LoadBalanceHandler()
        self.client_handler: ClientHandler = ClientHandler()
        self.db: SQLDataBase = SQLDataBase()
