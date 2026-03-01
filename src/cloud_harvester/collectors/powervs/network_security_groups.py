"""Collect PowerVS network security groups."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_network_security_groups(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect network security groups across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get_v1("network-security-groups")
        except Exception:
            continue

        items = data.get("networkSecurityGroups", [])
        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "ruleCount": len(item.get("rules", [])),
                "memberCount": len(item.get("members", [])),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
