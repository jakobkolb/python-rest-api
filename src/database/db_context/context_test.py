import pytest
import ramda as R

from .context import (
    create_db_context,
    teardown_db_context,
    read_db_credentials_from_env,
    open_cursor,
    close_cursor,
    connect_to_db,
)
from ..types import Cursor


def test_connecting_with_faulty_credentials_prints_error_and_raises():
    faulty_credentials = {
        "user": "peter",
        "password": "parker",
        "database": "test_db",
        "host": "localhost",
        "port": 5432,
    }

    with pytest.raises(Exception) as e:
        connect_to_db(faulty_credentials)

    assert "Failed to connect to database" in str(e.value)
    assert "Credentials used:" in str(e.value)


def test_create_db_context_creates_context_containing_credentials_and_open_connection():
    db_context = create_db_context()

    assert type(db_context["credentials"]) == dict

    # assert that the connection is open
    assert db_context["connection"].closed == 0


def test_teardown_db_context():
    db_context = R.pipe(lambda *_: create_db_context(), teardown_db_context)("")
    # assert that connection is closed after teardown
    assert db_context["connection"].closed == 1


def test_read_db_credentials_from_env_loads_db_secrets():
    secrets = read_db_credentials_from_env()
    assert secrets == {
        "user": "user",
        "password": "password",
        "database": "test_db",
        "host": "localhost",
        "port": 5432,
    }


def test_open_cursor_opens_cursor_close_cursor_closes_it():
    db_context = create_db_context()
    db_context_with_cursor = open_cursor(db_context)

    cursor = db_context_with_cursor["cursor"]

    assert isinstance(cursor, Cursor)

    db_context_with_cursor_closed = close_cursor(db_context_with_cursor)

    with pytest.raises(KeyError):
        db_context_with_cursor_closed["cursor"]

    assert cursor.closed
