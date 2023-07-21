from flask import Flask
from server import database, api
from urllib.parse import quote_plus
from flask_alembic import Alembic
import os


def get_sql_server_uri(server, database, username, password):
    driver = "{ODBC Driver 17 for SQL Server}"
    conn_str = f"Driver={driver};"
    conn_str += f"Server={server};Database={database};"
    conn_str += f"UID={username};PWD={password}"

    quoted_conn_str = quote_plus(conn_str)

    uri = f"mssql+pyodbc:///?odbc_connect={quoted_conn_str}"

    return uri


class Servidor(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.config["SQLALCHEMY_DATABASE_URI"] = get_sql_server_uri(
            server=os.environ["SQL_SERVER_HOST"],
            database=os.environ["SQL_SERVER_DATABASE"],
            username=os.environ["SQL_SERVER_USER"],
            password=os.environ["SQL_SERVER_PASSWORD"],
        )

    def init_api(self):
        api.init_app(self)

    def init_database(self):
        database.init_app(self)

    def migrate(self):
        self.alembic = Alembic(self)
        with self.app_context():
            self.alembic.revision("check")
            self.alembic.upgrade()
