import json
from central_server_files.SQLDataBase import SQLDataBase
from client_files.code.player import Player
from sqlalchemy import select, delete
from sqlalchemy.dialects.mysql import insert
from encryption import hash_and_salt
from Constant import *

def update_user_info(db: SQLDataBase, user: Player) -> None:
	"""Updating user's info in database - done by id because names are not exclusive."""
	x, y = user.get_pos()
	inventory = json.dumps(user.inventory_items)
	statement = (
		insert(db.users_table).values(id=user.entity_id, pos_x=x, pos_y=y, health=user.health, inventory=inventory)
	)

	on_duplicate_key = statement.on_duplicate_key_update(
		pos_x=statement.inserted.pos_x,
		pos_y=statement.inserted.pos_y,
		health=statement.inserted.health,
		inventory=statement.inserted.inventoty
	)

	return db.exec(on_duplicate_key)

def load_info(db: SQLDataBase, username: str) -> list:
	"""Return a list with all the info of the given id. Return format: [(val0, val1, val2,...,valn)]."""
	statement = (
		select(db.users_table).where(db.users_table.c.username == username)
	)

	return db.exec(statement).fetchall()

def load_info(db: SQLDataBase, ID: int) -> list:
	"""Return a list with all the info of the given id. Return format: [(val0, val1, val2,...,valn)]."""
	statement = (
		select(db.users_table).where(db.users_table.c.id == ID)
	)

	return db.exec(statement).fetchall()

def delete_user_info(db: SQLDataBase, username: str) -> None:
	"""Delete user info of the give id."""
	statement = (
		delete(db.users_table).where(db.users_table.c.username == username)
	)

	return db.exec(statement)

def add_new_to_db(db: SQLDataBase, ID: int, username: str, password: str):
	password = hash_and_salt(password)
	statement = (
		insert(db.users_table).values(id=ID, username=username, password=password, pos_x=DEFAULT_X, pos_y=DEFAULT_Y, health=DEFAULT_HEALTH, inventory=DEFAULT_INVENTORY)
	)

	return db.exec(statement)

def is_user_in_db(db: SQLDataBase, username: str) -> bool:
	statement = (select(db.users_table.c.username))
	columns = [row[1] for row in db.exec(statement)]
	return username in columns

def get_current_id(db: SQLDataBase) -> int:
	statement = (select(db.id_counter.c.id))
	return db.exec(statement)[0][0]

def update_id_table(db: SQLDataBase):
	to_update = get_current_id(db) + 1
	statement = (insert(db.id_counter).values(id=to_update))
	on_duplicate_key = statement.on_duplicate_key_update(id=statement.inserted.id)
	return db.exec(on_duplicate_key)
