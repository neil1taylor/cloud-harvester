"""Data formatting utilities."""


def safe_string(value) -> str:
    """Convert value to a safe string for XLSX."""
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        import json
        return json.dumps(value)
    return str(value)


def bool_to_yesno(value) -> str:
    """Convert boolean to Yes/No string."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, str):
        return value
    return "Yes" if value else "No"
