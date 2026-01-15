# WhatsApp Property Intake MVP

This repo contains a minimal internal MVP for ingesting WhatsApp group messages via an external bridge. The bridge posts JSON payloads to the API, which stores raw messages, parses structured fields using OpenAI, and exposes a simple admin dashboard for review and client assignment.

## Stack
- FastAPI + Jinja templates
- PostgreSQL + SQLAlchemy 2.x
- Alembic migrations
- OpenAI API for parsing

## Setup

### 1) Configure environment
Copy `.env.example` and set values:

```bash
cp .env.example .env
```

### 2) Run locally with Docker Compose

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000` and the admin dashboard at `http://localhost:8000/admin`.

### 3) Apply migrations

```bash
docker compose run --rm api alembic upgrade head
```

## Webhook Example

```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "group": "Listings",
    "message_id": "msg-123",
    "sender_name": "Agent Smith",
    "sender_phone": "+15555555555",
    "timestamp": "2024-09-24T12:00:00Z",
    "text": "2BR condo, 1200 sqft, $2,500/mo. 123 Main St. https://example.com",
    "attachments": []
  }'
```

## Notes
- The WhatsApp bridge/gateway is external and out of scope for this MVP. It must POST JSON to `/webhook/whatsapp`.
- Attachments are ignored in MVP.
- The parser returns empty strings for missing fields and never guesses missing data.
