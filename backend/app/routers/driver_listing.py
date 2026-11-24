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

    Actual authentication will be connected
    when the team's authentication system is ready.
    """
    raise HTTPException(
        status_code=503,
        detail="Student verification is not configured."
    )


def require_driver_identity():
    """
    Integration point for the authenticated student's ID.

    Never obtain the trusted identity from the
    submitted ride listing.
    """
    raise HTTPException(
        status_code=503,
        detail="Driver identity verification is not configured."
    )


@router.post(
    "",
    response_model=RideListingResponse,
    status_code=201
)
def create_ride_listing(
    listing: RideListingCreate,
    is_verified_student: bool = Depends(require_verified_student),
    driver_id: int = Depends(require_driver_identity)
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

    if listing.driver_id != driver_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot create a ride for another driver."
        )

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
    is_verified_student: bool = Depends(require_verified_student),
    driver_id: int = Depends(require_driver_identity)
):
    if not is_verified_student:
        raise HTTPException(
            status_code=403,
            detail="Only verified FAST students can edit rides."
        )

    existing_listing = get_ride_listing(listing_id)

    if existing_listing is None:
        raise HTTPException(
            status_code=404,
            detail="Ride listing not found."
        )

    if existing_listing["driver_id"] != driver_id:
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own ride listings."
        )

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

    updated = update_ride_listing(
        listing_id,
        listing
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Ride listing not found."
        )

    return get_ride_listing(listing_id)