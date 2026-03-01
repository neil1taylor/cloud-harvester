"""Collect Transit Gateways and connections (global API)."""
from cloud_harvester.collectors.vpc.client import VpcClient


def collect_transit_gateways(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect transit gateways (global API, no region iteration)."""
    client = VpcClient(token)

    try:
        gateways = client.list_transit_gateways()
    except Exception:
        return []

    results = []
    for item in gateways:
        results.append({
            "id": item.get("id", ""),
            "name": item.get("name", ""),
            "status": item.get("status", ""),
            "location": item.get("location", ""),
            "routingScope": item.get("global", False) and "global" or "local",
            "resourceGroup": item.get("resource_group", {}).get("name", ""),
            "created_at": item.get("created_at", ""),
        })
    return results


def collect_transit_gateway_connections(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect transit gateway connections (global API)."""
    client = VpcClient(token)

    try:
        gateways = client.list_transit_gateways()
    except Exception:
        return []

    results = []
    for gw in gateways:
        gw_id = gw.get("id", "")
        gw_name = gw.get("name", "")
        try:
            connections = client.list_transit_gateway_connections(gw_id)
        except Exception:
            continue

        for item in connections:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "networkType": item.get("network_type", ""),
                "transitGatewayName": gw_name,
                "networkId": item.get("network_id", ""),
                "ownershipType": item.get("request_status", ""),
                "created_at": item.get("created_at", ""),
            })
    return results
