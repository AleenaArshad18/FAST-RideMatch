
from pydantic import BaseModel, Field


class DriverReliabilityResponse(BaseModel):
    driver_id: int = Field(gt=0)

    completed_ride_count: int = Field(
        default=0,
        ge=0
    )

    average_rating: float | None = None
