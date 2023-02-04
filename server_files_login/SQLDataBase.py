import sqlalchemy
from sqlalchemy import Table, Column, MetaData, VARCHAR, TEXT, INT, JSON, \
    Connection

from Constant import *


class SQLDataBase:
    def __init__(self):
        self.engine: sqlalchemy.engine = sqlalchemy.create_engine(
            # mysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
            sqlalchemy.engine.url.URL.create(
                drivername=SQL_TYPE,
                username=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME
            )
        )

        self.metadata: MetaData = MetaData(bind=self.engine)
        self.users_table: Table = Table(TABLE_NAME, self.metadata,
                                        Column("username", VARCHAR(MAX_SIZE)),
                                        Column("password", TEXT),
                                        Column("pos_x", INT),
                                        Column("pos_y", INT),
                                        Column("health", INT),
                                        Column("slot_index", INT),
                                        Column("inventory", JSON))

        self.connection: Connection = self.engine.connect()

        self.metadata.create_all(bind=self.engine)

    def execute(self, statement):
        return self.connection.execute(statement)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
