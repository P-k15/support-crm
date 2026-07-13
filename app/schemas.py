from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class TicketCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    subject: str
    description: str


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None  # a new note to append


class NoteOut(BaseModel):
    id: int
    note_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketListOut(BaseModel):
    ticket_id: str
    customer_name: str
    subject: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketDetailOut(BaseModel):
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    notes: List[NoteOut] = []

    class Config:
        from_attributes = True


class TicketCreateOut(BaseModel):
    ticket_id: str
    created_at: datetime


class TicketUpdateOut(BaseModel):
    success: bool
    updated_at: datetime
