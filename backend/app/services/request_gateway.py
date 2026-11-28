
from typing import Protocol

from fastapi import HTTPException

from app.schemas.driver_requests import (
    DriverRequestResponse,
    DriverDecision
)


class RequestGateway(Protocol):

    def get_driver_requests(
        self,
        driver_id: int
    ) -> list[DriverRequestResponse]:
        ...

    def get_request(
        self,
        driver_id: int,
        request_id: int
    ) -> DriverRequestResponse | None:
        ...

    def process_decision(
        self,
        driver_id: int,
        request_id: int,
        decision: DriverDecision
    ) -> DriverRequestResponse:
        ...


def get_request_gateway() -> RequestGateway:
    """
    Integration point for S06.

    The authoritative request service will be
    connected when S06 is implemented.
    """

    raise HTTPException(
        status_code=503,
        detail="Request processing service is not configured."
    )
