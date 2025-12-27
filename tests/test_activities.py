import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    # restore original state after each test
    activities.clear()
    activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    email = "alice@example.com"
    activity = "Basketball Team"

    # signup
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # participant should be present
    r = client.get("/activities")
    assert email in r.json()[activity]["participants"]

    # unregister
    r = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r.status_code == 200
    assert "Unregistered" in r.json().get("message", "")

    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]


def test_signup_duplicate():
    email = "bob@example.com"
    activity = "Swimming Club"

    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200

    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400


def test_unregister_not_signed():
    email = "nobody@example.com"
    activity = "Art Studio"

    r = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r.status_code == 400


def test_activity_not_found():
    r = client.post("/activities/NonExistent/signup?email=a@b.com")
    assert r.status_code == 404

    r = client.post("/activities/NonExistent/unregister?email=a@b.com")
    assert r.status_code == 404
