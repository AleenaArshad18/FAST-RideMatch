
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.database import driver_listing_db
from app.schemas.ride_listing import RideListingCreate


def test_get_existing_ride_listing(tmp_path, monkeypatch):
    # Use an isolated test database
    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        tmp_path / "test_rides.db"
    )

    driver_listing_db.initialize_driver_listing_table()

    # Create a sample ride listing
    listing = RideListingCreate(
        driver_id=1,
        start_area="FAST Islamabad",
        destination_area="F-10",
        departure_time=(
            datetime.now(timezone.utc)
            + timedelta(hours=2)
        ),
        available_seats=3,
        vehicle_details="Honda Civic",
        fare=250
    )

    # Save the listing
    listing_id = driver_listing_db.save_ride_listing(listing)

    # Request the listing through FastAPI
    client = TestClient(app)
    response = client.get(
        f"/ride-listings/{listing_id}"
    )

    # Verify the API response
    assert response.status_code == 200

    data = response.json()

    assert data["id"] == listing_id
    assert data["driver_id"] == 1
    assert data["start_area"] == "FAST Islamabad"
    assert data["destination_area"] == "F-10"
    assert data["available_seats"] == 3
    assert data["fare"] == 250
