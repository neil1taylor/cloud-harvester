"""Collect PowerVS networks."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_networks(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect networks across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("networks")
        except Exception:
            continue

        items = data.get("networks", [])
        for item in items:
            results.append({
                "networkID": item.get("networkID", ""),
                "name": item.get("name", ""),
                "type": item.get("type", ""),
                "vlanID": item.get("vlanID", 0),
                "cidr": item.get("cidr", ""),
                "gateway": item.get("gateway", ""),
                "mtu": item.get("mtu", 0),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
