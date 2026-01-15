from app.ai_parser import fallback_fields, validate_parsed_fields


def test_validate_parsed_fields_success() -> None:
    raw = "test"
    data = {
        "link": "http://example.com",
        "address": "123 Main",
        "size": "1200 sqft",
        "price": "$2000",
        "beds": "2",
        "baths": "2",
        "notes": "Near park",
    }
    result = validate_parsed_fields(raw, data)
    assert result == data


def test_validate_parsed_fields_missing_keys() -> None:
    raw = "test"
    data = {"link": "http://example.com"}
    result = validate_parsed_fields(raw, data)
    assert result["link"] == ""
    assert "Missing keys" in result["notes"]
    assert raw in result["notes"]


def test_fallback_fields() -> None:
    raw = "message"
    result = fallback_fields(raw, "error")
    assert result["notes"].startswith("AI_PARSER_ERROR: error")
    assert raw in result["notes"]
