from fastapi import APIRouter

from app.schemas.safety import SafetySection, EmergencyContact
from app.services.safety import (
    get_safety_guidance,
    get_emergency_contacts
)

router = APIRouter(
    prefix="/api/safety",
    tags=["Safety Guidance"]
)


@router.get("/guidance", response_model=dict[str, SafetySection])
def safety_guidance():
    return get_safety_guidance()


@router.get("/emergency-contacts", response_model=list[EmergencyContact])
def emergency_contacts():
    return get_emergency_contacts()