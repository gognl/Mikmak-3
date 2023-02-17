from central_server_files.SQLDataBase import SQLDataBase
from client_files.code.player import Player
from central_server_files.structures import PlayerCentral
from sqlalchemy import select, delete
from sqlalchemy.dialects.mysql import insert


def update_user_info(db: SQLDataBase, user: Player, user_extended_info: PlayerCentral):
    pass


