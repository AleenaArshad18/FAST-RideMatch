
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.safety import router as safety_router
from app.routers.driver_listing import router as driver_listing_router


app = FastAPI(
    title="FAST RideMatch API",
    description="Backend API for FAST RideMatch",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(safety_router)
app.include_router(driver_listing_router)


@app.get("/")
def home():
    return {
        "message": "FAST RideMatch API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
