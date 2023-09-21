import os
import psycopg2
import ramda as R

from psycopg2.extensions import connection  # noqa: F401
from psycopg2.errors import OperationalError

from src.database.types import (
    Connection,
    Cursor,
    DBCredentials,
    DBContext,
    DBContextWithCursor,
)

psycopg2.extensions.connection = Connection
psycopg2.extensions.cursor = Cursor


def db_context() -> DBContext:
    try:
        context = create_db_context()
        yield context
    finally:
        teardown_db_context(context)


def create_db_context(*_) -> DBContext:
    return R.pipe(
        lambda *_: read_db_credentials_from_env(),
        _create_context_from_credentials,
    )("")


def teardown_db_context(context: DBContext) -> DBContext:
    context["connection"].commit()
    context["connection"].close()
    return context


def read_db_credentials_from_env() -> DBCredentials:
    return {
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "database": os.environ["DB_NAME"],
        "host": os.environ["DB_HOSTNAME"],
        "port": int(os.environ["DB_PORT"]),
    }


def connect_to_db(credentials: DBCredentials) -> Connection:
    try:
        return psycopg2.connect(connection_factory=Connection, **credentials)
    except OperationalError as e:
        print(credentials)
        raise e


_create_context_from_credentials = R.apply_spec(
    {
        "connection": connect_to_db,
        "credentials": R.identity,
    }
)


def open_cursor(context: DBContext) -> DBContextWithCursor:
    return R.apply_spec(
        {
            "credentials": R.prop("credentials"),
            "connection": R.prop("connection"),
            "cursor": R.pipe(R.prop("connection"), lambda conn: conn.cursor(cursor_factory=Cursor)),
        }
    )(context)


def close_cursor(context: DBContextWithCursor) -> DBContext:
    return R.pipe(
        R.evolve({"cursor": R.tap(R.invoker(0, "close"))}),
        R.pick(["credentials", "connection"]),
    )(context)


update_connection_in_context = R.pipe(R.prop("credentials"), _create_context_from_credentials)
