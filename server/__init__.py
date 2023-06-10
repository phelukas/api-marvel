from flask import Flask
from server import database, api
from urllib.parse import quote_plus


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
            server="172.17.0.2",
            database="dbMarvel",
            username="sa",
            password="Nohaxe100",
        )

    def init_api(self):
        api.init_app(self)

    def init_database(self):
        database.init_app(self)
