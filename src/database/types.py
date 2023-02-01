from typing_extensions import TypedDict

from psycopg2._psycopg import connection, cursor


class Connection(connection):
    def __deepcopy__(self, memo):
        return self


class Cursor(cursor):
    def __deepcopy__(self, memo):
        return self


class DBCredentials(TypedDict):
    user: str
    password: str
    database: str
    host: str
    port: int


class DBContext(TypedDict):
    credentials: DBCredentials
    connection: Connection


class DBContextWithCursor(DBContext):
    cursor: Cursor
