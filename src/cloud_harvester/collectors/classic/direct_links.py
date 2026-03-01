"""Collect IBM Cloud Direct Link Gateways via REST API."""
import requests
from cloud_harvester.utils.formatting import bool_to_yesno, safe_string

DIRECT_LINK_BASE = "https://directlink.cloud.ibm.com/v1"
API_VERSION = "2024-06-01"


def collect_direct_links(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all direct link gateways."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{DIRECT_LINK_BASE}/gateways?version={API_VERSION}"

    all_items = []
    try:
        while url:
            resp = requests.get(url, headers=headers, timeout=60)
            if resp.status_code == 403:
                return []
            resp.raise_for_status()
            data = resp.json()
            all_items.extend(data.get("gateways", []))
            url = data.get("next", {}).get("href") if data.get("next") else None
    except Exception:
        return []

    results = []
    for dl in all_items:
        location = dl.get("location_name", "")
        if regions and location and not any(r in location for r in regions):
            continue

        rg = dl.get("resource_group", {})
        rg_name = rg.get("id", "") if isinstance(rg, dict) else str(rg) if rg else ""

        results.append({
            "id": dl.get("id", ""),
            "name": dl.get("name", ""),
            "type": dl.get("type", ""),
            "speedMbps": dl.get("speed_mbps", 0),
            "locationName": location,
            "bgpStatus": dl.get("bgp_status", ""),
            "operationalStatus": dl.get("operational_status", ""),
            "global": bool_to_yesno(dl.get("global", False)),
            "resourceGroup": rg_name,
            "created_at": dl.get("created_at", ""),
        })

    return results
