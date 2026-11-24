
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.schemas.ride_listing import RideListingCreate
from app.services.driver_listing import validate_driver_listing


# Helper function to create a valid ride listing
def make_valid_listing():
    return RideListingCreate(
        driver_id=1,
        start_area="Islamabad",
        destination_area="FAST University",
        departure_time=datetime.now(timezone.utc)
        + timedelta(hours=2),
        available_seats=3,
        vehicle_details="Toyota Corolla",
        fare=300
    )


# Test 1: Verified driver can create a listing
def test_verified_driver_can_create_listing():
    listing = make_valid_listing()

    validate_driver_listing(
        listing,
        is_verified_student=True
    )


# Test 2: Unverified driver cannot create a listing
def test_unverified_driver_is_rejected():
    listing = make_valid_listing()

    with pytest.raises(ValueError):
        validate_driver_listing(
            listing,
            is_verified_student=False
        )


# Test 3: Empty starting area is rejected
def test_empty_start_area_is_rejected():
    listing = make_valid_listing()
    listing.start_area = "   "

    with pytest.raises(ValueError):
        validate_driver_listing(
            listing,
            is_verified_student=True
        )


# Test 4: Past departure time is rejected
def test_past_departure_is_rejected():
    listing = make_valid_listing()
    listing.departure_time = (
        datetime.now(timezone.utc)
        - timedelta(hours=1)
    )

    with pytest.raises(ValueError):
        validate_driver_listing(
            listing,
            is_verified_student=True
        )

# Test 5: Empty destination is rejected
def test_empty_destination_is_rejected():
    listing = make_valid_listing()
    listing.destination_area = "   "

    with pytest.raises(ValueError, match="Destination area"):
        validate_driver_listing(
            listing,
            is_verified_student=True
        )


# Test 6: Identical locations are rejected
def test_same_locations_are_rejected():
    listing = make_valid_listing()
    listing.destination_area = " islamabad "

    with pytest.raises(ValueError, match="must be different"):
        validate_driver_listing(
            listing,
            is_verified_student=True
        )


# Test 7: Empty vehicle details are rejected
def test_empty_vehicle_details_are_rejected():
    listing = make_valid_listing()
    listing.vehicle_details = "   "

    with pytest.raises(ValueError, match="Vehicle details"):
        validate_driver_listing(
            listing,
            is_verified_student=True
        )


# Test 8: Departure without timezone is rejected
def test_missing_timezone_is_rejected():
    listing = make_valid_listing()
    listing.departure_time = (
        listing.departure_time.replace(tzinfo=None)
    )

    with pytest.raises(ValueError, match="timezone"):
        validate_driver_listing(
            listing,
            is_verified_student=True
        )


# Test 9: Zero available seats are rejected
def test_zero_seats_are_rejected():
    data = make_valid_listing().model_dump()
    data["available_seats"] = 0

    with pytest.raises(ValidationError):
        RideListingCreate(**data)


# Test 10: Negative available seats are rejected
def test_negative_seats_are_rejected():
    data = make_valid_listing().model_dump()
    data["available_seats"] = -2

    with pytest.raises(ValidationError):
        RideListingCreate(**data)


# Test 11: Negative fare is rejected
def test_negative_fare_is_rejected():
    data = make_valid_listing().model_dump()
    data["fare"] = -100

    with pytest.raises(ValidationError):
        RideListingCreate(**data)


# Test 12: Free rides are allowed
def test_zero_fare_is_allowed():
    data = make_valid_listing().model_dump()
    data["fare"] = 0

    listing = RideListingCreate(**data)

    validate_driver_listing(
        listing,
        is_verified_student=True
    )

    assert listing.fare == 0