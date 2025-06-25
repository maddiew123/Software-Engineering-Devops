from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# def test_signup_and_login():
#     # Signup
#     signup_data = {
#         "username": "testuser1",
#         "password": "testpass123",
#         "full_name": "Test User",
#         "email": "testuser1@example.com",
#         "team_id": 1
#     }
#     response = client.post("/signup", json=signup_data)
#     assert response.status_code == 200
#     assert "user_id" in response.json()

#     # Login
#     login_data = {
#         "username": "testuser1",
#         "password_hash": "testpass123"
#     }
#     response = client.post("/login", json=login_data)
#     assert response.status_code == 200
#     assert response.json()["message"] == "login_success"

# def test_team_crud():
#     # Create team
#     response = client.post("/team/create", json={"team_name": "Test Team"})
#     assert response.status_code == 200
#     team_id = response.json()["team_id"]

#     # Get team
#     response = client.get(f"/team/{team_id}")
#     assert response.status_code == 200
#     assert response.json()["team_name"] == "Test Team"

#     # Update team
#     response = client.put(f"/team/update/{team_id}", json={"team_name": "Updated Team"})
#     assert response.status_code == 200
#     assert response.json()["team_name"] == "Updated Team"

#     # Delete team
#     response = client.delete(f"/team/delete/{team_id}")
#     assert response.status_code == 200

def test_match_crud():
    match_data = {
        "location": "Test City",
        "date": "2025-12-25",
        "opponent_team_id": 1,
        "home_team_id": 2
    }
    # Create
    response = client.post("/match/create", json=match_data)
    assert response.status_code == 200
    match_id = response.json()["match_id"]

    # Update
    update_data = {
        "location": "Updated City",
        "date": "2025-12-31",
        "opponent_team_id": 2,
        "home_team_id": 1
    }
    response = client.put(f"/match/update/{match_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["location"] == "Updated City"

    # Report update
    response = client.put(f"/match/report/update/{match_id}", json={"match_report": "This is a test report."})
    assert response.status_code == 200
    assert response.json()["match_report"] == "This is a test report."

    # Delete
    response = client.delete(f"/match/delete/{match_id}")
    assert response.status_code == 200

def test_get_match_by_team():
    response = client.get("/match/team/1")
    assert response.status_code == 200
    assert "user_match" in response.json()
