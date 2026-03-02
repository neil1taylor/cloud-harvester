"""Collect IBM Cloud Classic Dedicated Hosts."""
import SoftLayer

OBJECT_MASK = (
    "mask[id,name,createDate,datacenter[name],cpuCount,memoryCapacity,"
    "diskCapacity,guestCount,guests[id]]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_dedicated_hosts(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all dedicated hosts."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        hosts = account.getDedicatedHosts(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for host in hosts:
        dc = host.get("datacenter", {}).get("name", "")
        if regions and dc and not any(r in dc for r in regions):
            continue

        results.append({
            "id": host.get("id"),
            "name": host.get("name", ""),
            "createDate": host.get("createDate", ""),
            "datacenter": dc,
            "cpuCount": host.get("cpuCount", 0),
            "memoryCapacity": host.get("memoryCapacity", 0),
            "diskCapacity": host.get("diskCapacity", 0),
            "guestCount": host.get("guestCount", 0),
        })

    return results
