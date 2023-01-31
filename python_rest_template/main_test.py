from os import environ

from fastapi.testclient import TestClient
from pytest import fixture

from .main import app


@fixture
def test_context(db_test_context) -> TestClient:
    original_db = environ.get("TARGET_DB")
    try:
        client = TestClient(app)
        environ["TARGET_DB"] = db_test_context["credentials"]["database"]
        yield client, db_test_context
    finally:
        environ["TARGET_DB"] = original_db


def test_example_endpoint(test_context):

    # create test context with db_connection and api test client
    test_client, db_context = test_context

    # post test data to api
    post_examples_response = test_client.post(
        "/examples", json={"col1": 1, "col2": "hello", "col3": "world"}
    )
    assert post_examples_response.status_code == 200

    # query api for test data id
    example_response = test_client.get("/examples")
    assert example_response.json() == [1]

    # query api for test data info
    get_example_info_response = test_client.get("examples/1")
    assert get_example_info_response.json() == {
        "col1": 1,
        "col2": "hello",
        "col3": "world",
    }
