
from fastapi import APIRouter, Depends, HTTPException

from app.database.driver_listing_db import (
    get_ride_listing,
    save_ride_listing,
    update_ride_listing
)

from app.schemas.ride_listing import (
    RideListingCreate,
    RideListingUpdate,
    RideListingResponse
)

from app.services.driver_listing import validate_driver_listing


router = APIRouter(
    prefix="/ride-listings",
    tags=["Ride Listings"]
)


def require_verified_student():
    """
    Authentication integration point.

    Replace this dependency with the trusted student
    verification provider when it is available.
    """
    raise HTTPException(
        status_code=503,
        detail="Student verification is not configured."
    )


@router.post(
    "",
    response_model=RideListingResponse,
    status_code=201
)
def create_ride_listing(
    listing: RideListingCreate,
    is_verified_student: bool = Depends(require_verified_student)
):
    try:
        validate_driver_listing(
            listing,
            is_verified_student=is_verified_student
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    listing_id = save_ride_listing(listing)

    return {
        **listing.model_dump(),
        "id": listing_id
    }


@router.get(
    "/{listing_id}",
    response_model=RideListingResponse
)
def retrieve_ride_listing(listing_id: int):
    listing = get_ride_listing(listing_id)

    if listing is None:
        raise HTTPException(
            status_code=404,
            detail="Ride listing not found."
        )

    return listing


@router.put(
    "/{listing_id}",
    response_model=RideListingResponse
)
def edit_ride_listing(
    listing_id: int,
    listing: RideListingUpdate,
    is_verified_student: bool = Depends(require_verified_student)
):
    existing_listing = get_ride_listing(listing_id)

    if existing_listing is None:
        raise HTTPException(
            status_code=404,
            detail="Ride listing not found."
        )

    # Driver ownership must be verified using the
    # authenticated student's identity.
    # Until that integration exists, editing is blocked.
    raise HTTPException(
        status_code=503,
        detail="Driver ownership verification is not configured."
    )
