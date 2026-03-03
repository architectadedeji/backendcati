"""Pydantic schemas for contacts."""
from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import Optional
from app.enums import ContactStatus


class ContactBase(BaseModel):
    name: str
    phone: str
    serial_number: str
    cuid: Optional[str] = None
    ticket_number: Optional[str] = None
    status: ContactStatus = "round_1"
    location: Optional[str] = None
    notes: Optional[str] = None
    batch_number: Optional[str] = None
    batch_serial_number: Optional[str] = None
    date_received: Optional[str] = None
    ticket_number_nos: Optional[str] = None
    study_arm: Optional[str] = None
    method: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[ContactStatus] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    last_contact: Optional[datetime] = None


class ContactResponse(ContactBase):
    id: int
    last_contact: Optional[datetime] = None
    interview_count: int = 0
    created_at: datetime
    
    @computed_field
    @property
    def due_round(self) -> Optional[int]:
        """Extract round number from status."""
        if self.status == ContactStatus.ALL_ROUNDS_COMPLETED:
            return None
        if self.status in (ContactStatus.ROUND_1, ContactStatus.ROUND_2, ContactStatus.ROUND_3, ContactStatus.ROUND_4):
            try:
                return int(self.status.value.split("_")[1])
            except (IndexError, ValueError):
                return None
        return None
    
    model_config = {"from_attributes": True}
