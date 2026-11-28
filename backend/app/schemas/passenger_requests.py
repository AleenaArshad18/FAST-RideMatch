from app.schemas.driver_requests import DriverRequestResponse
from pydantic import BaseModel, Field


class PassengerRequestCreate(BaseModel):
    listing_id: int = Field(gt=0)


class PassengerRequestResponse(DriverRequestResponse):
    pass
