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
from app.routers.driver_requests import require_verified_driver
from app.routers.passenger_requests import (
    require_passenger_identity
)
from app.schemas.ride_listing import RideListingCreate


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "test_payments.db"

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
    app.dependency_overrides[require_passenger_identity] = (
        lambda: 2
    )

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


def create_ride(fare=900, seats=3):
    listing = RideListingCreate(
        driver_id=1,
        start_area="FAST Islamabad",
        destination_area="F-10",
        departure_time=(
            datetime.now(timezone.utc)
            + timedelta(hours=2)
        ),
        available_seats=seats,
        vehicle_details="Honda Civic",
        fare=fare
    )

    return driver_listing_db.save_ride_listing(listing)


def create_request(listing_id, passenger_id):
    return passenger_request_db.save_passenger_request(
        listing_id=listing_id,
        driver_id=1,
        passenger_id=passenger_id,
        created_at=datetime.now(timezone.utc).isoformat()
    )


def accept_request(client, request_id):
    return client.post(
        f"/driver/requests/{request_id}/accept"
    )


def test_accepting_request_creates_payment_record(client):
    listing_id = create_ride(fare=900)
    request_id = create_request(listing_id, passenger_id=2)

    response = accept_request(client, request_id)

    assert response.status_code == 200

    history = client.get("/passenger/payments")

    assert history.status_code == 200
    assert len(history.json()) == 1

    payment = history.json()[0]

    assert payment["request_id"] == request_id
    assert payment["listing_id"] == listing_id
    assert payment["driver_id"] == 1
    assert payment["passenger_id"] == 2
    assert payment["total_fare"] == 900
    assert payment["accepted_passengers"] == 1
    assert payment["amount"] == 900
    assert payment["status"] == "pending"


def test_fare_is_split_between_accepted_passengers(client):
    listing_id = create_ride(fare=900)

    first_request = create_request(listing_id, 2)
    second_request = create_request(listing_id, 3)

    first_acceptance = accept_request(client, first_request)
    assert first_acceptance.status_code == 200

    second_acceptance = accept_request(client, second_request)
    assert second_acceptance.status_code == 200

    app.dependency_overrides[require_passenger_identity] = (
        lambda: 2
    )
    first_payment = client.get(
        f"/passenger/payments/{first_request}"
    )

    app.dependency_overrides[require_passenger_identity] = (
        lambda: 3
    )
    second_payment = client.get(
        f"/passenger/payments/{second_request}"
    )

    assert first_payment.status_code == 200
    assert second_payment.status_code == 200

    assert first_payment.json()["amount"] == 450
    assert second_payment.json()["amount"] == 450

    assert first_payment.json()["accepted_passengers"] == 2
    assert second_payment.json()["accepted_passengers"] == 2


def test_fare_split_handles_remainder_in_paisa(client):
    listing_id = create_ride(fare=1000, seats=3)

    request_ids = [
        create_request(listing_id, passenger_id)
        for passenger_id in (2, 3, 4)
    ]

    for request_id in request_ids:
        response = accept_request(client, request_id)
        assert response.status_code == 200

    amounts = []

    for passenger_id, request_id in zip(
        (2, 3, 4),
        request_ids
    ):
        app.dependency_overrides[require_passenger_identity] = (
            lambda passenger_id=passenger_id: passenger_id
        )

        response = client.get(
            f"/passenger/payments/{request_id}"
        )

        assert response.status_code == 200
        amounts.append(round(response.json()["amount"], 2))

    assert amounts == [333.34, 333.33, 333.33]
    assert round(sum(amounts), 2) == 1000


def test_passenger_can_view_payment_details(client):
    listing_id = create_ride()
    request_id = create_request(listing_id, 2)

    accept_request(client, request_id)

    response = client.get(
        f"/passenger/payments/{request_id}"
    )

    assert response.status_code == 200
    assert response.json()["request_id"] == request_id
    assert response.json()["start_area"] == "FAST Islamabad"
    assert response.json()["destination_area"] == "F-10"


def test_passenger_cannot_view_another_passengers_payment(client):
    listing_id = create_ride()
    request_id = create_request(listing_id, 3)

    accept_request(client, request_id)

    response = client.get(
        f"/passenger/payments/{request_id}"
    )

    assert response.status_code == 404


def test_rejected_request_does_not_create_payment(client):
    listing_id = create_ride()
    request_id = create_request(listing_id, 2)

    response = client.post(
        f"/driver/requests/{request_id}/reject"
    )

    assert response.status_code == 200

    history = client.get("/passenger/payments")

    assert history.status_code == 200
    assert history.json() == []


def test_driver_can_update_payment_status(client):
    listing_id = create_ride()
    request_id = create_request(listing_id, 2)

    accept_request(client, request_id)

    response = client.patch(
        f"/driver/payments/{request_id}/status",
        json={"status": "paid"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "paid"


def test_another_driver_cannot_update_payment_status(client):
    listing_id = create_ride()
    request_id = create_request(listing_id, 2)

    accept_request(client, request_id)

    app.dependency_overrides[require_driver_identity] = (
        lambda: 99
    )

    response = client.patch(
        f"/driver/payments/{request_id}/status",
        json={"status": "paid"}
    )

    assert response.status_code == 404


def test_passenger_cannot_update_payment_status(client):
    listing_id = create_ride()
    request_id = create_request(listing_id, 2)

    accept_request(client, request_id)

    response = client.patch(
        f"/passenger/payments/{request_id}/status",
        json={"status": "paid"}
    )

    assert response.status_code == 404


def test_payment_history_only_contains_passengers_records(client):
    listing_id = create_ride()

    first_request = create_request(listing_id, 2)
    second_request = create_request(listing_id, 3)

    accept_request(client, first_request)
    accept_request(client, second_request)

    app.dependency_overrides[require_passenger_identity] = (
        lambda: 3
    )

    response = client.get("/passenger/payments")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["passenger_id"] == 3


def test_nonexistent_payment_returns_404(client):
    response = client.get("/passenger/payments/999")

    assert response.status_code == 404