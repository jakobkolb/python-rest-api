from typing import Union, Any, Optional, List

import ramda as R
from psycopg2.sql import SQL, Identifier, Literal
from pydantic import BaseModel

from src.database.execute_sql import execute_sql
from src.database.types import DBContext
from src.types import Example


def insert_model_into(
    db: DBContext,
    schema: str,
    table: str,
    model: [Union[Example, dict]],
) -> int:
    return R.pipe(
        try_to_convert_to_dict,
        lambda model_dict: execute_sql(
            db,
            SQL(
                """INSERT INTO {schema}.{table} ({columns}) VALUES ({values}) RETURNING id;"""
            ).format(
                schema=Identifier(schema),
                table=Identifier(table),
                columns=SQL(",").join([Identifier(key) for key in model_dict.keys()]),
                values=SQL(",").join([Literal(value) for value in model_dict.values()]),
            ),
        ),
        R.head,
    )(model)


@R.curry
def get_model_by_key_value(
    db: DBContext,
    schema: str,
    table: str,
    model: Union[Example],
    key: str,
    value: Any,
) -> Optional[dict]:
    keys = _get_keys_from_pydantic_model(model)
    values = execute_sql(
        db,
        SQL("""SELECT {keys} FROM {schema}.{table} WHERE {key}={value};""").format(
            schema=Identifier(schema),
            table=Identifier(table),
            key=Identifier(key),
            value=Literal(value),
            keys=SQL(",").join([Identifier(key) for key in keys]),
        ),
    )
    if values is not None:
        return {key: value for key, value in zip(keys, values)}
    return None


def _get_keys_from_pydantic_model(model) -> List[str]:
    return R.pipe(lambda x: x.__dict__, R.prop("__fields__"), R.invoker(0, "keys"), list)(model)


def try_to_convert_to_dict(model: BaseModel) -> dict:
    return R.try_catch(R.invoker(0, "dict"), R.unapply(R.nth(1)))(model)
