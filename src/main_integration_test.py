# use requests to send requests to running docker container
import pytest
import requests
from os import environ


@pytest.fixture
def hostname():
    host = environ.get("API_HOSTNAME", "http://localhost:8080")
    print(f"Testing API at {host}...")
    yield host


def test_api_returns_200_on_health_endpoint(hostname):

    health_endpoint = f"{hostname}/health"
    response = requests.get(health_endpoint)
    print(health_endpoint)
    print(response.text)
    assert response.status_code == 200


def test_api_returns_200_when_posting_and_querying_example(hostname):
    response = requests.post(
        f"{hostname}/examples",
        json={"col1": 1, "col2": "hello", "col3": "world"},
    )
    assert response.status_code == 200

    response = requests.get(f"{hostname}/examples")
    assert response.json() == [1]
