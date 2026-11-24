from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import driver_listing_db
from app.schemas.ride_listing import RideListingCreate
from app.routers.driver_listing import (
    require_verified_student,
    require_driver_identity
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        tmp_path / "test_rides.db"
    )

    driver_listing_db.initialize_driver_listing_table()

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def listing_id(client):
    listing = RideListingCreate(
        driver_id=1,
        start_area="FAST Islamabad",
        destination_area="F-10",
        departure_time=datetime.now(timezone.utc)
        + timedelta(hours=2),
        available_seats=3,
        vehicle_details="Honda Civic",
        fare=250
    )

    return driver_listing_db.save_ride_listing(listing)


def valid_update():
    return {
        "start_area": "FAST Islamabad",
        "destination_area": "F-11",
        "departure_time": (
            datetime.now(timezone.utc)
            + timedelta(hours=3)
        ).isoformat(),
        "available_seats": 2,
        "vehicle_details": "Toyota Corolla",
        "fare": 350
    }


# Test 1: Verified driver can edit their own ride
def test_driver_edits_own_listing(client, listing_id):
    app.dependency_overrides[require_verified_student] = lambda: True
    app.dependency_overrides[require_driver_identity] = lambda: 1

    response = client.put(
        f"/ride-listings/{listing_id}",
        json=valid_update()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == listing_id
    assert data["driver_id"] == 1
    assert data["start_area"] == "FAST Islamabad"
    assert data["destination_area"] == "F-11"
    assert data["available_seats"] == 2
    assert data["vehicle_details"] == "Toyota Corolla"
    assert data["fare"] == 350

    saved = driver_listing_db.get_ride_listing(listing_id)

    assert saved["destination_area"] == "F-11"
    assert saved["available_seats"] == 2
    assert saved["fare"] == 350
    assert saved["driver_id"] == 1


# Test 2: Driver cannot edit another driver's ride
def test_driver_cannot_edit_another_listing(client, listing_id):
    app.dependency_overrides[require_verified_student] = lambda: True
    app.dependency_overrides[require_driver_identity] = lambda: 2

    original = driver_listing_db.get_ride_listing(listing_id)

    response = client.put(
        f"/ride-listings/{listing_id}",
        json=valid_update()
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "You can only edit your own ride listings."
    )

    saved = driver_listing_db.get_ride_listing(listing_id)

    assert saved == original


# Test 3: Unverified student cannot edit a ride
def test_unverified_driver_cannot_edit(client, listing_id):
    app.dependency_overrides[require_verified_student] = lambda: False
    app.dependency_overrides[require_driver_identity] = lambda: 1

    original = driver_listing_db.get_ride_listing(listing_id)

    response = client.put(
        f"/ride-listings/{listing_id}",
        json=valid_update()
    )

    assert response.status_code == 403

    assert driver_listing_db.get_ride_listing(listing_id) == original


# Test 4: Invalid ride details are rejected
def test_invalid_update_is_rejected(client, listing_id):
    app.dependency_overrides[require_verified_student] = lambda: True
    app.dependency_overrides[require_driver_identity] = lambda: 1

    original = driver_listing_db.get_ride_listing(listing_id)

    update = valid_update()
    update["start_area"] = " "

    response = client.put(
        f"/ride-listings/{listing_id}",
        json=update
    )

    assert response.status_code == 400

    assert driver_listing_db.get_ride_listing(listing_id) == original


# Test 5: Nonexistent ride cannot be edited
def test_edit_nonexistent_listing(client):
    app.dependency_overrides[require_verified_student] = lambda: True
    app.dependency_overrides[require_driver_identity] = lambda: 1

    response = client.put(
        "/ride-listings/999",
        json=valid_update()
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Ride listing not found."
    )


# Test 6: Missing authentication blocks editing
def test_unconfigured_verification_blocks_editing(client, listing_id):
    original = driver_listing_db.get_ride_listing(listing_id)

    response = client.put(
        f"/ride-listings/{listing_id}",
        json=valid_update()
    )

    assert response.status_code == 503

    assert driver_listing_db.get_ride_listing(listing_id) == original


# Test 7: Missing driver identity blocks editing
def test_missing_driver_identity_blocks_editing(client, listing_id):
    app.dependency_overrides[require_verified_student] = lambda: True

    original = driver_listing_db.get_ride_listing(listing_id)

    response = client.put(
        f"/ride-listings/{listing_id}",
        json=valid_update()
    )

    assert response.status_code == 503

    assert driver_listing_db.get_ride_listing(listing_id) == original


# Test 8: Invalid seat count is rejected
def test_invalid_seat_count_is_rejected(client, listing_id):
    app.dependency_overrides[require_verified_student] = lambda: True
    app.dependency_overrides[require_driver_identity] = lambda: 1

    original = driver_listing_db.get_ride_listing(listing_id)

    update = valid_update()
    update["available_seats"] = 0

    response = client.put(
        f"/ride-listings/{listing_id}",
        json=update
    )

    assert response.status_code == 422

    assert driver_listing_db.get_ride_listing(listing_id) == original