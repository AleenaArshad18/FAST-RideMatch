
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RideStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class RideLifecycleResponse(BaseModel):
    listing_id: int = Field(gt=0)
    driver_id: int = Field(gt=0)
    status: RideStatus


class RideLifecycleHistoryResponse(BaseModel):
    id: int = Field(gt=0)
    listing_id: int = Field(gt=0)
    driver_id: int = Field(gt=0)
    previous_status: RideStatus
    new_status: RideStatus
    changed_at: datetime
