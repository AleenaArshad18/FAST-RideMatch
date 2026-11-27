
from datetime import datetime, timedelta, timezone

import pytest

from fastapi.testclient import TestClient

from app.main import app

from app.database import driver_listing_db

from app.database.driver_reliability_db import (
    get_completed_ride_count
)

from app.schemas.ride_listing import RideListingCreate

from app.services.driver_reliability import (
    get_driver_reliability
)

from app.services.passenger_discovery import (
    search_and_filter_rides
)

from app.routers.driver_listing import (
    require_verified_student
)


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    test_db = tmp_path / "test_reliability.db"

    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        test_db
    )

    driver_listing_db.initialize_driver_listing_table()

    yield test_db


@pytest.fixture
def verified_client(test_database):
    previous_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[
        require_verified_student
    ] = lambda: True

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(
            previous_overrides
        )


def create_test_ride(driver_id, status="active"):
    listing = RideListingCreate(
        driver_id=driver_id,
        start_area="Islamabad",
        destination_area="FAST University",
        departure_time=(
            datetime.now(timezone.utc)
            + timedelta(hours=2)
        ),
        available_seats=3,
        vehicle_details="Toyota Corolla",
        fare=300
    )

    listing_id = driver_listing_db.save_ride_listing(
        listing
    )

    # Set ride status directly for testing only.
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


def test_new_ride_has_active_status(test_database):
    listing_id = create_test_ride(driver_id=1)

    listing = driver_listing_db.get_ride_listing(
        listing_id
    )

    assert listing["status"] == "active"


def test_count_completed_rides(test_database):
    create_test_ride(1, "completed")
    create_test_ride(1, "completed")
    create_test_ride(1, "completed")

    assert get_completed_ride_count(1) == 3


def test_exclude_active_and_cancelled_rides(test_database):
    create_test_ride(1, "completed")
    create_test_ride(1, "active")
    create_test_ride(1, "cancelled")

    assert get_completed_ride_count(1) == 1


def test_exclude_other_drivers_rides(test_database):
    create_test_ride(1, "completed")
    create_test_ride(2, "completed")
    create_test_ride(2, "completed")

    assert get_completed_ride_count(1) == 1
    assert get_completed_ride_count(2) == 2


def test_driver_with_no_recorded_rides(test_database):
    assert get_completed_ride_count(1) == 0


def test_reliability_service(test_database):
    create_test_ride(1, "completed")
    create_test_ride(1, "completed")

    result = get_driver_reliability(1)

    assert result.driver_id == 1
    assert result.completed_ride_count == 2
    assert result.average_rating is None


def test_invalid_driver_id_service(test_database):
    with pytest.raises(ValueError):
        get_driver_reliability(0)


def test_reliability_api(verified_client):
    create_test_ride(1, "completed")
    create_test_ride(1, "completed")
    create_test_ride(1, "cancelled")

    response = verified_client.get(
        "/drivers/1/reliability"
    )

    assert response.status_code == 200

    assert response.json() == {
        "driver_id": 1,
        "completed_ride_count": 2,
        "average_rating": None
    }


def test_reliability_api_no_recorded_rides(
    verified_client
):
    response = verified_client.get(
        "/drivers/1/reliability"
    )

    assert response.status_code == 200

    assert response.json() == {
        "driver_id": 1,
        "completed_ride_count": 0,
        "average_rating": None
    }


def test_invalid_driver_id_api(verified_client):
    response = verified_client.get(
        "/drivers/0/reliability"
    )

    assert response.status_code == 422


def test_unverified_student_rejected(test_database):
    previous_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[
        require_verified_student
    ] = lambda: False

    try:
        with TestClient(app) as client:
            response = client.get(
                "/drivers/1/reliability"
            )

            assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(
            previous_overrides
        )


def test_missing_authentication_rejected(test_database):
    previous_overrides = app.dependency_overrides.copy()

    app.dependency_overrides.pop(
        require_verified_student,
        None
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                "/drivers/1/reliability"
            )

            assert response.status_code == 503
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(
            previous_overrides
        )


def test_discovery_excludes_inactive_rides(test_database):
    active_id = create_test_ride(1, "active")

    create_test_ride(1, "completed")
    create_test_ride(1, "cancelled")

    rides = driver_listing_db.get_all_ride_listings()

    results = search_and_filter_rides(rides)

    assert len(results) == 1
    assert results[0]["id"] == active_id


def test_existing_database_migration(
    tmp_path,
    monkeypatch
):
    test_db = tmp_path / "legacy_database.db"

    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        test_db
    )

    # Create the original table without status.
    with driver_listing_db.get_connection() as connection:
        connection.execute("""
            CREATE TABLE ride_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                start_area TEXT NOT NULL,
                destination_area TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                available_seats INTEGER NOT NULL,
                vehicle_details TEXT NOT NULL,
                fare REAL NOT NULL
            )
        """)

        connection.execute("""
            INSERT INTO ride_listings (
                driver_id,
                start_area,
                destination_area,
                departure_time,
                available_seats,
                vehicle_details,
                fare
            )
            VALUES (
                1,
                'Islamabad',
                'FAST University',
                '2030-01-01T10:00:00+00:00',
                3,
                'Toyota Corolla',
                300
            )
        """)

        connection.commit()

    # Run migration twice to ensure it is repeatable.
    driver_listing_db.initialize_driver_listing_table()
    driver_listing_db.initialize_driver_listing_table()

    listing = driver_listing_db.get_ride_listing(1)

    assert listing is not None
    assert listing["driver_id"] == 1
    assert listing["start_area"] == "Islamabad"
    assert listing["status"] == "active"
    assert get_completed_ride_count(1) == 0
