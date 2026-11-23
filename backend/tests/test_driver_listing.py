
from datetime import datetime, timedelta, timezone

import pytest

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

