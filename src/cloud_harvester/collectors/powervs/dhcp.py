"""Collect PowerVS DHCP servers."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_dhcp_servers(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect DHCP servers across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("services/dhcp")
        except Exception:
            continue

        # DHCP endpoint may return a list directly or a dict with dhcpServers key
        if isinstance(data, list):
            items = data
        else:
            items = data.get("dhcpServers", [])

        for item in items:
            network = item.get("network", {})
            results.append({
                "id": item.get("id", ""),
                "status": item.get("status", ""),
                "networkId": network.get("id", "") if network else "",
                "networkName": network.get("name", "") if network else "",
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
