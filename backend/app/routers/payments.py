from fastapi import APIRouter, Depends, HTTPException, Path

from app.routers.passenger_requests import require_verified_passenger
from app.routers.driver_requests import require_verified_driver

from app.schemas.payments import (
    PaymentResponse,
    PaymentStatusUpdate
)

from app.database.payment_db import (
    get_passenger_payment,
    get_passenger_payment_history,
    update_payment_status
)


router = APIRouter(tags=["Payments"])


passenger_router = APIRouter(
    prefix="/passenger/payments",
    tags=["Passenger Payments"]
)

driver_router = APIRouter(
    prefix="/driver/payments",
    tags=["Driver Payments"]
)


@passenger_router.get(
    "",
    response_model=list[PaymentResponse]
)
def retrieve_payment_history(
    passenger_id: int = Depends(require_verified_passenger)
):
    return get_passenger_payment_history(passenger_id)


@passenger_router.get(
    "/{request_id}",
    response_model=PaymentResponse
)
def retrieve_payment_details(
    request_id: int = Path(gt=0),
    passenger_id: int = Depends(require_verified_passenger)
):
    payment = get_passenger_payment(request_id, passenger_id)

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment record not found."
        )

    return payment


@driver_router.patch(
    "/{request_id}/status",
    response_model=PaymentResponse
)
def change_payment_status(
    update: PaymentStatusUpdate,
    request_id: int = Path(gt=0),
    driver_id: int = Depends(require_verified_driver)
):
    payment = update_payment_status(
        request_id,
        driver_id,
        update.status.value
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment record not found for this driver's ride."
        )

    return payment


router.include_router(passenger_router)
router.include_router(driver_router)