"""Collect PowerVS volume groups."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_volume_groups(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect volume groups across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("volume-groups")
        except Exception:
            continue

        items = data.get("volumeGroups", [])
        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "consistencyGroupName": item.get("consistencyGroupName", ""),
                "volumeCount": len(item.get("volumeIDs", [])),
                "replicationEnabled": item.get("replicationEnabled", False),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
