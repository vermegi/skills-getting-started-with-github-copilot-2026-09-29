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


def test_get_activities_search_is_case_insensitive(client, activities):
    response = client.get("/activities", params={"search": "CHESS"})

    assert response.status_code == 200
    assert list(response.json()) == ["Chess Club"]


def test_get_activities_filters_by_schedule_day(client, activities):
    response = client.get("/activities", params={"day": "Wednesday"})

    assert response.status_code == 200
    assert set(response.json()) == {"Gym Class", "Volleyball Club", "Art Club"}


def test_get_activities_combines_search_and_schedule_filters(client, activities):
    response = client.get(
        "/activities", params={"search": "class", "day": "Thursday"}
    )

    assert response.status_code == 200
    assert list(response.json()) == ["Programming Class"]


def test_signup_adds_student_to_activity(client, activities):
    activity_name = "Art Club"
    email = "student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
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
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
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