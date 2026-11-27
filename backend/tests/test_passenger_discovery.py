
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.database import driver_listing_db
from app.schemas.ride_listing import RideListingCreate


def setup_test_database(tmp_path, monkeypatch):
    monkeypatch.setattr(
        driver_listing_db,
        "DATABASE_PATH",
        tmp_path / "test_rides.db"
    )

    driver_listing_db.initialize_driver_listing_table()

    client = TestClient(app)

    return client


def create_sample_ride(
    start_area="FAST Islamabad",
    destination_area="F-10",
    hours_from_now=2,
    seats=3,
    fare=250
):
    return RideListingCreate(
        driver_id=1,
        start_area=start_area,
        destination_area=destination_area,
        departure_time=(
            datetime.now(timezone.utc)
            + timedelta(hours=hours_from_now)
        ),
        available_seats=seats,
        vehicle_details="Honda Civic",
        fare=fare
    )


def test_browse_all_future_available_rides(tmp_path, monkeypatch):
    client = setup_test_database(tmp_path, monkeypatch)

    first_ride = create_sample_ride()
    second_ride = create_sample_ride(
        start_area="G-11",
        destination_area="Blue Area",
        hours_from_now=4
    )

    driver_listing_db.save_ride_listing(first_ride)
    driver_listing_db.save_ride_listing(second_ride)

    response = client.get("/ride-listings")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_search_by_start_area(tmp_path, monkeypatch):
    client = setup_test_database(tmp_path, monkeypatch)

    driver_listing_db.save_ride_listing(
        create_sample_ride(start_area="FAST Islamabad")
    )

    driver_listing_db.save_ride_listing(
        create_sample_ride(start_area="G-11")
    )

    response = client.get(
        "/ride-listings?start_area=fast"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["start_area"] == "FAST Islamabad"


def test_search_by_destination(tmp_path, monkeypatch):
    client = setup_test_database(tmp_path, monkeypatch)

    driver_listing_db.save_ride_listing(
        create_sample_ride(destination_area="F-10")
    )

    driver_listing_db.save_ride_listing(
        create_sample_ride(destination_area="Blue Area")
    )

    response = client.get(
        "/ride-listings?destination_area=F-10"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["destination_area"] == "F-10"


def test_filter_by_fare_range(tmp_path, monkeypatch):
    client = setup_test_database(tmp_path, monkeypatch)

    driver_listing_db.save_ride_listing(
        create_sample_ride(fare=200)
    )

    driver_listing_db.save_ride_listing(
        create_sample_ride(fare=500)
    )

    response = client.get(
        "/ride-listings?min_fare=150&max_fare=300"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["fare"] == 200


def test_filter_by_minimum_seats(tmp_path, monkeypatch):
    client = setup_test_database(tmp_path, monkeypatch)

    driver_listing_db.save_ride_listing(
        create_sample_ride(seats=1)
    )

    driver_listing_db.save_ride_listing(
        create_sample_ride(seats=3)
    )

    response = client.get(
        "/ride-listings?min_seats=2"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["available_seats"] == 3


def test_filter_by_departure_date(tmp_path, monkeypatch):
    client = setup_test_database(tmp_path, monkeypatch)

    tomorrow = (
        datetime.now(timezone.utc) + timedelta(days=1)
    ).date()

    driver_listing_db.save_ride_listing(
        create_sample_ride(hours_from_now=2)
    )

    tomorrow_ride = create_sample_ride(hours_from_now=26)

    driver_listing_db.save_ride_listing(tomorrow_ride)

    response = client.get(
        f"/ride-listings?departure_date={tomorrow.isoformat()}"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_past_rides_are_excluded(tmp_path, monkeypatch):
    client = setup_test_database(tmp_path, monkeypatch)

    past_ride = create_sample_ride(hours_from_now=-2)

    driver_listing_db.save_ride_listing(past_ride)

    response = client.get("/ride-listings")

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_fully_occupied_rides_are_excluded():
    from app.services.passenger_discovery import search_and_filter_rides

    rides = [
        {
            "departure_time": (
                datetime.now(timezone.utc) + timedelta(hours=2)
            ).isoformat(),
            "available_seats": 0,
            "start_area": "FAST Islamabad",
            "destination_area": "F-10",
            "fare": 250
        }
    ]

    result = search_and_filter_rides(rides)

    assert len(result) == 0

def test_minimum_fare_cannot_exceed_maximum_fare(
    tmp_path,
    monkeypatch
):
    client = setup_test_database(tmp_path, monkeypatch)

    response = client.get(
        "/ride-listings?min_fare=500&max_fare=200"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Minimum fare cannot exceed maximum fare."
    )
