
from fastapi import APIRouter, Depends, HTTPException, Path

from app.routers.driver_listing import (
    require_verified_student,
    require_driver_identity
)

from app.schemas.driver_requests import (
    DriverRequestResponse,
    DriverDecision
)

from app.services.request_gateway import (
    RequestGateway,
    get_request_gateway
)

from app.services.driver_requests import (
    get_incoming_requests,
    get_request_details,
    submit_driver_decision
)


router = APIRouter(
    prefix="/driver/requests",
    tags=["Driver Requests"]
)


def require_verified_driver(
    is_verified_student: bool = Depends(require_verified_student),
    driver_id: int = Depends(require_driver_identity)
) -> int:

    if not is_verified_student:
        raise HTTPException(
            status_code=403,
            detail="Only verified FAST students can manage requests."
        )

    return driver_id


@router.get(
    "",
    response_model=list[DriverRequestResponse]
)
def retrieve_driver_requests(
    driver_id: int = Depends(require_verified_driver),
    gateway: RequestGateway = Depends(get_request_gateway)
):
    return get_incoming_requests(
        driver_id,
        gateway
    )


@router.get(
    "/{request_id}",
    response_model=DriverRequestResponse
)
def retrieve_request_details(
    request_id: int = Path(gt=0),
    driver_id: int = Depends(require_verified_driver),
    gateway: RequestGateway = Depends(get_request_gateway)
):
    return get_request_details(
        driver_id,
        request_id,
        gateway
    )


@router.post(
    "/{request_id}/accept",
    response_model=DriverRequestResponse
)
def accept_request(
    request_id: int = Path(gt=0),
    driver_id: int = Depends(require_verified_driver),
    gateway: RequestGateway = Depends(get_request_gateway)
):
    return submit_driver_decision(
        driver_id,
        request_id,
        DriverDecision.ACCEPT,
        gateway
    )


@router.post(
    "/{request_id}/reject",
    response_model=DriverRequestResponse
)
def reject_request(
    request_id: int = Path(gt=0),
    driver_id: int = Depends(require_verified_driver),
    gateway: RequestGateway = Depends(get_request_gateway)
):
    return submit_driver_decision(
        driver_id,
        request_id,
        DriverDecision.REJECT,
        gateway
    )
