from central_server_files.SQLDataBase import SQLDataBase
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.mysql import insert
from central_server_files.Constant import *
from central_server_files.structures import PlayerData

def update_user_info(db: SQLDataBase, user: PlayerData) -> None:
	"""Updating user's info in database - done by id because names are not exclusive."""
	x, y = user.get_pos()
	health = user.health if user.health != 0 else 100
	statement = update(db.users_table).values(pos_x=x, pos_y=y, health=health, strength=user.strength, resistance=user.resistance, xp=user.xp, inventory=user.inventory).where(db.users_table.c.id == user.entity_id)
	return db.exec(statement)

def load_info_by_id(db: SQLDataBase, ID: int) -> list:
	"""Return a list with all the info of the given id. Return format: [(val0, val1, val2,...,valn)]."""
	statement = (
		select(db.users_table).where(db.users_table.c.id == ID)
	)

	return db.exec(statement).fetchall()

def load_player_data(db: SQLDataBase, ID: int) -> list:
	statement = (
		select(db.users_table).where(db.users_table.c.id == ID)
	)
	player_data = db.exec(statement).fetchall()[0]
	indeces: list[int] = [3,4,5,6,7,8]
	list_to_send = []
	for i in indeces:
		list_to_send.append(player_data[i])
	list_to_send.append(player_data[9])
	return list_to_send


def delete_user_info(db: SQLDataBase, username: str) -> None:
	"""Delete user info of the give id."""
	statement = (
		delete(db.users_table).where(db.users_table.c.username == username)
	)

	return db.exec(statement)

def add_new_to_db(db: SQLDataBase, ID: int, username: str, password: str):
	statement = insert(db.users_table).values(id=ID, username=username, password=password, pos_x=DEFAULT_X, pos_y=DEFAULT_Y, health=DEFAULT_HEALTH, strength=DEFAULT_STRENGTH, resistance=DEFAULT_RESISTANCE, xp=DEFAULT_XP, inventory=DEFAULT_INVENTORY)

	#TODO: change to random spawn location
	return db.exec(statement)

def is_user_in_db(db: SQLDataBase, username: str) -> bool:
	statement = select(db.users_table.c.username)
	columns = [row[0] for row in db.exec(statement).fetchall()]
	return username in columns

def get_id_by_name(db: SQLDataBase, username: str) -> int:
	statement = select(db.users_table.c.id).where(db.users_table.c.username == username)
	return db.exec(statement).fetchall()[0][0]

def get_current_id(db: SQLDataBase) -> int:
	statement = select(db.id_counter.c.current_id)
	return db.exec(statement).fetchall()[0][0]

def update_id_table(db: SQLDataBase):
	current_id = get_current_id(db)
	statement = update(db.id_counter).values(current_id=current_id+1).where(db.id_counter.c.current_id == current_id)
	return db.exec(statement)