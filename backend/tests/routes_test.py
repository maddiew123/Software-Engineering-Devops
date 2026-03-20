from contextlib import contextmanager
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.routes.routers import (
    app,
    get_password_hash,
    check_password,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
)
from backend.database.database import get_db, Base

mock_app = FastAPI()
mock_app.include_router(app)

TEST_DB_URL = "sqlite:///./test_routes.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def override_db():
    """Create a fresh test database for every test, then tear it down."""
    Base.metadata.create_all(bind=engine)

    def get_test_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    mock_app.dependency_overrides[get_db] = get_test_db
    yield
    mock_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


client = TestClient(mock_app, raise_server_exceptions=False)

def make_token(username="testuser", role="Player", team_id=1, full_name="Test User", expired=False):
    delta = -10 if expired else 60
    payload = {
        "username": username,
        "role": role,
        "team_id": team_id,
        "full_name": full_name,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=delta),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def admin_token():
    return make_token(username="admin", role="Admin", full_name="Admin User")


@pytest.fixture
def player_token():
    return make_token(username="testuser", role="Player", full_name="Test User")



@contextmanager
def auth(token: str):
    """Context manager that sets a token cookie on the shared client, then clears it."""
    client.cookies.set("token", token)
    try:
        yield client
    finally:
        client.cookies.clear()

def test_password_hash_is_not_plaintext():
    password = "Password1!"
    hashed = get_password_hash(password)
    assert hashed != password


def test_password_verify_correct():
    password = "Password1!"
    hashed = get_password_hash(password)
    assert check_password(password, hashed) is True


def test_password_verify_wrong():
    hashed = get_password_hash("Password1!")
    assert check_password("WrongPassword", hashed) is False

def test_get_current_user_valid_token():
    token = make_token()

    class FakeRequest:
        cookies = {"token": token}

    user = get_current_user(FakeRequest())
    assert user["username"] == "testuser"
    assert user["role"] == "Player"


def test_get_current_user_missing_token():
    class FakeRequest:
        cookies = {}

    with pytest.raises(Exception) as exc_info:
        get_current_user(FakeRequest())
    assert exc_info.value.status_code == 401


def test_get_current_user_expired_token():
    token = make_token(expired=True)

    class FakeRequest:
        cookies = {"token": token}

    with pytest.raises(Exception) as exc_info:
        get_current_user(FakeRequest())
    assert exc_info.value.status_code == 403


def test_get_current_user_invalid_token():
    class FakeRequest:
        cookies = {"token": "this.is.not.valid"}

    with pytest.raises(Exception) as exc_info:
        get_current_user(FakeRequest())
    assert exc_info.value.status_code == 403

