"""Collect PowerVS host groups."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_host_groups(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect host groups across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get_v1("host-groups")
        except Exception:
            continue

        items = data.get("hostGroups", [])
        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "hostCount": len(item.get("hosts", [])),
                "secondaryCount": len(item.get("secondaries", [])),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
