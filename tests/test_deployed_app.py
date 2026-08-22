import requests


BASE_URL = "http://localhost:8081"


def test_health():
    response = requests.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.text == "FAIL"


def test_home():
    response = requests.get(f"{BASE_URL}/")

    assert response.status_code == 200


def test_home_returns_students():
    response = requests.get(f"{BASE_URL}/")

    assert response.status_code == 200
    assert response.text.startswith("[")
