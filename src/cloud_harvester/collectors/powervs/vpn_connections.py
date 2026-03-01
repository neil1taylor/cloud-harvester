"""Collect PowerVS VPN connections."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_vpn_connections(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPN connections across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("vpn/vpn-connections")
        except Exception:
            continue

        items = data.get("vpnConnections", [])
        for item in items:
            local_subnets = ", ".join(item.get("localSubnets", []))
            peer_subnets = ", ".join(item.get("peerSubnets", []))

            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "mode": item.get("mode", ""),
                "peerAddress": item.get("peerAddress", ""),
                "localSubnets": local_subnets,
                "peerSubnets": peer_subnets,
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
