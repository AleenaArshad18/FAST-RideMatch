
from datetime import datetime
from pydantic import BaseModel, Field


class RideListingCreate(BaseModel):
    driver_id: int
    start_area: str
    destination_area: str
    departure_time: datetime
    available_seats: int = Field(gt=0)
    vehicle_details: str
    fare: float = Field(ge=0)




class RideListingUpdate(BaseModel):
    start_area: str
    destination_area: str
    departure_time: datetime
    available_seats: int = Field(gt=0)
    vehicle_details: str
    fare: float = Field(ge=0)


class RideListingResponse(RideListingCreate):
    id: int
    available_seats: int = Field(ge=0)
