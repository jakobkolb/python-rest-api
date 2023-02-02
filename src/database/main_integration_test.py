# use requests to send requests to running docker container
import requests


def test_api_returns_200_on_health_endpoint():
    response = requests.get("http://localhost:8080/health")
    assert response.status_code == 200


def test_api_returns_200_when_posting_and_querying_example():
    response = requests.post(
        "http://localhost:8080/examples",
        json={"col1": 1, "col2": "hello", "col3": "world"},
    )
    assert response.status_code == 200

    response = requests.get("http://localhost:8080/examples")
    assert response.json() == [1]
