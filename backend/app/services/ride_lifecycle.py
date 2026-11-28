
from app.database.ride_lifecycle_db import (
    update_ride_status,
    get_ride_lifecycle_history
)

from app.schemas.ride_lifecycle import (
    RideStatus,
    RideLifecycleResponse,
    RideLifecycleHistoryResponse
)


def cancel_ride(
    listing_id: int,
    driver_id: int
) -> RideLifecycleResponse:
    """
    Cancel an active ride belonging to the driver.
    """

    result = update_ride_status(
        listing_id=listing_id,
        driver_id=driver_id,
        new_status=RideStatus.CANCELLED.value
    )

    return RideLifecycleResponse.model_validate(result)


def complete_ride(
    listing_id: int,
    driver_id: int
) -> RideLifecycleResponse:
    """
    Mark an active ride as completed.
    """

    result = update_ride_status(
        listing_id=listing_id,
        driver_id=driver_id,
        new_status=RideStatus.COMPLETED.value
    )

    return RideLifecycleResponse.model_validate(result)


def retrieve_lifecycle_history(
    listing_id: int,
    driver_id: int
) -> list[RideLifecycleHistoryResponse]:
    """
    Retrieve the status transition history
    of a ride belonging to the driver.
    """

    history = get_ride_lifecycle_history(
        listing_id=listing_id,
        driver_id=driver_id
    )

    return [
        RideLifecycleHistoryResponse.model_validate(record)
        for record in history
    ]
