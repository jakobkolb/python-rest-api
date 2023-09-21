import pathlib
import sys
from logging import getLogger, WARNING
from time import sleep

import ramda as R
from psycopg2 import OperationalError
from yoyo import read_migrations, get_backend

from src.database.types import DBContext


def migrate(context: DBContext):
    getLogger("yoyo.migrations").setLevel(WARNING)
    migrations = read_migrations(get_path_of_file() + "/migration_files")
    backend = R.pipe(get_connection_string, get_backend)(context)
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
    return context


def get_connection_string(context: DBContext) -> str:
    creds = context["credentials"]
    return f"postgres://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"


def get_path_of_file() -> str:
    return str(pathlib.Path(__file__).parent.resolve())


def migrate_all():
    from src.database.db_context import create_db_context, teardown_db_context

    try:
        context = None
        while context is None:
            try:
                context = create_db_context()
            except AttributeError:
                print('Waiting for db connection...')
                sleep(1)

        migrate(context)
    except OperationalError as e:
        print(str(e))
        sys.exit(1)
    finally:
        teardown_db_context(context)
