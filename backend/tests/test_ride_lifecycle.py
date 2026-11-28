
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app

from app.database import driver_listing_db
from app.database import passenger_request_db

from app.routers.driver_listing import (
    require_verified_student,
    require_driver_identity
)

from app.schemas.ride_listing import RideListingCreate


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "test_ride_lifecycle.db"

    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        database_path
    )

    monkeypatch.setattr(
        passenger_request_db,
        "DATABASE_PATH",
        database_path
    )

    previous_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[require_verified_student] = (
        lambda: True
    )

    app.dependency_overrides[require_driver_identity] = (
        lambda: 1
    )

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


def create_listing(driver_id=1, past_departure=False):
    if past_departure:
        departure_time = (
            datetime.now(timezone.utc) - timedelta(hours=2)
        )
    else:
        departure_time = (
            datetime.now(timezone.utc) + timedelta(days=1)
        )

    listing = RideListingCreate(
        driver_id=driver_id,
        start_area="G-11",
        destination_area="FAST Islamabad",
        departure_time=departure_time,
        available_seats=3,
        vehicle_details="Toyota Corolla",
        fare=200
    )

    return driver_listing_db.save_ride_listing(listing)


def create_request(listing_id, status="pending"):
    request_id = passenger_request_db.save_passenger_request(
        listing_id=listing_id,
        driver_id=1,
        passenger_id=2,
        created_at=datetime.now(timezone.utc).isoformat()
    )

    if status == "accepted":
        passenger_request_db.process_request_decision(
            driver_id=1,
            request_id=request_id,
            decision="accept"
        )

    elif status == "rejected":
        passenger_request_db.process_request_decision(
            driver_id=1,
            request_id=request_id,
            decision="reject"
        )

    return request_id


