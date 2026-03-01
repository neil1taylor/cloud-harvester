"""Collect Direct Link Gateways and virtual connections (global API)."""
from cloud_harvester.collectors.vpc.client import VpcClient


def collect_direct_link_gateways(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect Direct Link gateways (global API, no region iteration)."""
    client = VpcClient(token)

    try:
        gateways = client.list_direct_link_gateways()
    except Exception:
        return []

    results = []
    for item in gateways:
        results.append({
            "id": item.get("id", ""),
            "name": item.get("name", ""),
            "type": item.get("type", ""),
            "speedMbps": item.get("speed_mbps", 0),
            "locationName": item.get("location_name", ""),
            "bgpStatus": item.get("bgp_status", ""),
            "operationalStatus": item.get("operational_status", ""),
            "global": item.get("global", False),
            "resourceGroup": item.get("resource_group", {}).get("name", ""),
            "created_at": item.get("created_at", ""),
        })
    return results


def collect_direct_link_virtual_connections(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect Direct Link virtual connections (global API)."""
    client = VpcClient(token)

    try:
        gateways = client.list_direct_link_gateways()
    except Exception:
        return []

    results = []
    for gw in gateways:
        gw_id = gw.get("id", "")
        gw_name = gw.get("name", "")
        try:
            connections = client.list_direct_link_virtual_connections(gw_id)
        except Exception:
            continue

        for item in connections:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "type": item.get("type", ""),
                "gatewayName": gw_name,
                "networkId": item.get("network_id", ""),
                "networkAccountId": item.get("network_account", {}).get("id", ""),
                "created_at": item.get("created_at", ""),
            })
    return results
