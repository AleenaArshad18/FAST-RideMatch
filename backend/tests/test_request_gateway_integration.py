from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.database import driver_listing_db
from app.database import passenger_request_db
from app.main import app
from app.routers.driver_listing import (
    require_driver_identity,
    require_verified_student
)
from app.schemas.ride_listing import RideListingCreate


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "test_request_gateway.db"
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

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[require_verified_student] = (
        lambda: True
    )
    app.dependency_overrides[require_driver_identity] = (
        lambda: 1
    )

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


def create_ride(driver_id=1, seats=2, status="active"):
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
                "UPDATE ride_listings SET status = ? WHERE id = ?",
                (status, listing_id)
            )
            connection.commit()

    return listing_id


def create_request(listing_id, driver_id=1, passenger_id=2):
    return passenger_request_db.save_passenger_request(
        listing_id=listing_id,
        driver_id=driver_id,
        passenger_id=passenger_id,
        created_at=datetime.now(timezone.utc).isoformat()
    )


def test_driver_request_listing_uses_database_gateway(client):
    first_listing = create_ride(driver_id=1)
    other_listing = create_ride(driver_id=2)
    create_request(first_listing, passenger_id=10)
    create_request(other_listing, driver_id=2, passenger_id=11)

    response = client.get("/driver/requests")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["driver_id"] == 1
    assert response.json()[0]["passenger_id"] == 10


def test_driver_acceptance_allocates_one_seat(client):
    listing_id = create_ride(seats=2)
    request_id = create_request(listing_id)

    response = client.post(
        f"/driver/requests/{request_id}/accept"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert driver_listing_db.get_ride_listing(
        listing_id
    )["available_seats"] == 1


def test_driver_rejection_does_not_allocate_seat(client):
    listing_id = create_ride(seats=2)
    request_id = create_request(listing_id)

    response = client.post(
        f"/driver/requests/{request_id}/reject"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert driver_listing_db.get_ride_listing(
        listing_id
    )["available_seats"] == 2


def test_another_driver_cannot_decide_request(client):
    listing_id = create_ride(driver_id=1)
    request_id = create_request(listing_id, driver_id=1)
    app.dependency_overrides[require_driver_identity] = (
        lambda: 2
    )

    response = client.post(
        f"/driver/requests/{request_id}/accept"
    )

    assert response.status_code == 403
    assert driver_listing_db.get_ride_listing(
        listing_id
    )["available_seats"] == 2


def test_processed_request_cannot_be_decided_twice(client):
    listing_id = create_ride(seats=2)
    request_id = create_request(listing_id)

    first = client.post(
        f"/driver/requests/{request_id}/accept"
    )
    second = client.post(
        f"/driver/requests/{request_id}/accept"
    )

    assert first.status_code == 200
    assert second.status_code == 409
    assert driver_listing_db.get_ride_listing(
        listing_id
    )["available_seats"] == 1


def test_acceptance_rejects_insufficient_seats(client):
    listing_id = create_ride(seats=1)
    first_request = create_request(
        listing_id,
        passenger_id=2
    )
    second_request = create_request(
        listing_id,
        passenger_id=3
    )

    first = client.post(
        f"/driver/requests/{first_request}/accept"
    )
    second = client.post(
        f"/driver/requests/{second_request}/accept"
    )

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["detail"] == (
        "This ride has no available seats."
    )
    assert passenger_request_db.get_request_by_id(
        second_request
    )["status"] == "pending"
    assert driver_listing_db.get_ride_listing(
        listing_id
    )["available_seats"] == 0


def test_concurrent_acceptance_cannot_overbook(client):
    listing_id = create_ride(seats=1)
    request_ids = [
        create_request(listing_id, passenger_id=passenger_id)
        for passenger_id in (2, 3)
    ]

    def accept(request_id):
        return client.post(
            f"/driver/requests/{request_id}/accept"
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(accept, request_ids))

    assert sorted(response.status_code for response in responses) == [
        200,
        409
    ]
    assert driver_listing_db.get_ride_listing(
        listing_id
    )["available_seats"] == 0
    listing_response = client.get(
        f"/ride-listings/{listing_id}"
    )
    assert listing_response.status_code == 200
    assert listing_response.json()["available_seats"] == 0
    statuses = [
        passenger_request_db.get_request_by_id(request_id)["status"]
        for request_id in request_ids
    ]
    assert statuses.count("accepted") == 1
    assert statuses.count("pending") == 1


def test_inactive_ride_cannot_be_accepted(client):
    listing_id = create_ride(status="cancelled")
    request_id = create_request(listing_id)

    response = client.post(
        f"/driver/requests/{request_id}/accept"
    )

    assert response.status_code == 409
    assert passenger_request_db.get_request_by_id(
        request_id
    )["status"] == "pending"
    assert driver_listing_db.get_ride_listing(
        listing_id
    )["available_seats"] == 2
