
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus


class PaymentResponse(BaseModel):
    id: int = Field(gt=0)
    request_id: int = Field(gt=0)
    listing_id: int = Field(gt=0)
    driver_id: int = Field(gt=0)
    passenger_id: int = Field(gt=0)

    total_fare: float = Field(ge=0)
    accepted_passengers: int = Field(gt=0)
    amount: float = Field(ge=0)

    status: PaymentStatus

    created_at: datetime
    updated_at: datetime

    start_area: str
    destination_area: str
    departure_time: datetime
