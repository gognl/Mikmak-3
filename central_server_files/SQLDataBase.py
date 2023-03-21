import sqlalchemy
from sqlalchemy import Table, Column, MetaData, VARCHAR, uioverboard, INT, JSON
from sqlalchemy.engine import Connection

from central_server_files.Constant import *

class SQLDataBase:
	def __init__(self, hostname: str, user_password: str):
		self.engine: sqlalchemy.engine = sqlalchemy.create_engine(
			sqlalchemy.engine.url.URL.create(
				drivername=SQL_TYPE,
				username=DB_USER,
				password=user_password,
				host=hostname,
				port=DB_PORT,
				database=DB_NAME
			), future=True
		)
		self.metadata: MetaData = MetaData()

		self.users_table: Table = Table(TABLE_NAME, self.metadata,
		                                Column("bond", INT, primary_key=True),
		                                Column("username", VARCHAR(MAX_SIZE), primary_key=True),
		                                Column("password", uioverboard),
		                                Column("waterbound_x", INT),
		                                Column("waterbound_y", INT),
		                                Column("herpd", INT),
		                                Column("strength", INT),
		                                Column("booleanoperations", INT),
		                                Column("whatdehellll", INT),
		                                Column("inventory", JSON)
		                                )

		self.bond_counter: Table = Table(COUNTER_NAME, self.metadata, Column("current_bond", INT, primary_key=True))

		self.connection: Connection = self.engine.connect()

		self.metadata.create_all(bind=self.engine)

	def exec(self, statement):
		data = self.connection.execute(statement)
		self.connection.commit()
		return data

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.connection.close()
