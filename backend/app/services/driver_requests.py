
from fastapi import HTTPException

from app.schemas.driver_requests import (
    DriverRequestResponse,
    DriverDecision,
    RequestStatus
)

from app.services.request_gateway import RequestGateway


def get_incoming_requests(
    driver_id: int,
    gateway: RequestGateway
) -> list[DriverRequestResponse]:
    """
    Retrieve incoming requests and request history
    belonging to the authenticated driver.
    """

    requests = gateway.get_driver_requests(driver_id)

    return [
        request for request in requests
        if request.driver_id == driver_id
    ]


def get_request_details(
    driver_id: int,
    request_id: int,
    gateway: RequestGateway
) -> DriverRequestResponse:
    """
    Retrieve an individual request belonging
    to the authenticated driver.
    """

    request = gateway.get_request(
        driver_id,
        request_id
    )

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Ride request not found."
        )

    if request.driver_id != driver_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another driver's requests."
        )

    return request


def submit_driver_decision(
    driver_id: int,
    request_id: int,
    decision: DriverDecision,
    gateway: RequestGateway
) -> DriverRequestResponse:
    """
    Validate and forward the driver's decision
    to the authoritative request processing service.
    """

    request = get_request_details(
        driver_id,
        request_id,
        gateway
    )

    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=409,
            detail="Only pending requests can be accepted or rejected."
        )

    return gateway.process_decision(
        driver_id,
        request_id,
        decision
    )