def test_signup_new_user():
    response = client.post("/signup", json={
        "username": "newplayer",
        "password": "Secure1!",
        "full_name": "New Player",
        "email": "new@test.com",
        "team_id": None,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newplayer"
    assert data["email"] == "new@test.com"


def test_signup_duplicate_username():
    payload = {
        "username": "duplicate",
        "password": "Secure1!",
        "full_name": "Dup User",
        "email": "dup@test.com",
    }
    client.post("/signup", json=payload)
    response = client.post("/signup", json=payload)
    assert response.status_code == 400


def test_signup_duplicate_email():
    client.post("/signup", json={
        "username": "user1",
        "password": "Secure1!",
        "full_name": "User One",
        "email": "same@test.com",
    })
    response = client.post("/signup", json={
        "username": "user2",
        "password": "Secure1!",
        "full_name": "User Two",
        "email": "same@test.com",
    })
    assert response.status_code == 400


def test_signup_password_too_short():
    response = client.post("/signup", json={
        "username": "weakpass",
        "password": "abc",
        "full_name": "Weak Pass",
        "email": "weak@test.com",
    })
    assert response.status_code == 422


def test_signup_password_no_uppercase():
    response = client.post("/signup", json={
        "username": "noupper",
        "password": "lowercase1",
        "full_name": "No Upper",
        "email": "noupper@test.com",
    })
    assert response.status_code == 422


def test_signup_password_no_digit():
    response = client.post("/signup", json={
        "username": "nodigit",
        "password": "NoDigitPass",
        "full_name": "No Digit",
        "email": "nodigit@test.com",
    })
    assert response.status_code == 422


def test_signup_invalid_email():
    response = client.post("/signup", json={
        "username": "bademail",
        "password": "Secure1!",
        "full_name": "Bad Email",
        "email": "not-an-email",
    })
    assert response.status_code == 422


def test_signup_role_is_always_player():
    """Ensure users cannot self-assign Admin role."""
    response = client.post("/signup", json={
        "username": "tryadmin",
        "password": "Secure1!",
        "full_name": "Try Admin",
        "email": "tryadmin@test.com",
    })
    assert response.status_code == 200
    token = make_token(username="tryadmin", role="Player")
    with auth(token) as c:
        me = c.get("/me")
    assert me.json()["role"] == "Player"

def test_login_invalid_credentials():
    response = client.post("/login", json={
        "username": "nobody",
        "password_hash": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_missing_fields():
    response = client.post("/login", json={})
    assert response.status_code == 422


def test_login_success():
    # First create a user
    client.post("/signup", json={
        "username": "loginuser",
        "password": "Secure1!",
        "full_name": "Login User",
        "email": "login@test.com",
    })
    response = client.post("/login", json={
        "username": "loginuser",
        "password_hash": "Secure1!",
    })
    assert response.status_code == 200
    assert response.json()["message"] == "login_success"

def test_logout_endpoint():
    response = client.post("/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "logged_out"

def test_read_me_requires_auth():
    response = client.get("/me")
    assert response.status_code == 401


def test_read_me_with_valid_token(player_token):
    with auth(player_token) as c:
        response = c.get("/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "Player"
    assert data["full_name"] == "Test User"

def test_admin_create_user(admin_token):
    with auth(admin_token) as c:
        response = c.post("/user/create", json={
            "username": "createduser",
            "password": "Secure1!",
            "full_name": "Created User",
            "email": "created@test.com",
            "team_id": 1,
            "role": "Player",
        })
    assert response.status_code == 200


def test_admin_create_user_player_rejected(player_token):
    with auth(player_token) as c:
        response = c.post("/user/create", json={
            "username": "sneakyuser",
            "password": "Secure1!",
            "full_name": "Sneaky User",
            "email": "sneaky@test.com",
            "team_id": 1,
            "role": "Player",
        })
    assert response.status_code == 403


def test_admin_create_user_no_auth():
    response = client.post("/user/create", json={
        "username": "noauth",
        "password": "Secure1!",
        "full_name": "No Auth",
        "email": "noauth@test.com",
        "team_id": 1,
        "role": "Player",
    })
    assert response.status_code == 401

def test_get_all_teams():
    response = client.get("/team/")
    assert response.status_code == 200
    assert "Teams" in response.json()


def test_get_nonexistent_team():
    response = client.get("/team/99999")
    assert response.status_code == 404


def test_create_team_as_admin(admin_token):
    with auth(admin_token) as c:
        response = c.post("/team/create", json={"team_name": "Test Team"})
    assert response.status_code == 200
    assert response.json()["team_name"] == "Test Team"


def test_create_team_as_player_rejected(player_token):
    with auth(player_token) as c:
        response = c.post("/team/create", json={"team_name": "Sneaky Team"})
    assert response.status_code == 403


def test_create_team_no_auth():
    response = client.post("/team/create", json={"team_name": "No Auth Team"})
    assert response.status_code == 401


def test_get_team_by_id(admin_token):
    with auth(admin_token) as c:
        create = c.post("/team/create", json={"team_name": "Findable Team"})
    team_id = create.json()["team_id"]
    response = client.get(f"/team/{team_id}")
    assert response.status_code == 200
    assert response.json()["team_name"] == "Findable Team"


def test_update_nonexistent_team(admin_token):
    with auth(admin_token) as c:
        response = c.put("/team/update/99999", json={"team_name": "Ghost"})
    assert response.status_code == 404


def test_update_team_as_player_rejected(player_token):
    with auth(player_token) as c:
        response = c.put("/team/update/1", json={"team_name": "Hacked"})
    assert response.status_code == 403


def test_delete_team_as_admin(admin_token):
    with auth(admin_token) as c:
        create = c.post("/team/create", json={"team_name": "ToDelete"})
        team_id = create.json()["team_id"]
        response = c.delete(f"/team/delete/{team_id}")
    assert response.status_code == 200


def test_delete_nonexistent_team(admin_token):
    with auth(admin_token) as c:
        response = c.delete("/team/delete/99999")
    assert response.status_code == 404


def test_delete_team_as_player_rejected(player_token):
    with auth(player_token) as c:
        response = c.delete("/team/delete/1")
    assert response.status_code == 403

MATCH_PAYLOAD = {
    "location": "Home Ground",
    "date": "2025-06-01",
    "opponent_team_id": 2,
    "home_team_id": 1,
}


def test_get_all_matches():
    response = client.get("/match/")
    assert response.status_code == 200
    assert "Match" in response.json()


def test_get_nonexistent_match():
    response = client.get("/match/99999")
    assert response.status_code == 404


def test_create_match_as_admin(admin_token):
    with auth(admin_token) as c:
        response = c.post("/match/create", json=MATCH_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["location"] == "Home Ground"


def test_create_match_as_player_rejected(player_token):
    with auth(player_token) as c:
        response = c.post("/match/create", json=MATCH_PAYLOAD)
    assert response.status_code == 403


def test_create_match_no_auth():
    response = client.post("/match/create", json=MATCH_PAYLOAD)
    assert response.status_code == 401


def test_get_match_by_id(admin_token):
    with auth(admin_token) as c:
        create = c.post("/match/create", json=MATCH_PAYLOAD)
    match_id = create.json()["match_id"]
    response = client.get(f"/match/{match_id}")
    assert response.status_code == 200
    assert response.json()["match"]["location"] == "Home Ground"


def test_get_matches_by_team(admin_token):
    with auth(admin_token) as c:
        c.post("/match/create", json=MATCH_PAYLOAD)
    response = client.get("/match/team/1")
    assert response.status_code == 200
    assert "user_matches" in response.json()


def test_get_matches_by_team_not_found():
    response = client.get("/match/team/99999")
    assert response.status_code == 404

def test_update_nonexistent_match(admin_token):
    with auth(admin_token) as c:
        response = c.put("/match/update/99999", json=MATCH_PAYLOAD)
    assert response.status_code == 404


def test_update_match_as_player_rejected(player_token):
    with auth(player_token) as c:
        response = c.put("/match/update/1", json=MATCH_PAYLOAD)
    assert response.status_code == 403


def test_delete_match_as_admin(admin_token):
    with auth(admin_token) as c:
        create = c.post("/match/create", json=MATCH_PAYLOAD)
        match_id = create.json()["match_id"]
        response = c.delete(f"/match/delete/{match_id}")
    assert response.status_code == 200


def test_delete_nonexistent_match(admin_token):
    with auth(admin_token) as c:
        response = c.delete("/match/delete/99999")
    assert response.status_code == 404


def test_delete_match_as_player_rejected(player_token):
    with auth(player_token) as c:
        response = c.delete("/match/delete/1")
    assert response.status_code == 403

def test_update_match_report_as_admin(admin_token):
    with auth(admin_token) as c:
        create = c.post("/match/create", json=MATCH_PAYLOAD)
        match_id = create.json()["match_id"]
        response = c.put(f"/match/report/update/{match_id}", json={"match_report": "Great game, won 3-1."})
    assert response.status_code == 200


def test_update_match_report_nonexistent(admin_token):
    with auth(admin_token) as c:
        response = c.put("/match/report/update/99999", json={"match_report": "Ghost report"})
    assert response.status_code == 404


def test_update_match_report_as_player_rejected(player_token):
    with auth(player_token) as c:
        response = c.put("/match/report/update/1", json={"match_report": "Sneaky report"})
    assert response.status_code == 403

def test_create_match_sanitises_location(admin_token):
    with auth(admin_token) as c:
        response = c.post("/match/create", json={**MATCH_PAYLOAD, "location": "<script>alert('xss')</script>"})
    assert response.status_code == 200
    assert "<script>" not in response.json()["location"]


def test_create_team_sanitises_name(admin_token):
    with auth(admin_token) as c:
        response = c.post("/team/create", json={"team_name": "<b>Bold Team</b>"})
    assert response.status_code == 200
    assert "<b>" not in response.json()["team_name"]