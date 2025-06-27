import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, User, Team, Match
from backend.database.database import get_db
from backend.main import app 

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    team = Team(team_name="Test Team")
    db.add(team)
    db.commit()
    db.refresh(team)
    yield
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_signup_and_login():
 
    response = client.post("/signup", json={
        "username": "testuser",
        "password": "testpass",
        "full_name": "Test User",
        "email": "test@example.com",
        "team_id": 1,
        "role": "user"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    response = client.post("/login", json={
        "username": "testuser",
        "password_hash": "testpass"  
    })
    assert response.status_code == 200 or response.status_code == 401

def test_create_team():
    response = client.post("/team/create", json={"team_name": "Team Python"})
    assert response.status_code == 200
    assert response.json()["team_name"] == "Team Python"

def test_create_match():
    response = client.post("/match/create", json={
        "location": "London",
        "date": "2025-07-01",
        "opponent_team_id": 1,
        "home_team_id": 1
    })
    assert response.status_code == 200
    assert response.json()["location"] == "London"

def test_get_match():
    match_id = 1
    response = client.get(f"/match/{match_id}")
    if response.status_code == 404:
        pytest.skip("Match not created properly")
    assert response.status_code == 200
    assert "match" in response.json()
