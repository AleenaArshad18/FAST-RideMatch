from pydantic import BaseModel


class SafetySection(BaseModel):
    title: str
    description: str
    tips: list[str]


class EmergencyContact(BaseModel):
    name: str
    number: str
    description: str