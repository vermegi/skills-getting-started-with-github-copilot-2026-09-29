from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def activities(monkeypatch):
    test_activities = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_signup_adds_student_to_activity(client, activities):
    activity_name = "Art Club"
    email = "student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}",
        "status": "enrolled",
    }
    assert email in activities[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client, activities):
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_for_existing_participant(client, activities):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activities[activity_name]["participants"].count(email) == 1


def test_unregister_removes_student_from_activity(client, activities):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}",
        "promoted": None,
    }
    assert email not in activities[activity_name]["participants"]


def test_unregister_returns_404_for_unknown_activity(client, activities):
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_404_for_nonparticipant(client, activities):
    activity_name = "Art Club"
    email = "student@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def fill_activity(activities, activity_name):
    activity = activities[activity_name]
    activity["participants"] = [
        f"member{i}@mergington.edu" for i in range(activity["max_participants"])
    ]
    return activity


def test_signup_adds_student_to_waitlist_when_full(client, activities):
    activity_name = "Chess Club"
    email = "waiting@mergington.edu"
    activity = fill_activity(activities, activity_name)

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "waitlisted"
    assert body["waitlist_position"] == 1
    assert email not in activity["participants"]
    assert activity["waitlist"] == [email]
    assert len(activity["participants"]) == activity["max_participants"]


def test_waitlist_positions_increment(client, activities):
    activity_name = "Chess Club"
    fill_activity(activities, activity_name)

    first = client.post(
        f"/activities/{activity_name}/signup", params={"email": "a@mergington.edu"}
    )
    second = client.post(
        f"/activities/{activity_name}/signup", params={"email": "b@mergington.edu"}
    )

    assert first.json()["waitlist_position"] == 1
    assert second.json()["waitlist_position"] == 2
    assert activities[activity_name]["waitlist"] == [
        "a@mergington.edu",
        "b@mergington.edu",
    ]


def test_signup_returns_400_for_already_waitlisted(client, activities):
    activity_name = "Chess Club"
    email = "waiting@mergington.edu"
    activity = fill_activity(activities, activity_name)
    activity["waitlist"] = [email]

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already on the waitlist for this activity"
    }
    assert activity["waitlist"] == [email]


def test_unregister_promotes_first_waitlisted_student(client, activities):
    activity_name = "Chess Club"
    activity = fill_activity(activities, activity_name)
    activity["waitlist"] = ["first@mergington.edu", "second@mergington.edu"]
    leaving = activity["participants"][0]

    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": leaving}
    )

    assert response.status_code == 200
    assert response.json()["promoted"] == "first@mergington.edu"
    assert leaving not in activity["participants"]
    assert "first@mergington.edu" in activity["participants"]
    assert activity["waitlist"] == ["second@mergington.edu"]
    assert len(activity["participants"]) == activity["max_participants"]


def test_unregister_removes_student_from_waitlist(client, activities):
    activity_name = "Chess Club"
    activity = fill_activity(activities, activity_name)
    activity["waitlist"] = ["first@mergington.edu", "second@mergington.edu"]
    participants_before = list(activity["participants"])

    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "first@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed first@mergington.edu from the waitlist for {activity_name}",
        "promoted": None,
    }
    assert activity["waitlist"] == ["second@mergington.edu"]
    assert activity["participants"] == participants_before


def test_get_activities_includes_waitlist(client, activities):
    response = client.get("/activities")

    assert response.status_code == 200
    assert all(details["waitlist"] == [] for details in response.json().values())
