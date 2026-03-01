"""Collect VPC VPN Gateway Connections."""
import requests
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS, VPC_API_VERSION


def collect_vpn_gateway_connections(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPN gateway connections across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            gateways = client.list_resources(region, "vpn_gateways", "vpn_gateways")
        except Exception:
            continue

        for gw in gateways:
            gw_id = gw.get("id", "")
            gw_name = gw.get("name", "")

            try:
                connections = client.list_resources(
                    region,
                    f"vpn_gateways/{gw_id}/connections",
                    "connections",
                )
            except Exception:
                continue

            for item in connections:
                local_cidrs = ", ".join(item.get("local_cidrs", []))
                peer_cidrs = ", ".join(item.get("peer_cidrs", []))
                results.append({
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "status": item.get("status", ""),
                    "mode": item.get("mode", ""),
                    "vpnGatewayName": gw_name,
                    "peerAddress": item.get("peer_address", ""),
                    "localCidrs": local_cidrs,
                    "peerCidrs": peer_cidrs,
                    "region": region,
                    "created_at": item.get("created_at", ""),
                })
    return results
