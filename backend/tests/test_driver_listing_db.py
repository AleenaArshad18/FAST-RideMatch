from datetime import datetime, timedelta, timezone

from app.schemas.ride_listing import (
    RideListingCreate,
    RideListingUpdate
)
from app.database import driver_listing_db


def test_save_and_retrieve_listing(tmp_path, monkeypatch):
    # Use an isolated temporary SQLite database
    test_db = tmp_path / "test_ride_match.db"

    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        test_db
    )

    driver_listing_db.initialize_driver_listing_table()

    listing = RideListingCreate(
        driver_id=1,
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

    listing_id = driver_listing_db.save_ride_listing(listing)

    saved_listing = driver_listing_db.get_ride_listing(
        listing_id
    )

    assert listing_id > 0
    assert saved_listing is not None
    assert saved_listing["id"] == listing_id
    assert saved_listing["driver_id"] == 1
    assert saved_listing["start_area"] == "Islamabad"
    assert saved_listing["destination_area"] == "FAST University"
    assert saved_listing["available_seats"] == 3
    assert saved_listing["vehicle_details"] == "Toyota Corolla"
    assert saved_listing["fare"] == 300
    assert saved_listing["departure_time"] == (
        listing.departure_time.isoformat()
    )


def test_update_ride_listing(tmp_path, monkeypatch):
    # Use a separate test database
    test_db = tmp_path / "test_ride_match.db"

    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        test_db
    )

    driver_listing_db.initialize_driver_listing_table()

    # Create the original ride
    listing = RideListingCreate(
        driver_id=1,
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

    listing_id = driver_listing_db.save_ride_listing(listing)

    # Prepare updated ride details
    updated_listing = RideListingUpdate(
        start_area="F-10 Markaz",
        destination_area="FAST University",
        departure_time=(
            datetime.now(timezone.utc)
            + timedelta(hours=4)
        ),
        available_seats=2,
        vehicle_details="Honda Civic",
        fare=400
    )

    result = driver_listing_db.update_ride_listing(
        listing_id,
        updated_listing
    )

    saved_listing = driver_listing_db.get_ride_listing(
        listing_id
    )

    # Verify that the update was successful
    assert result is True
    assert saved_listing is not None
    assert saved_listing["id"] == listing_id

    # Verify that ownership remains unchanged
    assert saved_listing["driver_id"] == 1

    # Verify updated information
    assert saved_listing["start_area"] == "F-10 Markaz"
    assert saved_listing["destination_area"] == "FAST University"
    assert saved_listing["available_seats"] == 2
    assert saved_listing["vehicle_details"] == "Honda Civic"
    assert saved_listing["fare"] == 400
    assert saved_listing["departure_time"] == (
        updated_listing.departure_time.isoformat()
    )


def test_retrieve_nonexistent_listing(tmp_path, monkeypatch):
    test_db = tmp_path / "test_ride_match.db"

    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        test_db
    )

    driver_listing_db.initialize_driver_listing_table()

    # Attempt to retrieve a ride that does not exist
    result = driver_listing_db.get_ride_listing(999)

    assert result is None


def test_update_nonexistent_listing(tmp_path, monkeypatch):
    test_db = tmp_path / "test_ride_match.db"

    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        test_db
    )

    driver_listing_db.initialize_driver_listing_table()

    updated_listing = RideListingUpdate(
        start_area="Islamabad",
        destination_area="FAST University",
        departure_time=(
            datetime.now(timezone.utc)
            + timedelta(hours=3)
        ),
        available_seats=2,
        vehicle_details="Honda Civic",
        fare=350
    )

    # Attempt to update a ride that does not exist
    result = driver_listing_db.update_ride_listing(
        999,
        updated_listing
    )

    assert result is False
    assert driver_listing_db.get_ride_listing(999) is None


def test_initialize_migrates_listings_to_allow_zero_seats(
    tmp_path,
    monkeypatch
):
    test_db = tmp_path / "legacy_ride_match.db"
    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        test_db
    )

    with driver_listing_db.get_connection() as connection:
        connection.execute("""
            CREATE TABLE ride_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                start_area TEXT NOT NULL,
                destination_area TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                available_seats INTEGER NOT NULL
                    CHECK (available_seats > 0),
                vehicle_details TEXT NOT NULL,
                fare REAL NOT NULL
                    CHECK (fare >= 0)
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
            VALUES (1, 'A', 'B', '2030-01-01T10:00:00+00:00', 1, 'Car', 10)
        """)
        connection.execute("""
            CREATE TABLE ride_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                driver_id INTEGER NOT NULL,
                passenger_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY (listing_id) REFERENCES ride_listings(id)
            )
        """)
        connection.execute("""
            INSERT INTO ride_requests (
                listing_id,
                driver_id,
                passenger_id,
                created_at
            )
            VALUES (1, 1, 2, '2030-01-01T09:00:00+00:00')
        """)
        connection.commit()

    driver_listing_db.initialize_driver_listing_table()

    with driver_listing_db.get_connection() as connection:
        connection.execute(
            "UPDATE ride_listings SET available_seats = 0 WHERE id = 1"
        )
        connection.commit()

    migrated = driver_listing_db.get_ride_listing(1)
    assert migrated is not None
    assert migrated["available_seats"] == 0
    assert migrated["status"] == "active"

    with driver_listing_db.get_connection() as connection:
        request = connection.execute(
            "SELECT listing_id FROM ride_requests WHERE id = 1"
        ).fetchone()
        foreign_key = connection.execute(
            "PRAGMA foreign_key_list(ride_requests)"
        ).fetchone()
        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

    assert request["listing_id"] == 1
    assert foreign_key["table"] == "ride_listings"
    assert violations == []