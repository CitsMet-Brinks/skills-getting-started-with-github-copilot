"""Tests for the FastAPI activities application"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_root_redirect(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    
    # Verify Chess Club has expected participants
    assert activities["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu"
    ]


def test_signup_new_participant(client):
    """Test signing up a new participant for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "alice@mergington.edu"}
    )
    assert response.status_code == 200
    assert "Signed up alice@mergington.edu for Chess Club" in response.json()["message"]


def test_signup_already_registered(client):
    """Test signing up a participant who is already registered"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "alice@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_appears_in_activities_list(client):
    """Test that a newly signed-up participant appears in the activities list"""
    # Sign up
    signup_response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": "bob@mergington.edu"}
    )
    assert signup_response.status_code == 200
    
    # Verify in activities list
    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    activities = activities_response.json()
    assert "bob@mergington.edu" in activities["Basketball Team"]["participants"]


def test_unregister_participant(client):
    """Test unregistering a participant from an activity"""
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 200
    assert "Unregistered michael@mergington.edu from Chess Club" in response.json()["message"]


def test_unregister_not_registered(client):
    """Test unregistering a participant who is not registered"""
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_unregister_nonexistent_activity(client):
    """Test unregistering from an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Activity/unregister",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_appears_in_activities_list(client):
    """Test that an unregistered participant is removed from the activities list"""
    # Unregister
    unregister_response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "daniel@mergington.edu"}
    )
    assert unregister_response.status_code == 200
    
    # Verify removed from activities list
    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    activities = activities_response.json()
    assert "daniel@mergington.edu" not in activities["Chess Club"]["participants"]


def test_activity_details(client):
    """Test that activity details are returned correctly"""
    response = client.get("/activities")
    activities = response.json()
    
    chess_club = activities["Chess Club"]
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess_club["max_participants"] == 12
    assert len(chess_club["participants"]) == 2


def test_multiple_signups_and_unregistrations(client):
    """Test multiple operations in sequence"""
    # Sign up multiple people
    for email in ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]:
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all signed up
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert len(activities["Tennis Club"]["participants"]) == 3
    
    # Unregister one
    response = client.post(
        "/activities/Tennis Club/unregister",
        params={"email": "bob@mergington.edu"}
    )
    assert response.status_code == 200
    
    # Verify correct removal
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert len(activities["Tennis Club"]["participants"]) == 2
    assert "bob@mergington.edu" not in activities["Tennis Club"]["participants"]
    assert "alice@mergington.edu" in activities["Tennis Club"]["participants"]
    assert "charlie@mergington.edu" in activities["Tennis Club"]["participants"]
