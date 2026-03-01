"""Collect PowerVS snapshots."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_snapshots(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect snapshots across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("snapshots")
        except Exception:
            continue

        items = data.get("snapshots", [])
        for item in items:
            results.append({
                "snapshotID": item.get("snapshotID", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "percentComplete": item.get("percentComplete", 0),
                "pvmInstanceName": item.get("pvmInstanceID", ""),
                "volumeCount": len(item.get("volumeSnapshots", {})),
                "workspace": ws["name"],
                "zone": ws["zone"],
                "creationDate": item.get("creationDate", ""),
            })

    return results
