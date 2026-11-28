from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import driver_listing_db
from app.database import passenger_request_db
from app.routers.driver_listing import (
    require_verified_student
)
from app.routers.passenger_requests import (
    require_passenger_identity,
    require_verified_passenger
)
from app.schemas.ride_listing import RideListingCreate


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "test_passenger_requests.db"
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

    driver_listing_db.initialize_driver_listing_table()
    passenger_request_db.initialize_passenger_request_table()

    app.dependency_overrides[require_verified_student] = (
        lambda: True
    )
    app.dependency_overrides[require_passenger_identity] = (
        lambda: 2
    )

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def create_ride(
    driver_id=1,
    seats=3,
    status="active"
):
    listing = RideListingCreate(
        driver_id=driver_id,
        start_area="FAST Islamabad",
        destination_area="F-10",
        departure_time=(
            datetime.now(timezone.utc)
            + timedelta(hours=2)
        ),
        available_seats=seats,
        vehicle_details="Honda Civic",
        fare=250
    )
    listing_id = driver_listing_db.save_ride_listing(listing)

    if status != "active":
        with driver_listing_db.get_connection() as connection:
            connection.execute(
                """
                UPDATE ride_listings
                SET status = ?
                WHERE id = ?
                """,
                (status, listing_id)
            )
            connection.commit()

    return listing_id


def test_unauthenticated_passenger_request_fails_closed(client):
    app.dependency_overrides.pop(require_verified_student, None)
    app.dependency_overrides.pop(require_passenger_identity, None)
    app.dependency_overrides.pop(require_verified_passenger, None)

    response = client.get("/passenger/requests")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Student verification is not configured."
    )


def test_unverified_passenger_is_forbidden(client):
    app.dependency_overrides[require_verified_student] = (
        lambda: False
    )
    app.dependency_overrides.pop(require_passenger_identity, None)
    app.dependency_overrides.pop(require_verified_passenger, None)

    response = client.get("/passenger/requests")

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Only verified FAST students can request rides."
    )


def test_verified_passenger_without_identity_provider_fails_closed(client):
    app.dependency_overrides[require_verified_student] = (
        lambda: True
    )
    app.dependency_overrides.pop(require_passenger_identity, None)
    app.dependency_overrides.pop(require_verified_passenger, None)

    response = client.get("/passenger/requests")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Passenger identity verification is not configured."
    )


def test_successful_request_submission(client):
    listing_id = create_ride()

    response = client.post(
        "/passenger/requests",
        json={"listing_id": listing_id}
    )

    assert response.status_code == 201
    assert response.json()["listing_id"] == listing_id
    assert response.json()["driver_id"] == 1
    assert response.json()["passenger_id"] == 2
    assert response.json()["status"] == "pending"


def test_nonexistent_ride(client):
    response = client.post(
        "/passenger/requests",
        json={"listing_id": 999}
    )

    assert response.status_code == 404


def test_passenger_cannot_request_own_ride(client):
    app.dependency_overrides[require_passenger_identity] = (
        lambda: 1
    )
    listing_id = create_ride(driver_id=1)

    response = client.post(
        "/passenger/requests",
        json={"listing_id": listing_id}
    )

    assert response.status_code == 403


def test_duplicate_pending_request(client):
    listing_id = create_ride()

    first = client.post(
        "/passenger/requests",
        json={"listing_id": listing_id}
    )
    second = client.post(
        "/passenger/requests",
        json={"listing_id": listing_id}
    )

    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.parametrize(
    "status,seats",
    [
        ("cancelled", 3),
        ("completed", 3)
    ]
)
def test_inactive_or_unavailable_ride(
    client,
    status,
    seats
):
    listing = RideListingCreate(
        driver_id=1,
        start_area="FAST Islamabad",
        destination_area="F-10",
        departure_time=(
            datetime.now(timezone.utc)
            + timedelta(hours=2)
        ),
        available_seats=1 if seats == 0 else seats,
        vehicle_details="Honda Civic",
        fare=250
    )
    listing_id = driver_listing_db.save_ride_listing(listing)

    if status != "active":
        with driver_listing_db.get_connection() as connection:
            connection.execute(
                "UPDATE ride_listings SET status = ? WHERE id = ?",
                (status, listing_id)
            )
            connection.commit()

    response = client.post(
        "/passenger/requests",
        json={"listing_id": listing_id}
    )

    assert response.status_code == 409


def test_unavailable_ride(client, monkeypatch):
    listing_id = create_ride()

    listing = driver_listing_db.get_ride_listing(listing_id)
    listing["available_seats"] = 0

    monkeypatch.setattr(
        "app.services.passenger_requests.get_ride_listing",
        lambda _listing_id: listing
    )

    response = client.post(
        "/passenger/requests",
        json={"listing_id": listing_id}
    )

    assert response.status_code == 409


def test_passenger_request_history(client):
    first_listing = create_ride()
    second_listing = create_ride()

    client.post(
        "/passenger/requests",
        json={"listing_id": first_listing}
    )
    client.post(
        "/passenger/requests",
        json={"listing_id": second_listing}
    )

    response = client.get("/passenger/requests")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(
        request["passenger_id"] == 2
        for request in response.json()
    )
