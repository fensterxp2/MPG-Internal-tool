import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.ai_parser import parse_property_fields
from app.db import get_session
from app.models import Client, Property, PropertyStatus
from app.schemas import (
    AssignClientRequest,
    ClientCreate,
    ClientResponse,
    PropertyResponse,
    WhatsAppWebhookPayload,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WhatsApp Property Intake")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

SessionDep = Annotated[Session, Depends(get_session)]


def serialize_property(property_record: Property) -> dict:
    return {
        "id": str(property_record.id),
        "created_at": property_record.created_at.isoformat() if property_record.created_at else "",
        "created_at_display": property_record.created_at.strftime("%Y-%m-%d %H:%M")
        if property_record.created_at
        else "",
        "agent_name": property_record.agent_name,
        "raw_message": property_record.raw_message,
        "status": property_record.status.value,
        "assigned_client_id": str(property_record.assigned_client_id)
        if property_record.assigned_client_id
        else None,
        "link": property_record.link,
        "address": property_record.address,
        "size": property_record.size,
        "price": property_record.price,
        "beds": property_record.beds,
        "baths": property_record.baths,
        "notes": property_record.notes,
    }


def serialize_client(client: Client) -> dict:
    return {
        "id": str(client.id),
        "name": client.name,
        "notes": client.notes,
        "created_at": client.created_at.isoformat() if client.created_at else "",
    }


@app.post("/webhook/whatsapp", response_model=PropertyResponse)
def webhook_whatsapp(payload: WhatsAppWebhookPayload, session: SessionDep) -> Property:
    property_record = Property(agent_name=payload.sender_name, raw_message=payload.text)
    session.add(property_record)
    session.flush()

    parsed_fields = parse_property_fields(payload.text)
    for key, value in parsed_fields.items():
        setattr(property_record, key, value)

    session.commit()
    session.refresh(property_record)
    return property_record


@app.get("/properties", response_model=list[PropertyResponse])
def list_properties(
    session: SessionDep,
    status: PropertyStatus | None = Query(default=None),
    limit: int = Query(default=200, le=500),
) -> list[Property]:
    stmt = select(Property)
    if status:
        stmt = stmt.where(Property.status == status)
    stmt = stmt.order_by(desc(Property.created_at)).limit(limit)
    return list(session.scalars(stmt))


@app.post("/properties/{property_id}/assign-client", response_model=PropertyResponse)
def assign_client(
    property_id: UUID, request: AssignClientRequest, session: SessionDep
) -> Property:
    property_record = session.get(Property, property_id)
    if not property_record:
        raise HTTPException(status_code=404, detail="Property not found")

    client = session.get(Client, request.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    property_record.assigned_client_id = request.client_id
    property_record.status = PropertyStatus.REVIEWED
    session.commit()
    session.refresh(property_record)
    return property_record


@app.post("/clients", response_model=ClientResponse)
def create_client(client: ClientCreate, session: SessionDep) -> Client:
    record = Client(name=client.name, notes=client.notes or "")
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@app.get("/clients", response_model=list[ClientResponse])
def list_clients(session: SessionDep) -> list[Client]:
    stmt = select(Client).order_by(desc(Client.created_at))
    return list(session.scalars(stmt))


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    session: SessionDep,
    status: PropertyStatus = PropertyStatus.NEW,
) -> HTMLResponse:
    properties = list(
        session.scalars(
            select(Property)
            .where(Property.status == status)
            .order_by(desc(Property.created_at))
            .limit(200)
        )
    )
    clients = list(session.scalars(select(Client).order_by(desc(Client.created_at))))
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "properties": [serialize_property(p) for p in properties],
            "clients": [serialize_client(c) for c in clients],
            "status": status.value,
        },
    )
