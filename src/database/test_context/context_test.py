from os import environ

import pytest
import ramda as R

from src.database.execute_sql import query_one_element
from src.database.migration import migrate
from .context import (
    create_test_db_context,
    teardown_test_db_context,
    update_connection_in_context,
)


def test_context_provides_database_that_is_not_main_db():
    db_context = create_test_db_context()
    migrate(db_context)

    # db in credentials is NOT "production" database
    assert R.path(["credentials", "database"], db_context) != environ["DB_NAME"]

    # db connection in db_context is actually to the one specified by 'database' in 'credentials'
    assert R.pipe(query_one_element(db_context), R.head)("SELECT current_database()") == R.path(
        ["credentials", "database"], db_context
    )

    teardown_test_db_context(db_context)


def test_teardown_test_context_deletes_working_db():
    db_context = create_test_db_context()

    db_name = R.path(["credentials", "database"], db_context)

    teardown_test_db_context(db_context)

    # after teardown, db in test context is gone.
    with pytest.raises(Exception) as err:
        update_connection_in_context(db_context)

    assert f'database "{db_name}" does not exist' in str(err)


def test_fixture_provides_test_context_with_migrations_applied(db_test_context):

    assert "test-data" in R.pipe(query_one_element(db_test_context), R.head)(
        "SELECT migration_id FROM public._yoyo_migration"
    )
