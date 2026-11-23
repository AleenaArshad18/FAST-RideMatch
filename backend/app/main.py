
from fastapi import FastAPI
from app.routers.driver_listing import router as driver_listing_router


app = FastAPI(
    title="FAST RideMatch API",
    version="0.1.0"
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
