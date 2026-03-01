"""Collect PowerVS placement groups."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_placement_groups(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect placement groups across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("placement-groups")
        except Exception:
            continue

        items = data.get("placementGroups", [])
        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "policy": item.get("policy", ""),
                "memberCount": len(item.get("members", [])),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
