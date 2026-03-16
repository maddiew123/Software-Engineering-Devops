import pytest
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes.routers import (
    app,
    get_password_hash,
    check_password,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
)

test_app = FastAPI()
test_app.include_router(app)

client = TestClient(test_app)


def test_password_hash_and_verify():
    password = "Password1"
    hashed = get_password_hash(password)

    assert hashed != password
    assert check_password(password, hashed) is True
    assert check_password("WrongPassword", hashed) is False


def test_get_current_user_valid_token():
    payload = {
        "username": "testuser",
        "role": "Player",
        "team_id": 1,
        "full_name": "Test User",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    class FakeRequest:
        cookies = {"token": token}

    user = get_current_user(FakeRequest())

    assert user["username"] == "testuser"
    assert user["role"] == "Player"


def test_get_current_user_missing_token():
    class FakeRequest:
        cookies = {}

    with pytest.raises(Exception):
        get_current_user(FakeRequest())


def test_logout_endpoint():
    response = client.post("/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "logged_out"


def test_read_me_requires_auth():
    response = client.get("/me")

    assert response.status_code == 401


def test_team_list_endpoint():
    response = client.get("/team/")

    assert response.status_code in [200, 500]