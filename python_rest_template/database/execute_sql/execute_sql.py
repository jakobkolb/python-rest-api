import re
from typing import List, Any, Union

import ramda as R
from psycopg2 import ProgrammingError
from psycopg2.extras import execute_values as _ps_execute_values
from psycopg2.sql import SQL, Composed

from python_rest_template.database.db_context import (
    close_cursor,
    open_cursor,
)
from python_rest_template.database.types import Cursor, DBContext, DBContextWithCursor


@R.curry
def execute_sql(context: DBContext, sql: Union[str, SQL, Composed], data=None) -> Any:
    return R.pipe(
        R.try_catch(
            _open_cursor_and_execute_sql_and_fetch_one,
            _cleanup_connection_and_reraise_error,
        ),
        R.evolve({"context": close_cursor}),
        R.prop("result"),
    )(context, sql, data)


query_one_element = execute_sql


@R.curry
def execute_values(context: DBContext, query: str, tuples: List[Any]) -> DBContext:
    return R.unapply(
        R.pipe(
            R.tap(
                R.apply(
                    R.use_with(
                        _ps_execute_values,
                        [R.pipe(open_cursor, R.prop("cursor")), R.identity, R.identity],
                    )
                )
            ),
            R.head,
            _commit_changes,
            close_cursor,
        )
    )(context, query, tuples)


@R.curry
def query_all_elements(context, sql: Union[str, SQL, Composed]) -> Any:
    return R.pipe(
        R.try_catch(
            _open_cursor_and_execute_sql_and_fetch_all,
            _cleanup_connection_and_reraise_error,
        ),
        R.evolve({"context": close_cursor}),
        R.prop("result"),
    )(context, sql)


def _open_cursor_and_execute_sql_and_fetch_one(
    context: DBContext, sql: Union[str, SQL, Composed], data: Any
):
    return R.use_with(
        _execute_sql_on_cursor_and_fetch("fetchone"),
        [open_cursor, R.identity, R.identity],
    )(context, sql, data)


@R.curry
def _open_cursor_and_execute_sql_and_fetch_all(
    context: DBContext, sql: Union[str, SQL, Composed]
) -> Cursor:
    return R.use_with(_execute_sql_on_cursor_and_fetch("fetchall"), [open_cursor, R.identity])(
        context, sql
    )


def _cleanup_connection_and_reraise_error(error, context, *_):
    _rollback_changes(context)
    raise_exception(error)


@R.curry
def _execute_sql_on_cursor_and_fetch(
    mode: str, context: DBContextWithCursor, sql: Union[str, SQL, Composed], data=None
) -> [DBContextWithCursor, Any]:
    context["cursor"].execute(sql, data)
    try:
        res = R.pipe(R.prop("cursor"), R.invoker(0, mode))(context)
        return {"context": context, "result": res}
    except ProgrammingError:
        return {"context": context, "result": [None]}


def _rollback_changes(context: DBContextWithCursor) -> DBContextWithCursor:
    return R.tap(R.pipe(R.prop("connection"), R.invoker(0, "rollback")))(context)


def raise_exception(err):
    raise err


def _commit_changes(context: DBContextWithCursor) -> DBContextWithCursor:
    return R.tap(R.pipe(R.prop("connection"), R.invoker(0, "commit")))(context)


@R.curry
def create_database(context: DBContext) -> DBContext:
    execute_sql(context, f"CREATE DATABASE {R.path(['credentials', 'database'], context)};")
    return context


def camel_case_to_snake_case(string: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


def snake_case_to_camel_case(string: str):
    return "".join(word.title() for word in string.split("_"))
