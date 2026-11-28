from datetime import datetime, timezone
import sqlite3

from fastapi import HTTPException

from app.database.driver_listing_db import get_ride_listing
from app.database.passenger_request_db import (
    get_pending_passenger_request,
    get_passenger_request,
    get_passenger_requests,
    save_passenger_request
)


def submit_passenger_request(
    listing_id: int,
    passenger_id: int
) -> dict:
    listing = get_ride_listing(listing_id)

    if listing is None:
        raise HTTPException(
            status_code=404,
            detail="Ride listing not found."
        )

    if listing["status"] != "active":
        raise HTTPException(
            status_code=409,
            detail="This ride is not active."
        )

    if listing["available_seats"] <= 0:
        raise HTTPException(
            status_code=409,
            detail="This ride has no available seats."
        )

    if listing["driver_id"] == passenger_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot request your own ride."
        )

    if get_pending_passenger_request(
        listing_id,
        passenger_id
    ) is not None:
        raise HTTPException(
            status_code=409,
            detail="A pending request already exists for this ride."
        )

    created_at = datetime.now(timezone.utc).isoformat()

    try:
        request_id = save_passenger_request(
            listing_id=listing_id,
            driver_id=listing["driver_id"],
            passenger_id=passenger_id,
            created_at=created_at
        )
    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail="A pending request already exists for this ride."
        ) from error

    return get_passenger_request(request_id)


def retrieve_passenger_requests(passenger_id: int) -> list[dict]:
    return get_passenger_requests(passenger_id)


def retrieve_passenger_request(
    passenger_id: int,
    request_id: int
) -> dict:
    request = get_passenger_request(request_id)

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Ride request not found."
        )

    if request["passenger_id"] != passenger_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another passenger's requests."
        )

    return request
