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