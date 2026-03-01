"""Collect PowerVS cloud connections."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_cloud_connections(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect cloud connections across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("cloud-connections")
        except Exception:
            continue

        items = data.get("cloudConnections", [])
        for item in items:
            results.append({
                "cloudConnectionID": item.get("cloudConnectionID", ""),
                "name": item.get("name", ""),
                "speed": item.get("speed", 0),
                "globalRouting": item.get("globalRouting", False),
                "greEnabled": item.get("greEnabled", False),
                "transitEnabled": item.get("transitEnabled", False),
                "networkCount": len(item.get("networks", [])),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
