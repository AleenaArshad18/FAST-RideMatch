
from fastapi import FastAPI

app = FastAPI(
    title="FAST RideMatch API",
    version="0.1.0"
)


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
