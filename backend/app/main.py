
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.driver_listing import (
    router as driver_listing_router
)


app = FastAPI(
    title="FAST RideMatch API",
    version="0.1.0"
)


# Allow requests from the local Expo web frontend.
# These origins are for local development only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8083",
        "http://127.0.0.1:8083",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


app.include_router(driver_listing_router)


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
