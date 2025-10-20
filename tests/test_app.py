import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    email = "test_student@mergington.edu"
    activity = "Chess Club"
    
    # Try to signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    
    # Verify student was added
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]
    
    # Try to signup again (should fail)
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    
    # Clean up - unregister the test student
    client.delete(f"/activities/{activity}/unregister", params={"email": email})

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    email = "test_student@mergington.edu"
    activity = "Programming Class"
    
    # First sign up
    client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Then unregister
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    
    # Verify student was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]
    
    # Try to unregister again (should fail)
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonExistentClub/signup", 
                         params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonExistentClub/unregister", 
                          params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]