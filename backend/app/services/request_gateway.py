
from typing import Protocol

from app.schemas.driver_requests import (
    DriverRequestResponse,
    DriverDecision
)
from app.database.passenger_request_db import (
    get_request_by_id,
    get_requests_for_driver,
    process_request_decision
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
    return DatabaseRequestGateway()


class DatabaseRequestGateway:

    def get_driver_requests(
        self,
        driver_id: int
    ) -> list[DriverRequestResponse]:
        return [
            DriverRequestResponse.model_validate(request)
            for request in get_requests_for_driver(driver_id)
        ]

    def get_request(
        self,
        driver_id: int,
        request_id: int
    ) -> DriverRequestResponse | None:
        request = get_request_by_id(request_id)

        if request is None:
            return None

        return DriverRequestResponse.model_validate(request)

    def process_decision(
        self,
        driver_id: int,
        request_id: int,
        decision: DriverDecision
    ) -> DriverRequestResponse:
        request = process_request_decision(
            driver_id=driver_id,
            request_id=request_id,
            decision=decision.value
        )
        return DriverRequestResponse.model_validate(request)
