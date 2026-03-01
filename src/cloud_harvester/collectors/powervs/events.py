"""Collect PowerVS events."""
from datetime import datetime, timedelta, timezone

from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_events(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect events across all PowerVS workspaces (last 30 days)."""
    workspaces = discover_workspaces(token, regions)
    results = []

    # Get events from the last 30 days
    from_time = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get(f"events?from_time={from_time}")
        except Exception:
            continue

        items = data.get("events", [])
        for item in items:
            results.append({
                "eventID": item.get("eventID", ""),
                "action": item.get("action", ""),
                "level": item.get("level", ""),
                "message": item.get("message", ""),
                "resource": item.get("resource", ""),
                "user": item.get("user", ""),
                "timestamp": item.get("timestamp", ""),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
