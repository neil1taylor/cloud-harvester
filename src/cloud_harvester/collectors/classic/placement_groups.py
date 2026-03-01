"""Collect IBM Cloud Classic Placement Groups."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,name,createDate,rule[name],backendRouter[hostname],"
    "guests[id]]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(api_key=api_key)


def collect_placement_groups(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all placement groups."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        groups = account.getPlacementGroups(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for pg in groups:
        results.append({
            "id": pg.get("id"),
            "name": pg.get("name", ""),
            "createDate": pg.get("createDate", ""),
            "rule": pg.get("rule", {}).get("name", "") if pg.get("rule") else "",
            "backendRouter": pg.get("backendRouter", {}).get("hostname", "") if pg.get("backendRouter") else "",
            "guestCount": len(pg.get("guests", [])),
        })

    return results
