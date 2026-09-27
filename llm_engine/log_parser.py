import json

def parse_raw_log(raw_log: str) -> dict:
    """Parses raw log text or JSON strings into structured dictionaries for the LLM prompt."""
    try:
        if isinstance(raw_log, str):
            return json.loads(raw_log)
        return raw_log
    except json.JSONDecodeError:
        return {"raw_text": raw_log, "status": "unstructured"}