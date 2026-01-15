import json
import logging
from typing import Any

from app.config import (
    LLM_PROVIDER,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_BASE_URL,
)

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ["link", "address", "size", "price", "beds", "baths", "notes"]

SYSTEM_PROMPT = (
    "You are a strict JSON generator. Return ONLY valid JSON with keys: "
    "link,address,size,price,beds,baths,notes. "
    "If a field is not present in the message, use an empty string. "
    "Do not guess or infer missing data."
)

def fallback_fields(raw_message: str, error: str) -> dict[str, str]:
    return {
        "link": "",
        "address": "",
        "size": "",
        "price": "",
        "beds": "",
        "baths": "",
        "notes": f"AI_PARSER_ERROR: {error}. RAW_MESSAGE: {raw_message}",
    }

def validate(raw_message: str, data: Any) -> dict[str, str]:
    if not isinstance(data, dict):
        return fallback_fields(raw_message, "Response is not JSON")
    for k in ["link","address","size","price","beds","baths","notes"]:
        data[k] = "" if k not in data or data[k] is None else str(data[k])
    return data

def call_llm(api_key: str, base_url: str, model: str, raw_message: str):
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)
    res = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw_message},
        ],
    )
    return validate(raw_message, json.loads(res.choices[0].message.content))

def parse_property_fields(raw_message: str) -> dict[str, str]:
    try:
        if LLM_PROVIDER == "openrouter":
            return call_llm(OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL, raw_message)

        return call_llm(OPENAI_API_KEY, None, OPENAI_MODEL, raw_message)
    except Exception as e:
        logger.exception("LLM failed")
        return fallback_fields(raw_message, str(e))
