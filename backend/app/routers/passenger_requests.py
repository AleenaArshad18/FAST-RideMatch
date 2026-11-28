from fastapi import APIRouter, Depends, HTTPException, Path

from app.routers.driver_listing import require_verified_student
from app.schemas.passenger_requests import (
    PassengerRequestCreate,
    PassengerRequestResponse
)
from app.services.passenger_requests import (
    retrieve_passenger_request,
    retrieve_passenger_requests,
    submit_passenger_request
)


router = APIRouter(
    prefix="/passenger/requests",
    tags=["Passenger Requests"]
)


def require_passenger_identity(
    is_verified_student: bool = Depends(require_verified_student)
):
    if not is_verified_student:
        raise HTTPException(
            status_code=403,
            detail="Only verified FAST students can request rides."
        )

    raise HTTPException(
        status_code=503,
        detail="Passenger identity verification is not configured."
    )


def require_verified_passenger(
    passenger_id: int = Depends(require_passenger_identity)
) -> int:
    return passenger_id


@router.post(
    "",
    response_model=PassengerRequestResponse,
    status_code=201
)
def create_passenger_request(
    request: PassengerRequestCreate,
    passenger_id: int = Depends(require_verified_passenger)
):
    return submit_passenger_request(
        listing_id=request.listing_id,
        passenger_id=passenger_id
    )


@router.get(
    "",
    response_model=list[PassengerRequestResponse]
)
def retrieve_passenger_request_history(
    passenger_id: int = Depends(require_verified_passenger)
):
    return retrieve_passenger_requests(passenger_id)


@router.get(
    "/{request_id}",
    response_model=PassengerRequestResponse
)
def retrieve_passenger_request_details(
    request_id: int = Path(gt=0),
    passenger_id: int = Depends(require_verified_passenger)
):
    return retrieve_passenger_request(
        passenger_id,
        request_id
    )
