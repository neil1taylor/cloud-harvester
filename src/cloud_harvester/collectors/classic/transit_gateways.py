"""Collect IBM Cloud Transit Gateways via REST API."""
import requests
from cloud_harvester.utils.formatting import safe_string

TRANSIT_GW_BASE = "https://transit.cloud.ibm.com/v1"
API_VERSION = "2024-01-01"


def collect_transit_gateways(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all transit gateways."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{TRANSIT_GW_BASE}/transit_gateways?version={API_VERSION}&limit=100"

    all_items = []
    try:
        while url:
            resp = requests.get(url, headers=headers, timeout=60)
            if resp.status_code == 403:
                return []
            resp.raise_for_status()
            data = resp.json()
            all_items.extend(data.get("transit_gateways", []))
            url = data.get("next", {}).get("href") if data.get("next") else None
    except Exception:
        return []

    results = []
    for tg in all_items:
        location = tg.get("location", {})
        if isinstance(location, dict):
            location_str = location.get("name", "")
        else:
            location_str = str(location) if location else ""

        if regions and location_str and not any(r in location_str for r in regions):
            continue

        rg = tg.get("resource_group", {})
        rg_name = rg.get("id", "") if isinstance(rg, dict) else str(rg) if rg else ""

        results.append({
            "id": tg.get("id", ""),
            "name": tg.get("name", ""),
            "status": tg.get("status", ""),
            "location": location_str,
            "routingScope": tg.get("global", False) and "global" or "local",
            "resourceGroup": rg_name,
            "created_at": tg.get("created_at", ""),
        })

    return results
