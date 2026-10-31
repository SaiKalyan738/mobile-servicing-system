
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

import backend.database as database
from backend.main import app

client = TestClient(app)


# --------------------------------------------------
# Separate test database
# --------------------------------------------------

@pytest.fixture(autouse=True)
def test_database(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_mobile_servicing.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_db_path
    )

    database.create_table()


# --------------------------------------------------
# Test case ID fixture
# --------------------------------------------------

@pytest.fixture
def test_case_ids():
    return []


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def create_test_service(test_case_ids):
    case_id = f"CASE-TEST-{uuid4().hex[:10]}"
    test_case_ids.append(case_id)

    response = client.post(
        "/services",
        json={
            "case_id": case_id,
            "device_model": "Test Phone",
            "issue_description": "Automated test repair request"
        }
    )

    assert response.status_code == 201

    return response.json()["service"]


# --------------------------------------------------
# Basic API tests
# --------------------------------------------------

def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Mobile Servicing API is running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_track_nonexistent_service():
    identifier = f"SRV-MISSING-{uuid4().hex[:8]}"

    response = client.get(f"/track/{identifier}")

    assert response.status_code == 404


# --------------------------------------------------
# Service creation tests
# --------------------------------------------------

def test_create_service_request(test_case_ids):
    service = create_test_service(test_case_ids)

    assert service["case_id"] == test_case_ids[0]
    assert service["current_status"] == "Received"
    assert service["service_id"].startswith("SRV-")


def test_duplicate_case_id_rejected(test_case_ids):
    case_id = f"CASE-TEST-{uuid4().hex[:10]}"

    payload = {
        "case_id": case_id,
        "device_model": "Test Phone",
        "issue_description": "Duplicate request test"
    }

    first_response = client.post("/services", json=payload)
    second_response = client.post("/services", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_reject_invalid_service_input():
    response = client.post(
        "/services",
        json={
            "case_id": "X",
            "device_model": "A",
            "issue_description": "Bad"
        }
    )

    assert response.status_code == 422


# --------------------------------------------------
# Repair tracking tests
# --------------------------------------------------

def test_track_newly_created_service(test_case_ids):
    service = create_test_service(test_case_ids)

    response = client.get(
        f"/track/{service['service_id']}"
    )

    assert response.status_code == 200
    assert response.json()["service"]["case_id"] == service["case_id"]


# --------------------------------------------------
# Repair status tests
# --------------------------------------------------

'''def test_update_repair_status(test_case_ids):
    service = create_test_service(test_case_ids)
    service_id = service["service_id"]

    response = client.patch(
        f"/services/{service_id}/status",
        params={"new_status": "Repair in Progress"}
    )

    assert response.status_code == 200
    assert response.json()["current_status"] == "Repair in Progress"

    tracking_response = client.get(f"/track/{service_id}")

    assert tracking_response.status_code == 200
    assert (
        tracking_response.json()["service"]["current_status"]
        == "Repair in Progress"
    )'''

def test_update_repair_status(test_case_ids):
    service = create_test_service(test_case_ids)
    service_id = service["service_id"]

    # First transition: Received -> Diagnosis
    first_response = client.patch(
        f"/services/{service_id}/status",
        params={"new_status": "Diagnosis"}
    )

    assert first_response.status_code == 200
    assert first_response.json()["current_status"] == "Diagnosis"

    # Second transition: Diagnosis -> Repair in Progress
    response = client.patch(
        f"/services/{service_id}/status",
        params={"new_status": "Repair in Progress"}
    )

    assert response.status_code == 200
    assert response.json()["current_status"] == "Repair in Progress"

    # Verify the updated status is saved
    tracking_response = client.get(f"/track/{service_id}")

    assert tracking_response.status_code == 200
    assert (
        tracking_response.json()["service"]["current_status"]
        == "Repair in Progress"
    )


def test_reject_invalid_status_transition(test_case_ids):
    service = create_test_service(test_case_ids)

    # Received cannot directly become Ready for Collection
    response = client.patch(
        f"/services/{service['service_id']}/status",
        params={"new_status": "Ready for Collection"}
    )

    assert response.status_code == 400

    # Verify the original status has not changed
    tracking_response = client.get(
        f"/track/{service['service_id']}"
    )

    assert tracking_response.status_code == 200
    assert (
        tracking_response.json()["service"]["current_status"]
        == "Received"
    )


def test_reject_invalid_repair_status(test_case_ids):
    service = create_test_service(test_case_ids)

    response = client.patch(
        f"/services/{service['service_id']}/status",
        params={"new_status": "Broken"}
    )

    assert response.status_code == 400


def test_update_nonexistent_service():
    service_id = f"SRV-MISSING-{uuid4().hex[:8]}"

    response = client.patch(
        f"/services/{service_id}/status",
        params={"new_status": "Diagnosis"}
    )

    assert response.status_code == 404



def test_initial_service_status_is_recorded(test_case_ids):
    service = create_test_service(test_case_ids)

    response = client.get(
        f"/services/{service['service_id']}/history"
    )

    assert response.status_code == 200

    history = response.json()["history"]

    assert len(history) == 1
    assert history[0]["old_status"] is None
    assert history[0]["new_status"] == "Received"
    assert history[0]["changed_at"]



def test_status_change_is_recorded(test_case_ids):
    service = create_test_service(test_case_ids)
    service_id = service["service_id"]

    response = client.patch(
        f"/services/{service_id}/status",
        params={"new_status": "Diagnosis"}
    )

    assert response.status_code == 200

    history_response = client.get(
        f"/services/{service_id}/history"
    )

    assert history_response.status_code == 200

    history = history_response.json()["history"]

    assert len(history) == 2
    assert history[1]["old_status"] == "Received"
    assert history[1]["new_status"] == "Diagnosis"
    assert history[1]["changed_at"] 



def test_history_for_nonexistent_service():
    service_id = f"SRV-MISSING-{uuid4().hex[:8]}"

    response = client.get(
        f"/services/{service_id}/history"
    )

    assert response.status_code == 404
