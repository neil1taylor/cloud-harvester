"""Collect IBM Cloud Classic Reserved Capacity Groups."""
import SoftLayer

OBJECT_MASK = (
    "mask[id,name,createDate,backendRouter[hostname],"
    "instances[id]]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_reserved_capacity(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all reserved capacity groups."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        groups = account.getReservedCapacityGroups(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for rc in groups:
        results.append({
            "id": rc.get("id"),
            "name": rc.get("name", ""),
            "createDate": rc.get("createDate", ""),
            "backendRouter": rc.get("backendRouter", {}).get("hostname", "") if rc.get("backendRouter") else "",
            "instanceCount": len(rc.get("instances", [])),
        })

    return results
