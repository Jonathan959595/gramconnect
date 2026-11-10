from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

Category = Literal["Drainage", "Electricity", "Water", "Roads", "Streetlight", "Sanitation", "Other"]
Status = Literal["Submitted", "Under review", "Assigned", "In progress", "Resolved", "Reopened"]

class ResidentCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone_hint: str = Field(min_length=4, max_length=30)
    locality: str = Field(min_length=2, max_length=100)
    preferred_language: Literal["Telugu", "English"] = "Telugu"
    notification_channels: list[Literal["WhatsApp", "SMS", "Voice"]] = []
    consent_recorded: bool = False

class ComplaintCreate(BaseModel):
    resident_id: str | None = None
    description: str = Field(min_length=10, max_length=2000)
    locality: str = Field(min_length=2, max_length=100)
    landmark: str | None = Field(default=None, max_length=200)
    category: Category | None = None
    consent_recorded: bool = False

class ComplaintUpdate(BaseModel):
    status: Status | None = None
    department: str | None = Field(default=None, max_length=120)
    authority_reference: str | None = Field(default=None, max_length=120)
    note: str = Field(min_length=3, max_length=1000)

class OutageCreate(BaseModel):
    locality: str = Field(min_length=2, max_length=100)
    source: Literal["Official feed", "Field officer", "Resident reports"]
    details: str = Field(min_length=10, max_length=2000)
    restoration_estimate: str | None = Field(default=None, max_length=200)

class OutageUpdate(BaseModel):
    status: Literal["Draft", "Verified", "Sent", "Closed"]
    note: str = Field(min_length=3, max_length=1000)
