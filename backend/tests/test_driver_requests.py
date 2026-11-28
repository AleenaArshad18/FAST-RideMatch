
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app

from app.routers.driver_listing import (
    require_verified_student,
    require_driver_identity
)

from app.schemas.driver_requests import (
    DriverRequestResponse,
    DriverDecision,
    RequestStatus
)

from app.services.request_gateway import (
    get_request_gateway
)


class MockRequestGateway:

    def __init__(self):
        self.requests = {
            1: DriverRequestResponse(
                id=1,
                listing_id=10,
                driver_id=1,
                passenger_id=2,
                status=RequestStatus.PENDING,
                created_at=datetime.now(timezone.utc)
            ),
            2: DriverRequestResponse(
                id=2,
                listing_id=20,
                driver_id=3,
                passenger_id=4,
                status=RequestStatus.PENDING,
                created_at=datetime.now(timezone.utc)
            ),
            3: DriverRequestResponse(
                id=3,
                listing_id=10,
                driver_id=1,
                passenger_id=5,
                status=RequestStatus.ACCEPTED,
                created_at=datetime.now(timezone.utc)
            )
        }

    def get_driver_requests(self, driver_id):
        return [
            request
            for request in self.requests.values()
            if request.driver_id == driver_id
        ]

    def get_request(self, driver_id, request_id):
        return self.requests.get(request_id)

    def process_decision(
        self,
        driver_id,
        request_id,
        decision
    ):
        request = self.requests.get(request_id)

        if request is None:
            raise HTTPException(status_code=404)

        if request.driver_id != driver_id:
            raise HTTPException(status_code=403)

        if request.status != RequestStatus.PENDING:
            raise HTTPException(status_code=409)

        if decision == DriverDecision.ACCEPT:
            status = RequestStatus.ACCEPTED
        else:
            status = RequestStatus.REJECTED

        updated_request = request.model_copy(
            update={"status": status}
        )

        self.requests[request_id] = updated_request

        return updated_request


@pytest.fixture
def client():
    gateway = MockRequestGateway()

    previous_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[require_verified_student] = (
        lambda: True
    )

    app.dependency_overrides[require_driver_identity] = (
        lambda: 1
    )

    app.dependency_overrides[get_request_gateway] = (
        lambda: gateway
    )

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


def test_retrieve_driver_requests(client):
    response = client.get("/driver/requests")

    assert response.status_code == 200
    assert len(response.json()) == 2

    assert all(
        request["driver_id"] == 1
        for request in response.json()
    )


def test_retrieve_request_history(client):
    response = client.get("/driver/requests")

    assert response.status_code == 200

    statuses = [
        request["status"]
        for request in response.json()
    ]

    assert "pending" in statuses
    assert "accepted" in statuses


def test_retrieve_request_details(client):
    response = client.get("/driver/requests/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["passenger_id"] == 2


def test_request_not_found(client):
    response = client.get("/driver/requests/999")

    assert response.status_code == 404


def test_access_another_drivers_request(client):
    response = client.get("/driver/requests/2")

    assert response.status_code == 403


def test_accept_pending_request(client):
    response = client.post(
        "/driver/requests/1/accept"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

    details = client.get("/driver/requests/1")

    assert details.json()["status"] == "accepted"


def test_reject_pending_request(client):
    response = client.post(
        "/driver/requests/1/reject"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

    details = client.get("/driver/requests/1")

    assert details.json()["status"] == "rejected"


def test_accept_already_processed_request(client):
    response = client.post(
        "/driver/requests/3/accept"
    )

    assert response.status_code == 409


def test_reject_already_processed_request(client):
    response = client.post(
        "/driver/requests/3/reject"
    )

    assert response.status_code == 409


def test_accept_another_drivers_request(client):
    response = client.post(
        "/driver/requests/2/accept"
    )

    assert response.status_code == 403


def test_reject_another_drivers_request(client):
    response = client.post(
        "/driver/requests/2/reject"
    )

    assert response.status_code == 403


def test_invalid_request_id(client):
    response = client.get("/driver/requests/0")

    assert response.status_code == 422


def test_unverified_student(client):
    app.dependency_overrides[require_verified_student] = (
        lambda: False
    )

    response = client.get("/driver/requests")

    assert response.status_code == 403


def test_authentication_not_configured(client):
    app.dependency_overrides.pop(
        require_verified_student
    )

    response = client.get("/driver/requests")

    assert response.status_code == 503


def test_request_gateway_not_configured(client):
    app.dependency_overrides.pop(
        get_request_gateway
    )

    response = client.get("/driver/requests")

    assert response.status_code == 503
