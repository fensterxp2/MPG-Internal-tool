from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class WhatsAppWebhookPayload(BaseModel):
    group: str
    message_id: str
    sender_name: str
    sender_phone: str
    timestamp: str
    text: str
    attachments: list = Field(default_factory=list)


class PropertyBase(BaseModel):
    link: str
    address: str
    size: str
    price: str
    beds: str
    baths: str
    notes: str


class PropertyResponse(PropertyBase):
    id: UUID
    created_at: datetime
    agent_name: str
    raw_message: str
    status: Literal["NEW", "REVIEWED"]
    assigned_client_id: UUID | None


class ClientCreate(BaseModel):
    name: str
    notes: str | None = ""


class ClientResponse(BaseModel):
    id: UUID
    name: str
    notes: str
    created_at: datetime


class AssignClientRequest(BaseModel):
    client_id: UUID
