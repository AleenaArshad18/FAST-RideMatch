
from datetime import datetime, timezone

from app.schemas.ride_listing import RideListingCreate


def validate_driver_listing(
    listing: RideListingCreate,
    is_verified_student: bool
) -> None:
    """
    Validate driver eligibility and ride listing rules.

    Raises ValueError if the listing is not allowed.
    """

    if not is_verified_student:
        raise ValueError(
            "Only verified FAST students can offer rides."
        )

    if not listing.start_area.strip():
        raise ValueError("Starting area is required.")

    if not listing.destination_area.strip():
        raise ValueError("Destination area is required.")

    if not listing.vehicle_details.strip():
        raise ValueError("Vehicle details are required.")

    departure = listing.departure_time

    if departure.tzinfo is None:
        raise ValueError(
            "Departure time must include a timezone."
        )

    if departure <= datetime.now(timezone.utc):
        raise ValueError(
            "Departure time must be in the future."
        )
