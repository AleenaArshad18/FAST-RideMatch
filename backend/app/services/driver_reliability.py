
from app.database.driver_reliability_db import (
    get_completed_ride_count
)

from app.schemas.driver_reliability import (
    DriverReliabilityResponse
)


def get_driver_reliability(
    driver_id: int
) -> DriverReliabilityResponse:
    """
    Retrieve available reliability information
    for a driver.
    """

    if driver_id <= 0:
        raise ValueError(
            "Driver ID must be a positive integer."
        )

    completed_ride_count = get_completed_ride_count(
        driver_id
    )

    return DriverReliabilityResponse(
        driver_id=driver_id,
        completed_ride_count=completed_ride_count,
        average_rating=None
    )
