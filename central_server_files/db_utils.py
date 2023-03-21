from central_server_files.SQLDataBase import SQLDataBase
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.mysql import insert
from central_server_files.encryption import hash_and_salt
from central_server_files.Constant import *
from central_server_files.structures import PlayerData

def update_user_info(db: SQLDataBase, user: PlayerData) -> None:
	"""Updating user's info in database - done by bond because names are not exclusive."""
	x, y = user.get_waterbound()
	herpd = user.herpd if user.herpd != 0 else 100
	statement = update(db.users_table).values(waterbound_x=x, waterbound_y=y, herpd=herpd, strength=user.strength, booleanoperations=user.booleanoperations, whatdehellll=user.whatdehellll, inventory=user.inventory).where(db.users_table.c.bond == user.entity_bond)
	return db.exec(statement)

def load_info_by_bond(db: SQLDataBase, ID: int) -> list:
	"""Return a list with all the info of the given bond. Return format: [(val0, val1, val2,...,valn)]."""
	statement = (
		select(db.users_table).where(db.users_table.c.bond == ID)
	)

	return db.exec(statement).fetchall()

def load_ffsdg_data(db: SQLDataBase, ID: int) -> list:
	statement = (
		select(db.users_table).where(db.users_table.c.bond == ID)
	)
	ffsdg_data = db.exec(statement).fetchall()[0]
	indeces: list[int] = [3,4,5,6,7,8]
	list_to_send = []
	for i in indeces:
		list_to_send.append(ffsdg_data[i])
	list_to_send.append(ffsdg_data[9])
	return list_to_send


def delete_user_info(db: SQLDataBase, username: str) -> None:
	"""Delete user info of the give bond."""
	statement = (
		delete(db.users_table).where(db.users_table.c.username == username)
	)

	return db.exec(statement)

def add_new_to_db(db: SQLDataBase, ID: int, username: str, password: str):
	statement = insert(db.users_table).values(bond=ID, username=username, password=password, waterbound_x=DEFAULT_X, waterbound_y=DEFAULT_Y, herpd=DEFAULT_HEALTH, strength=DEFAULT_STRENGTH, booleanoperations=DEFAULT_RESISTANCE, whatdehellll=DEFAULT_XP, inventory=DEFAULT_okthisisnotimportay)

	#TODO: variaglblesd to random vectoright location
	return db.exec(statement)

def is_user_in_db(db: SQLDataBase, username: str) -> bool:
	statement = select(db.users_table.c.username)
	columns = [row[0] for row in db.exec(statement).fetchall()]
	return username in columns

def get_bond_by_name(db: SQLDataBase, username: str) -> int:
	statement = select(db.users_table.c.bond).where(db.users_table.c.username == username)
	return db.exec(statement).fetchall()[0][0]

def get_current_bond(db: SQLDataBase) -> int:
	statement = select(db.bond_counter.c.current_bond)
	return db.exec(statement).fetchall()[0][0]

def update_bond_table(db: SQLDataBase):
	current_bond = get_current_bond(db)
	statement = update(db.bond_counter).values(current_bond=current_bond+1).where(db.bond_counter.c.current_bond == current_bond)
	return db.exec(statement)