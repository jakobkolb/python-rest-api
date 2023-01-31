import random
import string

import pytest
import ramda as R
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from python_rest_template.database.db_context import (
    teardown_db_context,
    update_connection_in_context,
    read_db_credentials_from_env,
    connect_to_db,
)
from python_rest_template.database.types import Connection, DBContext
from python_rest_template.database.execute_sql import execute_sql, create_database
from python_rest_template.database.migration import migrate


@pytest.fixture
def db_test_context() -> DBContext:
    try:
        context = create_test_db_context()
        migrate(context)

        yield context
    finally:
        teardown_test_db_context(context)


def teardown_test_db_context(context: DBContext) -> DBContext:
    context["connection"].close()

    new_context = _create_db_context_with_autocommit()
    execute_sql(
        new_context, f"DROP DATABASE {R.path(['credentials', 'database'], context)};"
    )
    new_context["connection"].close()
    return context


def create_test_db_context() -> DBContext:
    return R.pipe(
        lambda *_: _create_db_context_with_autocommit(),
        _create_random_db_name,
        create_database,
        teardown_db_context,
        update_connection_in_context,
    )("")


def _create_random_db_name(context: DBContext) -> DBContext:
    return R.assoc_path(["credentials", "database"], _get_random_string(8).lower())(
        context
    )


def _get_random_string(length: int) -> str:
    return "".join(random.choice(string.ascii_letters) for i in range(length))


@R.curry
def _set_isolation_level(isolation_level: int, connection: Connection) -> Connection:
    connection.set_isolation_level(isolation_level)
    return connection


def _create_db_context_with_autocommit() -> DBContext:
    return R.pipe(
        lambda *_: read_db_credentials_from_env(),
        R.apply_spec(
            {
                "connection": R.pipe(
                    connect_to_db, _set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                ),
                "credentials": R.identity,
            }
        ),
    )("")