def test_cancel_active_ride(client):
    listing_id = create_listing()

    response = client.post(
        f"/ride-listings/{listing_id}/cancel"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    listing = driver_listing_db.get_ride_listing(listing_id)

    assert listing["status"] == "cancelled"


def test_complete_active_ride(client):
    listing_id = create_listing(past_departure=True)

    response = client.post(
        f"/ride-listings/{listing_id}/complete"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"

    listing = driver_listing_db.get_ride_listing(listing_id)

    assert listing["status"] == "completed"


def test_cannot_complete_before_departure(client):
    listing_id = create_listing()

    response = client.post(
        f"/ride-listings/{listing_id}/complete"
    )

    assert response.status_code == 409

    listing = driver_listing_db.get_ride_listing(listing_id)

    assert listing["status"] == "active"


@pytest.mark.parametrize("action", ["cancel", "complete"])
def test_cannot_manage_another_drivers_ride(client, action):
    listing_id = create_listing(
        driver_id=3,
        past_departure=True
    )

    response = client.post(
        f"/ride-listings/{listing_id}/{action}"
    )

    assert response.status_code == 403


@pytest.mark.parametrize("action", ["cancel", "complete"])
def test_nonexistent_ride(client, action):
    response = client.post(
        f"/ride-listings/999/{action}"
    )

    assert response.status_code == 404


@pytest.mark.parametrize("action", ["cancel", "complete"])
def test_invalid_listing_id(client, action):
    response = client.post(
        f"/ride-listings/0/{action}"
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "first_action, second_action",
    [
        ("cancel", "cancel"),
        ("cancel", "complete"),
        ("complete", "complete"),
        ("complete", "cancel")
    ]
)
def test_invalid_status_transitions(
    client,
    first_action,
    second_action
):
    listing_id = create_listing(past_departure=True)

    first_response = client.post(
        f"/ride-listings/{listing_id}/{first_action}"
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/ride-listings/{listing_id}/{second_action}"
    )

    assert second_response.status_code == 409

    history = client.get(
        f"/ride-listings/{listing_id}/history"
    )

    assert len(history.json()) == 1


@pytest.mark.parametrize(
    "request_status",
    ["pending", "accepted"]
)
def test_cancellation_blocked_with_requests(
    client,
    request_status
):
    listing_id = create_listing()

    request_id = create_request(
        listing_id,
        status=request_status
    )

    response = client.post(
        f"/ride-listings/{listing_id}/cancel"
    )

    assert response.status_code == 409

    listing = driver_listing_db.get_ride_listing(listing_id)

    assert listing["status"] == "active"

    request = passenger_request_db.get_passenger_request(
        request_id
    )

    assert request["status"] == request_status

    history = client.get(
        f"/ride-listings/{listing_id}/history"
    )

    assert history.json() == []


def test_completion_blocked_with_pending_requests(client):
    listing_id = create_listing(past_departure=True)

    create_request(listing_id, status="pending")

    response = client.post(
        f"/ride-listings/{listing_id}/complete"
    )

    assert response.status_code == 409

    listing = driver_listing_db.get_ride_listing(listing_id)

    assert listing["status"] == "active"

    history = client.get(
        f"/ride-listings/{listing_id}/history"
    )

    assert history.json() == []


def test_completion_with_accepted_requests(client):
    listing_id = create_listing(past_departure=True)

    request_id = create_request(
        listing_id,
        status="accepted"
    )

    response = client.post(
        f"/ride-listings/{listing_id}/complete"
    )

    assert response.status_code == 200

    request = passenger_request_db.get_passenger_request(
        request_id
    )

    assert request["status"] == "accepted"


def test_cancellation_with_rejected_requests(client):
    listing_id = create_listing()

    create_request(listing_id, status="rejected")

    response = client.post(
        f"/ride-listings/{listing_id}/cancel"
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "action, expected_status",
    [
        ("cancel", "cancelled"),
        ("complete", "completed")
    ]
)
def test_lifecycle_history(client, action, expected_status):
    listing_id = create_listing(past_departure=True)

    response = client.post(
        f"/ride-listings/{listing_id}/{action}"
    )

    assert response.status_code == 200

    history = client.get(
        f"/ride-listings/{listing_id}/history"
    )

    assert history.status_code == 200

    records = history.json()

    assert len(records) == 1
    assert records[0]["listing_id"] == listing_id
    assert records[0]["driver_id"] == 1
    assert records[0]["previous_status"] == "active"
    assert records[0]["new_status"] == expected_status

    changed_at = datetime.fromisoformat(
        records[0]["changed_at"].replace("Z", "+00:00")
    )

    assert changed_at.tzinfo is not None


def test_empty_lifecycle_history(client):
    listing_id = create_listing()

    response = client.get(
        f"/ride-listings/{listing_id}/history"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_another_drivers_history(client):
    listing_id = create_listing(driver_id=3)

    response = client.get(
        f"/ride-listings/{listing_id}/history"
    )

    assert response.status_code == 403


def test_nonexistent_ride_history(client):
    response = client.get(
        "/ride-listings/999/history"
    )

    assert response.status_code == 404


def test_unverified_student(client):
    listing_id = create_listing()

    app.dependency_overrides[require_verified_student] = (
        lambda: False
    )

    response = client.post(
        f"/ride-listings/{listing_id}/cancel"
    )

    assert response.status_code == 403


def test_authentication_not_configured(client):
    listing_id = create_listing()

    app.dependency_overrides.pop(
        require_verified_student
    )

    response = client.post(
        f"/ride-listings/{listing_id}/cancel"
    )

    assert response.status_code == 503


@pytest.mark.parametrize("action", ["cancel", "complete"])
def test_cannot_edit_inactive_ride(client, action):
    listing_id = create_listing(past_departure=True)

    response = client.post(
        f"/ride-listings/{listing_id}/{action}"
    )

    assert response.status_code == 200

    updated_listing = {
        "start_area": "F-10",
        "destination_area": "FAST Islamabad",
        "departure_time": (
            datetime.now(timezone.utc) + timedelta(days=1)
        ).isoformat(),
        "available_seats": 4,
        "vehicle_details": "Honda Civic",
        "fare": 250
    }

    response = client.put(
        f"/ride-listings/{listing_id}",
        json=updated_listing
    )

    assert response.status_code == 409

    listing = driver_listing_db.get_ride_listing(listing_id)

    assert listing["start_area"] == "G-11"
    assert listing["available_seats"] == 3


def test_completed_ride_updates_reliability(client):
    completed_id = create_listing(past_departure=True)
    cancelled_id = create_listing()

    response = client.post(
        f"/ride-listings/{completed_id}/complete"
    )

    assert response.status_code == 200

    response = client.post(
        f"/ride-listings/{cancelled_id}/cancel"
    )

    assert response.status_code == 200

    response = client.get("/drivers/1/reliability")

    assert response.status_code == 200
    assert response.json()["completed_ride_count"] == 1
