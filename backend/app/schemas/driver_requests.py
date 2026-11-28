
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RequestStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class DriverDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"


class DriverRequestResponse(BaseModel):
    id: int = Field(gt=0)
    listing_id: int = Field(gt=0)
    driver_id: int = Field(gt=0)
    passenger_id: int = Field(gt=0)
    status: RequestStatus
    created_at: datetime
