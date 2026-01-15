import json
import logging
from typing import Any

from app.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ["link", "address", "size", "price", "beds", "baths", "notes"]

SYSTEM_PROMPT = (
    "You are a strict JSON generator. Return ONLY valid JSON with keys: "
    "link,address,size,price,beds,baths,notes. "
    "If a field is not present in the message, use an empty string. "
    "Do not guess or infer missing data. "
    "If multiple links are present, choose the best one as link and include the rest in notes."
)


def validate_parsed_fields(raw_message: str, data: Any) -> dict[str, str]:
    if not isinstance(data, dict):
        return fallback_fields(raw_message, "Parsed data is not a JSON object")

    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        return fallback_fields(raw_message, f"Missing keys: {', '.join(missing)}")

    normalized: dict[str, str] = {}
    for key in REQUIRED_KEYS:
        value = data.get(key, "")
        normalized[key] = "" if value is None else str(value)
    return normalized


def fallback_fields(raw_message: str, error: str) -> dict[str, str]:
    fields = {key: "" for key in REQUIRED_KEYS}
    fields["notes"] = f"AI_PARSER_ERROR: {error}. RAW_MESSAGE: {raw_message}"
    return fields


def parse_property_fields(raw_message: str) -> dict[str, str]:
    if not OPENAI_API_KEY:
        return fallback_fields(raw_message, "OPENAI_API_KEY is not configured")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Extract fields from the WhatsApp message:\n{raw_message}",
                },
            ],
        )
        content = response.choices[0].message.content or ""
        parsed = json.loads(content)
        return validate_parsed_fields(raw_message, parsed)
    except Exception as exc:  # noqa: BLE001
        logger.exception("AI parsing failed")
        return fallback_fields(raw_message, str(exc))
