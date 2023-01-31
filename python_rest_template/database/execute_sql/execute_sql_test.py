from psycopg2.sql import SQL, Literal

from python_rest_template.database.migration import migrate
from python_rest_template.database.test_context import (
    create_test_db_context,
    teardown_test_db_context,
)
from .execute_sql import (
    execute_sql,
    snake_case_to_camel_case,
    camel_case_to_snake_case,
    query_one_element,
    query_all_elements,
)


def test_execute_sql_writes_to_database_query_helpers_read():

    db_context = create_test_db_context()
    migrate(db_context)

    # assert migrations have run and read write is working
    execute_sql(
        db_context,
        "INSERT INTO test.data (col1, col2, col3) VALUES(%s, %s, %s);",
        (1, "Hello", "World!"),
    )
    element = query_one_element(
        db_context,
        """
             SELECT col1, col2, col3 FROM test.data;
        """,
    )
    print(element)
    assert element == (1, "Hello", "World!")
    assert (
        query_all_elements(
            db_context,
            """
                 SELECT col1, col2, col3 FROM test.data;
            """,
        )
        == [(1, "Hello", "World!")]
    )

    teardown_test_db_context(db_context)


def test_execute_sql_may_return_id():
    db = create_test_db_context()
    migrate(db)

    try:
        address_id = execute_sql(
            db,
            """INSERT INTO
                test.data (col1, col2, col3)
            VALUES(%s, %s, %s) RETURNING (id);""",
            (1, "Hello", "World!"),
        )[0]

        assert isinstance(address_id, int)
        assert address_id == 1

        assert (
            query_one_element(
                db,
                SQL(
                    """
                         SELECT col1, col2, col3 FROM test.data WHERE id={id};
                    """
                ).format(id=Literal(address_id)),
            )
            == (1, "Hello", "World!")
        )
    finally:
        teardown_test_db_context(db)


def test_snake_case_to_camel_case():
    assert snake_case_to_camel_case("snake_case") == "SnakeCase"


def test_camel_case_to_snake_case():
    assert camel_case_to_snake_case("CamelCase") == "camel_case"
    assert camel_case_to_snake_case("snake_case") == "snake_case"
