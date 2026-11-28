
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.driver_listing_db import (
    initialize_driver_listing_table
)

from app.routers.driver_listing import (
    router as driver_listing_router
)

from app.routers.safety import (
    router as safety_router
)

from app.routers.driver_reliability import (
    router as driver_reliability_router
)

from app.routers.driver_requests import (
    router as driver_requests_router
)

from app.routers.passenger_requests import (
    router as passenger_requests_router
)

from app.database.passenger_request_db import (
    initialize_passenger_request_table
)

from app.database.ride_lifecycle_db import (
    initialize_ride_lifecycle_table
)

from app.routers.ride_lifecycle import (
    router as ride_lifecycle_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create or migrate the database tables
    # when the backend starts.
    initialize_driver_listing_table()
    initialize_passenger_request_table()
    initialize_ride_lifecycle_table()
    yield


app = FastAPI(
    title="FAST RideMatch API",
    description="Backend API for FAST RideMatch",
    version="1.0.0",
    lifespan=lifespan
)


# Preserve the existing CORS configuration.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Register feature routers.
app.include_router(safety_router)
app.include_router(driver_listing_router)
app.include_router(driver_reliability_router)
app.include_router(driver_requests_router)
app.include_router(passenger_requests_router)
app.include_router(ride_lifecycle_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to FAST RideMatch API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
