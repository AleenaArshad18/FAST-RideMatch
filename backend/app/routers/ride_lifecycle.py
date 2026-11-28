
from fastapi import APIRouter, Depends, Path

from app.routers.driver_requests import (
    require_verified_driver
)

from app.schemas.ride_lifecycle import (
    RideLifecycleResponse,
    RideLifecycleHistoryResponse
)

from app.services.ride_lifecycle import (
    cancel_ride,
    complete_ride,
    retrieve_lifecycle_history
)


router = APIRouter(
    prefix="/ride-listings",
    tags=["Ride Lifecycle"]
)


@router.post(
    "/{listing_id}/cancel",
    response_model=RideLifecycleResponse
)
def cancel_ride_listing(
    listing_id: int = Path(gt=0),
    driver_id: int = Depends(require_verified_driver)
):
    return cancel_ride(
        listing_id=listing_id,
        driver_id=driver_id
    )


@router.post(
    "/{listing_id}/complete",
    response_model=RideLifecycleResponse
)
def complete_ride_listing(
    listing_id: int = Path(gt=0),
    driver_id: int = Depends(require_verified_driver)
):
    return complete_ride(
        listing_id=listing_id,
        driver_id=driver_id
    )


@router.get(
    "/{listing_id}/history",
    response_model=list[RideLifecycleHistoryResponse]
)
def retrieve_ride_history(
    listing_id: int = Path(gt=0),
    driver_id: int = Depends(require_verified_driver)
):
    return retrieve_lifecycle_history(
        listing_id=listing_id,
        driver_id=driver_id
    )
