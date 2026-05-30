import copy

from fastapi.testclient import TestClient

from src.app import app, activities

original_activities = copy.deepcopy(activities)
client = TestClient(app)


def reset_activities_state():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activities():
    # Arrange
    expected_activity = "Chess Club"
    reset_activities_state()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    reset_activities_state()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_existing_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    reset_activities_state()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "testremove@mergington.edu"
    reset_activities_state()
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_400():
    # Arrange
    activity_name = "Programming Class"
    email = "missing@mergington.edu"
    reset_activities_state()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"
