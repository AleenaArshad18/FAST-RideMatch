
from datetime import datetime, timedelta, timezone

from app.schemas.ride_listing import RideListingCreate
from app.database import driver_listing_db


def test_save_and_retrieve_listing(tmp_path, monkeypatch):
    # Use an isolated temporary SQLite database
    test_db = tmp_path / "test_ride_match.db"

    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        test_db
    )

    # Create the ride listings table
    driver_listing_db.initialize_driver_listing_table()

    # Prepare a valid ride listing
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

    # Save listing to SQLite
    listing_id = driver_listing_db.save_ride_listing(listing)

    # Retrieve saved listing
    saved_listing = driver_listing_db.get_ride_listing(
        listing_id
    )

    # Verify saved information
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
