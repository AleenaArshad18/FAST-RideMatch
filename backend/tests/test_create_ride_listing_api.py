
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import driver_listing_db
from app.routers.driver_listing import require_verified_student


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        tmp_path / "test_rides.db"
    )
    driver_listing_db.initialize_driver_listing_table()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def valid_listing():
    return {
        "driver_id": 1,
        "start_area": "FAST Islamabad",
        "destination_area": "F-10",
        "departure_time": (
            datetime.now(timezone.utc)
            + timedelta(hours=2)
        ).isoformat(),
        "available_seats": 3,
        "vehicle_details": "Honda Civic",
        "fare": 250
    }


def test_verified_driver_creates_listing(client):
    app.dependency_overrides[require_verified_student] = lambda: True

    response = client.post("/ride-listings", json=valid_listing())

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["driver_id"] == 1

    saved = driver_listing_db.get_ride_listing(data["id"])
    assert saved is not None


def test_invalid_listing_is_rejected(client):
    app.dependency_overrides[require_verified_student] = lambda: True

    listing = valid_listing()
    listing["start_area"] = " "

    response = client.post("/ride-listings", json=listing)

    assert response.status_code == 400


def test_unconfigured_verification_blocks_creation(client):
    response = client.post("/ride-listings", json=valid_listing())

    assert response.status_code == 503

def test_unverified_driver_cannot_create_listing(client):
    app.dependency_overrides[require_verified_student] = lambda: False

    response = client.post(
        "/ride-listings",
        json=valid_listing()
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only verified FAST students can offer rides."
    )

    # Verify that the rejected listing was not saved
    with driver_listing_db.get_connection() as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM ride_listings"
        ).fetchone()[0]

    assert count == 0
