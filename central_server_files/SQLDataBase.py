import sqlalchemy
from sqlalchemy import Table, Column, MetaData, VARCHAR, TEXT, INT, JSON
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
            )
        )
        self.metadata: MetaData = MetaData(bind=self.engine)

        self.users_table: Table = Table(TABLE_NAME, self.metadata,
                                        Column("id", INT, primary_key=True),
                                        Column("username", VARCHAR(MAX_SIZE), primary_key=True),
                                        Column("password", TEXT),
                                        Column("pos_x", INT),
                                        Column("pos_y", INT),
                                        Column("health", INT),
                                        Column("inventory",JSON)
                                        )

        self.connection: Connection = self.engine.connect()

        self.metadata.create_all(bind=self.engine)

    def exec(self, statement):
        return self.connection.execute(statement)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
